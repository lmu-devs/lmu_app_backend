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
        """
        Process a specific role through the async pipeline
        
        Args:
            role_id: LSF role ID
            role_name: LSF role name
        """
        try:
            # Get all characters to crawl for this role
            characters = self.crawler.get_character_list()
            total_characters = len(characters)
            
            self.logger.info(f"📝 Role {role_id} will crawl {total_characters} character combinations")
            
            role_stats = {
                "total_batches": 0,
                "total_people_processed": 0,
                "total_people_stored": 0,
                "successful_batches": 0,
                "failed_batches": 0,
                "processing_times": []
            }
            
            # Process each character combination
            for char_idx, character in enumerate(characters, 1):
                try:
                    self.logger.info(f"🔍 [{char_idx}/{total_characters}] Crawling character '{character}' for role {role_id}")
                    
                    # Crawl this character combination
                    raw_people = await self.crawler.crawl_people_by_role_and_character_async(role_id, character)
                    
                    if not raw_people:
                        self.logger.info(f"No people found for character '{character}' in role {role_id}")
                        continue
                    
                    self.logger.info(f"Found {len(raw_people)} people for character '{character}'")
                    self.pipeline.update_raw_people_count(len(raw_people))
                    
                    # Process through pipeline
                    batch_result = await self.pipeline.process_character_batch(
                        raw_people=raw_people,
                        role_id=role_id,
                        role_name=role_name,
                        character=character
                    )
                    
                    # Update role statistics
                    role_stats["total_batches"] += 1
                    role_stats["total_people_processed"] += batch_result.get("processed", 0)
                    role_stats["total_people_stored"] += batch_result.get("stored", 0)
                    
                    if batch_result.get("success", False):
                        role_stats["successful_batches"] += 1
                    else:
                        role_stats["failed_batches"] += 1
                    
                    if "processing_time_seconds" in batch_result:
                        role_stats["processing_times"].append(batch_result["processing_time_seconds"])
                    
                    self.logger.info(f"✅ Character '{character}': {batch_result.get('stored', 0)}/{batch_result.get('processed', 0)} stored")
                    
                except Exception as e:
                    role_stats["failed_batches"] += 1
                    self.logger.error(f"❌ Failed to process character '{character}' for role {role_id}: {e}")
                    continue
            
            # Log role summary
            self._log_role_summary(role_id, role_name, role_stats)
            
        except Exception as e:
            self.logger.error(f"Failed to process role {role_id}: {e}")
            raise

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