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

    def __init__(self, batch_size: int = 50):
        super().__init__()
        self.batch_size = batch_size
        self.pipeline = PeoplePipeline(batch_size=batch_size)
        self.crawler = None
        self.logger.setLevel('WARNING')

    async def _collect_data(self, db):
        """Main collection method using the new pipeline"""
        try:
            # Initialize crawler
            self.crawler = LSFPersonCrawler()
            if hasattr(self.crawler, 'logger'):
                self.crawler.logger.setLevel('WARNING')
            
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
            
            # Print final statistics
            self._print_final_statistics()
            
        except Exception as e:
            self.logger.error(f"Fatal error in data collection: {e}")
            raise

    async def _process_role_with_pipeline(self, role_id: int, role_name: str):
        """Process a single role through the pipeline with character-by-character processing"""
        try:
            # For testing: only process first character for faster testing  
            processing_plan = list("a")  # Start with just 'a' for testing
            
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
                        result = await self.pipeline.process_character_batch(
                            raw_people, role_id, role_name, character
                        )
                        
                        role_results.append(result)
                        self.logger.info(f"✅ Character '{character}': {result['stored']}/{len(raw_people)} people stored")
                    else:
                        self.logger.info(f"– No people found for character '{character}'")
                        
                except Exception as e:
                    self.logger.error(f"❌ Failed to process character '{character}' for role {role_id}: {e}")
                    continue
            
            # Log role summary
            if role_results:
                total_processed = sum(r.get("processed", 0) for r in role_results)
                total_stored = sum(r.get("stored", 0) for r in role_results)
                self.logger.warning(f"Role {role_id} ({role_name}) summary: {total_stored}/{total_processed} people stored.")
            else:
                self.logger.warning(f"Role {role_id} ({role_name}): No results")
            
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
                            current_person["profile_url"] = profile_url
                            
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
                
                self.logger.debug(f"🔍 Role merge for {person.get('name', 'Unknown')}:")
                self.logger.debug(f"   Dropdown role: {dropdown_role.get('lsf_role_enum')} (institutions: {len(dropdown_role.get('institutions', []))})")
                self.logger.debug(f"   Existing roles: {[r.get('lsf_role_enum') for r in existing_roles]}")
                self.logger.debug(f"   Existing institution counts: {[len(r.get('institutions', [])) for r in existing_roles]}")
                
                # Don't overwrite existing roles with institutions - append dropdown role if not already present
                dropdown_role_name = dropdown_role.get("lsf_role_enum")
                existing_role_names = [role.get("lsf_role_enum") for role in existing_roles]
                
                if dropdown_role_name not in existing_role_names:
                    person["roles"] = existing_roles + [dropdown_role]
                    self.logger.debug(f"   ✅ Added dropdown role {dropdown_role_name}")
                else:
                    # Keep existing roles as they may have institution data
                    person["roles"] = existing_roles
                    self.logger.debug(f"   ✅ Kept existing roles with institutions")
            
            self.logger.info(f"✅ Crawled {len(out)} valid people for character '{character}', role {role_id}")
            return out
            
        except Exception as e:
            self.logger.error(f"Sync crawling failed for character '{character}', role {role_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def _validate_person_data(self, person: Dict) -> bool:
        """Validate that person data meets minimum quality requirements"""
        name = person.get("name", "").strip() if person.get("name") else ""
        if not name:
            self.logger.warning(f"Validation failed: empty name")
            return False
        has_contact = bool(person.get("email") or person.get("phone") or person.get("address"))
        basic_info = person.get("basic_info", {})
        has_basic_info = any(v and str(v).strip() for v in basic_info.values() if v is not None)
        faculty = person.get("faculty")
        has_faculty = bool(faculty and str(faculty).strip() if faculty is not None else False)
        if not (has_contact or has_basic_info or has_faculty):
            self.logger.warning(f"Validation failed for '{name}': no contact info, basic info, or faculty")
            return False
        return True

    def _log_role_summary(self, role_id: int, role_name: str, stats: Dict):
        """Log summary statistics for a completed role"""
        total_batches = stats["total_batches"]
        successful_batches = stats["successful_batches"]
        failed_batches = stats["failed_batches"]
        total_processed = stats["total_people_processed"]
        total_stored = stats["total_people_stored"]
        processing_times = stats["processing_times"]
        
        success_rate = (successful_batches / total_batches * 100) if total_batches > 0 else 0
        storage_rate = (total_stored / total_processed * 100) if total_processed > 0 else 0
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        self.logger.info(f"""
        📊 ROLE {role_id} '{role_name}' SUMMARY:
        ▫️ Batches: {successful_batches}/{total_batches} successful ({success_rate:.1f}%)
        ▫️ People: {total_stored}/{total_processed} stored ({storage_rate:.1f}%)
        ▫️ Avg processing time: {avg_processing_time:.2f}s per batch
        """)

    def _print_final_statistics(self):
        """Print comprehensive pipeline statistics"""
        stats = self.pipeline.get_pipeline_statistics()
        
        self.logger.info(f"""
        🏆 FINAL PIPELINE STATISTICS:
        ================================
        📥 Total raw people: {stats.get('total_raw_people', 0)}
        🧹 Normalized: {stats.get('total_normalized', 0)} ({stats.get('normalization_success_rate', 0):.1f}%)
        🏷️  Enum mapped: {stats.get('total_enum_mapped', 0)} ({stats.get('enum_mapping_success_rate', 0):.1f}%)
        📦 Model mapped: {stats.get('total_model_mapped', 0)} ({stats.get('model_mapping_success_rate', 0):.1f}%)
        💾 CMS stored: {stats.get('total_cms_stored', 0)} ({stats.get('cms_storage_success_rate', 0):.1f}%)
        ❌ Processing errors: {stats.get('processing_errors', 0)}
        📊 Batches processed: {stats.get('batches_processed', 0)}
        ================================
        """)

    async def crawl_and_process_people(self):
        """
        Main entry point for crawling and processing people data
        This method handles the complete pipeline from crawling to storage
        """
        try:
            self.logger.info("🚀 Starting People Collection Pipeline V2")
            
            # Start the collection process
            await self._collect_data(None)
            
            self.logger.info("🎉 People collection pipeline completed successfully!")
            
        except Exception as e:
            self.logger.error(f"💥 People collection pipeline failed: {e}")
            raise 