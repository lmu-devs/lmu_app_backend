"""
Refactored People Collector using the new modular pipeline
Processes people data through separate, async pipeline stages
"""
import asyncio
from typing import Dict, List, Optional
from data_fetcher.src.core.base_collector import BaseCollector
from data_fetcher.src.people.crawler.people_crawler import LSFPersonCrawler
from data_fetcher.src.people.services.people_pipeline import PeoplePipeline


class PeopleCollectorV2(BaseCollector):
    """Refactored people collector with modular async pipeline"""

    def __init__(self, test_mode: bool = True, batch_size: int = 50):
        super().__init__()
        self.test_mode = test_mode
        self.batch_size = batch_size
        self.pipeline = PeoplePipeline(test_mode=test_mode, batch_size=batch_size)
        self.crawler = None

    async def _collect_data(self, db):
        """Main collection method using the new pipeline"""
        try:
            # Initialize crawler
            self.crawler = LSFPersonCrawler()
            
            if not self.crawler.functions:
                self.logger.error("No functions available from crawler!")
                return
            
            total_roles = len(self.crawler.functions)
            self.logger.info(f"📋 Starting collection for {total_roles} roles")
            
            # Process each role
            for i, (role_id, role_name) in enumerate(self.crawler.functions.items(), 1):
                try:
                    self.logger.info(f"🔄 [{i}/{total_roles}] Processing role {role_id}: '{role_name}'")
                    
                    # Crawl this specific role with character-by-character processing
                    await self._process_role_with_pipeline(role_id, role_name)
                    
                except Exception as e:
                    self.logger.error(f"❌ Failed to process role {role_id} '{role_name}': {e}")
                    continue
            
            # Final statistics
            final_stats = self.pipeline.get_pipeline_statistics()
            self._log_final_statistics(final_stats)
            
        except Exception as e:
            self.logger.error(f"❌ Critical error in collection process: {e}")
            raise

    async def _process_role_with_pipeline(self, role_id: int, role_name: str):
        """Process a single role through the pipeline with character-by-character processing"""
        try:
            # Get the character processing plan
            processing_plan = self._get_character_processing_plan(role_id)
            
            total_characters = len(processing_plan)
            self.logger.info(f"📊 Role {role_id} processing plan: {total_characters} character combinations")
            
            role_results = []
            
            for char_index, character in enumerate(processing_plan, 1):
                try:
                    self.logger.info(f"🔤 [{char_index}/{total_characters}] Processing character '{character}' for role {role_id}")
                    
                    # Crawl people for this character/role combination
                    raw_people = await self._crawl_character_async(role_id, character)
                    
                    if raw_people:
                        self.pipeline.update_raw_people_count(len(raw_people))
                        
                        # Process through pipeline
                        progress_callback = self._create_progress_callback(role_id, character)
                        result = await self.pipeline.process_character_batch(
                            raw_people, role_id, role_name, character, progress_callback
                        )
                        
                        role_results.append(result)
                        self.logger.info(f"✅ Character '{character}': {result['stored']}/{len(raw_people)} people stored")
                    else:
                        self.logger.info(f"– No people found for character '{character}'")
                        
                except Exception as e:
                    self.logger.error(f"❌ Failed to process character '{character}' for role {role_id}: {e}")
                    continue
            
            # Log role summary
            self._log_role_summary(role_id, role_name, role_results)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to process role {role_id} with pipeline: {e}")
            raise

    async def _crawl_character_async(self, role_id: int, character: str) -> List[Dict]:
        """Crawl people for a specific character/role combination asynchronously"""
        try:
            self.logger.info(f"🔄 Starting async crawl for character '{character}', role {role_id}")
            
            # Run the crawling in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            raw_people = await loop.run_in_executor(
                None, 
                self._crawl_character_sync, 
                role_id, 
                character
            )
            
            self.logger.info(f"🔄 Completed async crawl for character '{character}', role {role_id}: {len(raw_people)} people")
            return raw_people
            
        except Exception as e:
            self.logger.error(f"Failed to crawl character '{character}' for role {role_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def _crawl_character_sync(self, role_id: int, character: str) -> List[Dict]:
        """Synchronous character crawling (runs in thread pool)"""
        try:
            self.logger.info(f"🔍 Starting crawl for character '{character}', role {role_id}")
            
            # Use the existing crawler logic but for a specific character
            processed_people = set()
            out = []
            
            # Check if this character combination will have too many results
            if self.crawler._too_many(character, role_id):
                self.logger.warning(f"Character '{character}' has >1000 results for role {role_id}, skipping")
                return []
            
            # Limit for testing - only process first page for now
            max_people_per_character = 10  # Limit for testing
            people_found = 0
            
            # Process all pages for this character
            page = 0
            while people_found < max_people_per_character:
                self.logger.debug(f"🔍 Fetching page {page + 1} for character '{character}'")
                
                try:
                    doc = self.crawler._fetch_search(character, role_id, page)
                except Exception as e:
                    self.logger.error(f"Failed to fetch search page {page} for character '{character}': {e}")
                    break
                
                # Parse results
                entries = doc.xpath('//div[contains(@class, "erg_list_entry")]')
                if not entries:
                    self.logger.debug(f"No more entries found for character '{character}' on page {page}")
                    break
                
                self.logger.debug(f"Found {len(entries)} entries on page {page + 1}")
                
                # Process each person entry
                current_person = {}
                for entry in entries:
                    if people_found >= max_people_per_character:
                        break
                        
                    label = entry.xpath('.//div[@class="erg_list_label"]/text()')
                    if not label:
                        continue
                        
                    label = label[0].strip()
                    value = entry.xpath('.//text()')
                    value = ' '.join(v.strip() for v in value if v.strip())
                    
                    if label == "Name:":
                        # Save previous person if exists and is valid
                        if current_person:
                            if self._validate_person_data(current_person):
                                out.append(current_person)
                                people_found += 1
                            else:
                                self.logger.warning(f"🚫 Rejected invalid person: {current_person.get('name', 'NO_NAME')} - missing required data")
                            
                        # Start new person with name from search results
                        search_name = self.crawler._clean_text(value)
                        current_person = {"name": search_name}
                        self.logger.debug(f"🔍 Processing person: '{search_name}'")
                        
                        # Get profile URL
                        link = entry.xpath('.//a[@class="regular"]/@href')
                        if link:
                            href = link[0]
                            profile_url = f"https://lsf.verwaltung.uni-muenchen.de{href}" if href.startswith('/') else href
                            
                            # Skip if already processed
                            if profile_url in processed_people:
                                self.logger.debug(f"Skipping already processed person: {search_name}")
                                current_person = {}
                                continue
                            
                            current_person["profile_url"] = profile_url
                            processed_people.add(profile_url)
                            
                            # Fetch detailed person information
                            try:
                                self.logger.debug(f"🔍 Fetching details for: {search_name}")
                                detail_doc = self.crawler._fetch_person_details(href)
                                details = self.crawler._extract_person_details(detail_doc)
                                
                                # Log what we extracted
                                self.logger.debug(f"📊 Details extracted for {search_name}:")
                                self.logger.debug(f"   Faculty: '{details.get('faculty', 'NOT_FOUND')}'")
                                self.logger.debug(f"   Basic info fields: {list(details.get('basic_info', {}).keys())}")
                                self.logger.debug(f"   Non-empty basic info: {[k for k, v in details.get('basic_info', {}).items() if v]}")
                                
                                # Merge details but preserve the search name
                                original_name = current_person["name"]
                                current_person.update(details)
                                
                                # If detail extraction lost the name, restore it
                                if not current_person.get("name") or current_person["name"].strip() == "":
                                    current_person["name"] = original_name
                                    self.logger.debug(f"✅ Restored name from search results: '{original_name}'")
                                
                            except Exception as e:
                                self.logger.error(f"❌ Failed to fetch details for {search_name}: {e}")
                                # Add basic info structure as fallback
                                current_person["basic_info"] = {
                                    "first_name": "",
                                    "last_name": "",
                                    "gender": "",
                                    "title": "",
                                    "academic_degree": "",
                                    "employment_status": "",
                                    "name_suffix": "",
                                    "status": "",
                                    "note": "",
                                    "office_hours": ""
                                }
                                current_person["faculty"] = ""
                                current_person["academic_title"] = ""
                                current_person["roles"] = []
                                current_person["courses"] = []
                                
                    elif label == "Dienstadresse:":
                        current_person["address"] = self.crawler._clean_text(value)
                    elif label == "E-Mail:":
                        current_person["email"] = self.crawler._clean_text(value)
                    elif label == "Telefon:":
                        current_person["phone"] = self.crawler._clean_text(value)
                
                # Add last person if valid
                if current_person and people_found < max_people_per_character:
                    if self._validate_person_data(current_person):
                        out.append(current_person)
                        people_found += 1
                    else:
                        self.logger.warning(f"🚫 Rejected invalid last person: {current_person.get('name', 'NO_NAME')} - missing required data")
                
                # Break if we've reached our limit
                if people_found >= max_people_per_character:
                    self.logger.info(f"Reached limit of {max_people_per_character} people for character '{character}'")
                    break
                    
                page += 1
                
                # Safety break to avoid infinite loops
                if page > 10:
                    self.logger.warning(f"Breaking after 10 pages for character '{character}'")
                    break
            
            # Add role information to each person
            for person in out:
                dropdown_role = self.crawler._create_role_info(role_id, self.crawler.functions[role_id])
                existing_roles = person.get("roles", [])
                person["roles"] = [dropdown_role] + existing_roles
            
            self.logger.info(f"✅ Crawled {len(out)} valid people for character '{character}', role {role_id}")
            return out
            
        except Exception as e:
            self.logger.error(f"Sync crawling failed for character '{character}', role {role_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def _validate_person_data(self, person: Dict) -> bool:
        """Validate that person data meets minimum quality requirements"""
        # Must have a non-empty name
        name = person.get("name", "").strip() if person.get("name") else ""
        if not name:
            self.logger.debug(f"🚫 Validation failed: empty name")
            return False
        
        # Must have at least one piece of contact info or basic info
        has_contact = bool(person.get("email") or person.get("phone") or person.get("address"))
        
        basic_info = person.get("basic_info", {})
        has_basic_info = any(v and str(v).strip() for v in basic_info.values() if v is not None)
        
        faculty = person.get("faculty")
        has_faculty = bool(faculty and str(faculty).strip() if faculty is not None else False)
        
        if not (has_contact or has_basic_info or has_faculty):
            self.logger.debug(f"🚫 Validation failed for '{name}': no contact info, basic info, or faculty")
            return False
        
        self.logger.debug(f"✅ Validation passed for '{name}': has_contact={has_contact}, has_basic_info={has_basic_info}, has_faculty={has_faculty}")
        return True

    def _get_character_processing_plan(self, role_id: int) -> List[str]:
        """Get the list of characters/combinations to process for a role"""
        # For testing: only process first few letters
        plan = list("abc")  # Start with just first 3 letters for testing
        
        # TODO: Re-enable full alphabet once pipeline is working
        # plan = list("abcdefghijklmnopqrstuvwxyzäöüß")
        
        # For roles that typically have many people, also add common two-letter combinations
        high_volume_roles = [1, 2, 3]  # Adjust based on actual role IDs that have many people
        if role_id in high_volume_roles:
            # Add some common two-letter combinations (disabled for testing)
            pass
            # for first in ["a", "b", "c", "d", "m", "s"]:
            #     for second in ["a", "e", "i", "o", "u"]:
            #         plan.append(f"{first}{second}")
        
        return plan

    def _create_progress_callback(self, role_id: int, character: str):
        """Create a progress callback for pipeline updates"""
        async def progress_callback(stage: str, current: int, total: int):
            progress_percent = (current / total * 100) if total > 0 else 0
            self.logger.debug(f"📈 Role {role_id}, char '{character}', {stage}: {current}/{total} ({progress_percent:.1f}%)")
        
        return progress_callback

    def _log_role_summary(self, role_id: int, role_name: str, results: List[Dict]):
        """Log summary statistics for a completed role"""
        if not results:
            self.logger.info(f"📊 Role {role_id} ({role_name}): No results")
            return
        
        total_processed = sum(r.get("processed", 0) for r in results)
        total_stored = sum(r.get("stored", 0) for r in results)
        successful_batches = sum(1 for r in results if r.get("success", False))
        
        self.logger.info(f"📊 Role {role_id} ({role_name}) Summary:")
        self.logger.info(f"   ✅ Batches processed: {successful_batches}/{len(results)}")
        self.logger.info(f"   👥 People processed: {total_processed}")
        self.logger.info(f"   💾 People stored: {total_stored}")
        if total_processed > 0:
            success_rate = (total_stored / total_processed) * 100
            self.logger.info(f"   📈 Success rate: {success_rate:.1f}%")

    def _log_final_statistics(self, stats: Dict):
        """Log final collection statistics"""
        self.logger.info("🎯 FINAL COLLECTION STATISTICS:")
        self.logger.info(f"   📥 Raw people: {stats.get('total_raw_people', 0)}")
        self.logger.info(f"   🔄 Normalized: {stats.get('total_normalized', 0)}")
        self.logger.info(f"   🏷️  Enum mapped: {stats.get('total_enum_mapped', 0)}")
        self.logger.info(f"   📋 Model mapped: {stats.get('total_model_mapped', 0)}")
        self.logger.info(f"   💾 CMS stored: {stats.get('total_cms_stored', 0)}")
        self.logger.info(f"   ❌ Errors: {stats.get('processing_errors', 0)}")
        self.logger.info(f"   📦 Batches: {stats.get('batches_processed', 0)}")
        
        if stats.get('total_raw_people', 0) > 0:
            overall_success = (stats.get('total_cms_stored', 0) / stats.get('total_raw_people', 1)) * 100
            self.logger.info(f"   🎯 Overall success rate: {overall_success:.1f}%")


# Convenience function for running the new collector
async def run_people_collection_v2(test_mode: bool = True, batch_size: int = 50):
    """Run the new people collection pipeline"""
    collector = PeopleCollectorV2(test_mode=test_mode, batch_size=batch_size)
    await collector._collect_data(None)  # db parameter not used in this implementation 