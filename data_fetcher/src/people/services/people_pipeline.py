"""
People Data Processing Pipeline
Orchestrates the complete pipeline from raw data to CMS storage
"""
import asyncio
from typing import Dict, List, Optional, Callable
from shared.src.core.logging import get_main_fetcher_logger
from shared.src.services.people_cms_service import PeopleCMSService
from shared.src.models.people_model import Person

from .people_data_normalizer import PeopleDataNormalizer
from .people_enum_mapper import PeopleEnumMapper
from .people_model_mapper import PeopleModelMapper

logger = get_main_fetcher_logger(__name__)


class PeoplePipeline:
    """Main pipeline orchestrator for people data processing"""

    def __init__(self, test_mode: bool = True, batch_size: int = 50):
        self.logger = logger
        self.test_mode = test_mode
        self.batch_size = batch_size
        
        # Initialize services
        self.normalizer = PeopleDataNormalizer()
        self.enum_mapper = PeopleEnumMapper()
        self.model_mapper = PeopleModelMapper()
        self.cms_service = PeopleCMSService(test_mode=test_mode)
        
        # Pipeline statistics
        self.stats = {
            "total_raw_people": 0,
            "total_normalized": 0,
            "total_enum_mapped": 0,
            "total_model_mapped": 0,
            "total_cms_stored": 0,
            "processing_errors": 0,
            "batches_processed": 0
        }

    async def process_role_batch(
        self, 
        raw_people: List[Dict], 
        role_id: int, 
        role_name: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Process a batch of people from a specific role through the complete pipeline
        
        Args:
            raw_people: Raw people data from crawler
            role_id: LSF role ID
            role_name: LSF role name
            progress_callback: Optional callback for progress updates
            
        Returns:
            Processing results and statistics
        """
        batch_start_time = asyncio.get_event_loop().time()
        
        try:
            self.logger.info(f"🔄 Processing batch for role {role_id} ({role_name}): {len(raw_people)} people")
            
            # Step 1: Normalize raw data
            if progress_callback:
                await progress_callback("normalizing", 0, len(raw_people))
            
            normalized_people = self.normalizer.normalize_batch(raw_people)
            self.stats["total_normalized"] += len(normalized_people)
            
            if not normalized_people:
                self.logger.warning(f"No people normalized for role {role_id}")
                return self._create_batch_result(role_id, role_name, 0, 0)
            
            # Step 2: Map enums
            if progress_callback:
                await progress_callback("mapping_enums", len(normalized_people), len(raw_people))
            
            enum_mapped_people = self.enum_mapper.map_batch_enums(normalized_people)
            self.stats["total_enum_mapped"] += len(enum_mapped_people)
            
            # Step 3: Map to models
            if progress_callback:
                await progress_callback("mapping_models", len(enum_mapped_people), len(raw_people))
            
            person_models = self.model_mapper.map_batch_to_models(enum_mapped_people)
            self.stats["total_model_mapped"] += len(person_models)
            
            if not person_models:
                self.logger.warning(f"No valid models created for role {role_id}")
                return self._create_batch_result(role_id, role_name, len(normalized_people), 0)
            
            # Step 4: Store in CMS (async)
            if progress_callback:
                await progress_callback("storing_cms", len(person_models), len(raw_people))
            
            stored_count = await self._store_people_async(person_models)
            self.stats["total_cms_stored"] += stored_count
            self.stats["batches_processed"] += 1
            
            batch_end_time = asyncio.get_event_loop().time()
            processing_time = batch_end_time - batch_start_time
            
            result = self._create_batch_result(
                role_id, role_name, len(person_models), stored_count, processing_time
            )
            
            self.logger.info(f"✅ Completed batch for role {role_id}: {stored_count}/{len(raw_people)} stored successfully")
            
            if progress_callback:
                await progress_callback("completed", len(raw_people), len(raw_people))
            
            return result
            
        except Exception as e:
            self.stats["processing_errors"] += 1
            self.logger.error(f"❌ Failed to process batch for role {role_id}: {e}")
            return self._create_batch_result(role_id, role_name, 0, 0, error=str(e))

    async def process_character_batch(
        self,
        raw_people: List[Dict],
        role_id: int,
        role_name: str,
        character: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Process a batch of people from a specific character/role combination
        
        Args:
            raw_people: Raw people data from crawler
            role_id: LSF role ID
            role_name: LSF role name
            character: Character or character combination crawled
            progress_callback: Optional callback for progress updates
            
        Returns:
            Processing results and statistics
        """
        self.logger.info(f"🔄 Processing character '{character}' for role {role_id} ({role_name}): {len(raw_people)} people")
        
        result = await self.process_role_batch(raw_people, role_id, role_name, progress_callback)
        result["character"] = character
        
        return result

    async def _store_people_async(self, person_models: List[Person]) -> int:
        """
        Store people in CMS asynchronously in smaller batches
        
        Args:
            person_models: List of Person models to store
            
        Returns:
            Number of people successfully stored
        """
        stored_count = 0
        
        # Process in smaller sub-batches for better performance
        sub_batch_size = min(self.batch_size // 2, 25)
        
        for i in range(0, len(person_models), sub_batch_size):
            sub_batch = person_models[i:i + sub_batch_size]
            
            try:
                # Convert models to dicts for CMS service, preserving enum objects
                people_dicts = []
                for person in sub_batch:
                    person_dict = {
                        "id": person.id,
                        "profile_url": person.profile_url,
                        "name": person.name,
                        "email": person.email,
                        "address": person.address,
                        "faculty_enum": person.faculty_enum,  # Keep enum object
                        "academic_title_enum": person.academic_title_enum,  # Keep enum object
                        "basic_info": {
                            "first_name": person.basic_info.first_name if person.basic_info else "",
                            "last_name": person.basic_info.last_name if person.basic_info else "",
                            "gender_enum": person.basic_info.gender if person.basic_info else None,  # Keep enum object
                            "title": person.basic_info.title if person.basic_info else "",
                            "academic_degree": person.basic_info.academic_degree if person.basic_info else "",
                            "employment_status_enum": person.basic_info.employment_status if person.basic_info else None,  # Keep enum object
                            "name_suffix": person.basic_info.name_suffix if person.basic_info else "",
                            "status": person.status,
                            "note": person.note,
                            "office_hours": person.office_hours,
                        },
                        "roles": [
                            {
                                "lsf_role_enum_obj": role.lsf_role_enum,  # Keep enum object
                                "institutions": [
                                    {
                                        "name": inst.name,
                                        "url": inst.url,
                                        "id": inst.id,
                                        "data": inst.data
                                    } for inst in role.institutions
                                ] if role.institutions else []
                            } for role in person.roles
                        ] if person.roles else [],
                        "courses": [
                            {
                                "number": course.course_number,
                                "name": course.course_name,
                                "semester": course.semester,
                                "url": course.course_url
                            } for course in person.courses
                        ] if person.courses else []
                    }
                    people_dicts.append(person_dict)
                
                # Store in CMS
                self.cms_service.collect_and_store_people(people_dicts)
                
                stored_count += len(sub_batch)
                
                # Small delay to prevent overwhelming the CMS
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Failed to store sub-batch of {len(sub_batch)} people: {e}")
                continue
        
        return stored_count

    def _create_batch_result(
        self, 
        role_id: int, 
        role_name: str, 
        processed: int, 
        stored: int,
        processing_time: Optional[float] = None,
        error: Optional[str] = None
    ) -> Dict:
        """Create a standardized batch result dictionary"""
        result = {
            "role_id": role_id,
            "role_name": role_name,
            "processed": processed,
            "stored": stored,
            "success": stored > 0 and error is None,
            "error": error
        }
        
        if processing_time is not None:
            result["processing_time_seconds"] = round(processing_time, 2)
            result["people_per_second"] = round(processed / processing_time, 2) if processing_time > 0 else 0
        
        return result

    def get_pipeline_statistics(self) -> Dict:
        """Get comprehensive pipeline statistics"""
        stats = self.stats.copy()
        
        # Calculate success rates
        if stats["total_raw_people"] > 0:
            stats["normalization_success_rate"] = (stats["total_normalized"] / stats["total_raw_people"]) * 100
            stats["enum_mapping_success_rate"] = (stats["total_enum_mapped"] / stats["total_raw_people"]) * 100
            stats["model_mapping_success_rate"] = (stats["total_model_mapped"] / stats["total_raw_people"]) * 100
            stats["cms_storage_success_rate"] = (stats["total_cms_stored"] / stats["total_raw_people"]) * 100
        
        return stats

    def get_detailed_statistics(self, person_models: List[Person]) -> Dict:
        """Get detailed statistics about the processed data"""
        pipeline_stats = self.get_pipeline_statistics()
        model_stats = self.model_mapper.get_model_statistics(person_models)
        integrity_report = self.model_mapper.validate_models_integrity(person_models)
        
        return {
            "pipeline": pipeline_stats,
            "models": model_stats,
            "integrity": integrity_report,
            "summary": {
                "total_processed": len(person_models),
                "pipeline_efficiency": pipeline_stats.get("cms_storage_success_rate", 0),
                "data_quality": integrity_report.get("validity_percent", 0)
            }
        }

    def reset_statistics(self):
        """Reset pipeline statistics"""
        self.stats = {
            "total_raw_people": 0,
            "total_normalized": 0,
            "total_enum_mapped": 0,
            "total_model_mapped": 0,
            "total_cms_stored": 0,
            "processing_errors": 0,
            "batches_processed": 0
        }
        
        self.logger.info("Pipeline statistics reset")

    def update_raw_people_count(self, count: int):
        """Update the count of raw people being processed"""
        self.stats["total_raw_people"] += count 