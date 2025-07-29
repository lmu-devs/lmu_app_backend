"""
People Data Processing Pipeline
Orchestrates the complete pipeline from raw data to CMS storage
"""
import asyncio
from typing import Dict, List, Optional, Callable
from tqdm import tqdm
from shared.src.core.logging import get_main_fetcher_logger
from shared.src.services.people_service import PeopleService
from shared.src.models.people_model import Person

from .people_data_normalizer import PeopleDataNormalizer
from .people_enum_mapper import PeopleEnumMapper
from .people_model_mapper import PeopleModelMapper

logger = get_main_fetcher_logger(__name__)


class PeoplePipeline:
    """Main pipeline orchestrator for people data processing"""

    def __init__(self, batch_size: int = 50):
        self.logger = logger
        self.batch_size = batch_size
        self.logger.setLevel('WARNING')
        
        # Initialize services
        self.normalizer = PeopleDataNormalizer()
        self.enum_mapper = PeopleEnumMapper()
        self.model_mapper = PeopleModelMapper()
        self.cms_service = PeopleService()
        
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
        batch_start_time = asyncio.get_event_loop().time()
        
        try:
            if not raw_people:
                self.logger.warning(f"No people to process for role {role_id}")
                return self._create_batch_result(role_id, role_name, 0, 0)
            
            with tqdm(total=len(raw_people), desc=f"Char '{character}' {role_name}", leave=False) as pbar:
                if progress_callback:
                    await progress_callback("normalizing", 0, len(raw_people))
                normalized_people = self.normalizer.normalize_batch(raw_people)
                self.stats["total_normalized"] += len(normalized_people)
                pbar.update(len(normalized_people))
            
            if not normalized_people:
                self.logger.warning(f"No people normalized for role {role_id}")
                return self._create_batch_result(role_id, role_name, 0, 0)
            
            with tqdm(total=len(normalized_people), desc=f"Enum mapping {role_name}", leave=False) as pbar:
                if progress_callback:
                    await progress_callback("mapping_enums", len(normalized_people), len(raw_people))
                enum_mapped_people = self.enum_mapper.map_batch_enums(normalized_people)
                self.stats["total_enum_mapped"] += len(enum_mapped_people)
                pbar.update(len(enum_mapped_people))
            
            with tqdm(total=len(enum_mapped_people), desc=f"Model mapping {role_name}", leave=False) as pbar:
                if progress_callback:
                    await progress_callback("mapping_models", len(enum_mapped_people), len(raw_people))
                person_models = self.model_mapper.map_batch_to_models(enum_mapped_people)
                self.stats["total_model_mapped"] += len(person_models)
                pbar.update(len(person_models))
            
            if not person_models:
                self.logger.warning(f"No valid models created for role {role_id}")
                return self._create_batch_result(role_id, role_name, len(normalized_people), 0)
            
            with tqdm(total=len(person_models), desc=f"Storing to CMS {role_name}", leave=False) as pbar:
                if progress_callback:
                    await progress_callback("storing_cms", len(person_models), len(raw_people))
                stored_count = await self._store_people_async(person_models, enum_mapped_people)
                self.stats["total_cms_stored"] += stored_count
                self.stats["batches_processed"] += 1
                pbar.update(stored_count)
            
            batch_end_time = asyncio.get_event_loop().time()
            processing_time = batch_end_time - batch_start_time
            
            result = self._create_batch_result(
                role_id, role_name, len(person_models), stored_count, processing_time
            )
            result["character"] = character
            
            self.logger.info(f"✅ Completed batch for role {role_id}: {stored_count}/{len(raw_people)} stored successfully")
            
            if progress_callback:
                await progress_callback("completed", len(raw_people), len(raw_people))
            
            return result
            
        except Exception as e:
            self.stats["processing_errors"] += 1
            self.logger.error(f"❌ Failed to process batch for role {role_id}: {e}")
            return self._create_batch_result(role_id, role_name, 0, 0, error=str(e))

    async def _store_people_async(self, person_models: List[Person], enum_mapped_people: List[Dict]) -> int:
        """
        Store people in CMS asynchronously in smaller batches
        
        Args:
            person_models: List of Person models to store
            enum_mapped_people: List of enum-mapped people data (contains original enum objects)
            
        Returns:
            Number of people successfully stored
        """
        stored_count = 0
        
        sub_batch_size = min(self.batch_size // 2, 25)
        
        for i in range(0, len(person_models), sub_batch_size):
            sub_batch = person_models[i:i + sub_batch_size]
            
            try:
                people_dicts = []
                for person in sub_batch:
                    enum_data = next((data for data in enum_mapped_people if data.get("person_id") == person.person_id), None)
                    
                    person_dict = {
                        "profile_url": person.profile_url,
                        "name": person.name,
                        "person_id": person.person_id,
                        "email": person.email,
                        "phone": person.phone,
                        "address": person.address,
                        "faculty_enum": person.faculty_enum,
                        "academic_title_enum": person.academic_title_enum,
                        "primary_role": person.primary_role,
                        "basic_info": {
                            "first_name": person.first_name,
                            "last_name": person.surname,
                            "gender_enum": enum_data.get("basic_info", {}).get("gender_enum") if enum_data else None,
                            "title": person.title,
                            "academic_degree": person.academic_degree,
                            "employment_status_enum": enum_data.get("basic_info", {}).get("employment_status_enum") if enum_data else None,
                            "name_suffix": None,
                            "status": person.status,
                            "note": person.note,
                            "office_hours": person.office_hours,
                        },
                        "roles": [
                            {
                                "role_name": role.role_name,
                                "lsf_role_enum_obj": self._get_role_enum_from_mapped_data(enum_data, role.role_name) if enum_data else None,
                                "institutions": role.institutions if role.institutions else []
                            } for role in person.roles
                        ] if person.roles else [],
                        "courses": person.courses  # Courses as list of course numbers for person_details
                    }
                    people_dicts.append(person_dict)
                
                self.cms_service.collect_and_store_people(people_dicts)
                
                stored_count += len(sub_batch)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                for person in sub_batch:
                    self.logger.error(f"Failed to store person {getattr(person, 'name', 'UNKNOWN')} ({getattr(person, 'id', 'NO_ID')}): {e}")
                continue
        
        self.logger.warning(f"Batch summary: {stored_count}/{len(person_models)} people stored in CMS.")
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
        
        if stats["total_raw_people"] > 0:
            stats["normalization_success_rate"] = (stats["total_normalized"] / stats["total_raw_people"]) * 100
            stats["enum_mapping_success_rate"] = (stats["total_enum_mapped"] / stats["total_raw_people"]) * 100
            stats["model_mapping_success_rate"] = (stats["total_model_mapped"] / stats["total_raw_people"]) * 100
            stats["cms_storage_success_rate"] = (stats["total_cms_stored"] / stats["total_raw_people"]) * 100
        
        return stats

    def update_raw_people_count(self, count: int):
        """Update the count of raw people being processed"""
        self.stats["total_raw_people"] += count

    def _get_role_enum_from_mapped_data(self, enum_data: Dict, role_name: str):
        """Get role enum object from enum-mapped data by role name"""
        if not enum_data or not role_name:
            return None
        
        roles = enum_data.get("roles", [])
        for role in roles:
            if role.get("role_name") == role_name:
                return role.get("lsf_role_enum_obj")
        
        return None

