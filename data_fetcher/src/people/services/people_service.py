import hashlib
import uuid
from sqlalchemy.orm import Session
from shared.src.core.logging import get_main_fetcher_logger
from shared.src.tables.people.people_table import PeopleTable, PeopleRoleTable, PeopleCoursesTable
from data_fetcher.src.people.crawler.people_crawler import LSFPersonCrawler


class PeopleService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_main_fetcher_logger(__name__)
        self.crawler = LSFPersonCrawler()

    def collect_and_store_people(self):
        """Collect people data and store in database"""
        self.logger.info("⬆️  Collecting and storing people data...")
        
        try:
            # Use crawler to get people data
            people_data = self.crawler.crawl_all_functions()
            
            if not people_data:
                self.logger.warning("No people data collected from crawler")
                return
                
            self.logger.info(f"Processing {len(people_data)} people records...")
            
            # Clear existing data (optional - you might want to keep this or make it configurable)
            # self._clear_existing_data()
            
            # Process and store people data
            for person_data in people_data:
                try:
                    self._process_person(person_data)
                except Exception as e:
                    self.logger.error(f"Error processing person {person_data.get('name', 'Unknown')}: {str(e)}")
                    continue
            
            self.db.commit()
            self.logger.info("💾 Successfully added people data to database")
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error collecting and storing people data: {str(e)}")
            raise

    def _process_person(self, person_data: dict):
        """Process a single person record and store in database"""
        
        # Generate a unique ID for the person (using profile_url or name as basis)
        person_id = self._generate_person_id(person_data)
        
        # Extract basic info
        basic_info = person_data.get("basic_info", {})
        
        # Create person record
        person_table = PeopleTable(
            id=person_id,
            profile_url=person_data.get("profile_url"),
            name=person_data.get("name", ""),
            first_name=basic_info.get("first_name", ""),
            last_name=basic_info.get("last_name", ""),
            gender=basic_info.get("gender", ""),
            title=basic_info.get("title", ""),
            academic_degree=basic_info.get("academic_degree", ""),
            employment_status=basic_info.get("employment_status", ""),
            name_suffix=basic_info.get("name_suffix", ""),
            status=basic_info.get("status", ""),
            note=basic_info.get("note", ""),
            office_hours=basic_info.get("office_hours", ""),
            email=person_data.get("email", ""),
            address=person_data.get("address", ""),
            faculty=person_data.get("faculty", ""),
            hash=self._generate_hash(person_data)
        )
        
        # Use merge to handle updates vs inserts
        self.db.merge(person_table)
        
        # Process roles
        self._process_person_roles(person_id, person_data)
        
        # Process courses
        self._process_person_courses(person_id, person_data)

    def _process_person_roles(self, person_id: str, person_data: dict):
        """Process and store person roles"""
        
        # Clear existing roles for this person
        self.db.query(PeopleRoleTable).filter(PeopleRoleTable.person_id == person_id).delete()
        
        # Add LSF role from crawler (if present)
        role_info = person_data.get("role")
        if role_info:
            role_id = f"{person_id}_lsf_role"
            lsf_role = PeopleRoleTable(
                id=role_id,
                person_id=person_id,
                institution="LMU",
                role=role_info.get("name", ""),
                lsf_role_id=role_info.get("id"),
                lsf_role_name=role_info.get("name", "")
            )
            self.db.merge(lsf_role)
        
        # Add detailed roles from person details
        roles = person_data.get("roles", [])
        for i, role in enumerate(roles):
            role_id = f"{person_id}_role_{i}"
            role_table = PeopleRoleTable(
                id=role_id,
                person_id=person_id,
                institution=role.get("institution", ""),
                role=role.get("role", ""),
                institution_url=role.get("institution_url", "")
            )
            self.db.merge(role_table)

    def _process_person_courses(self, person_id: str, person_data: dict):
        """Process and store person courses"""
        
        # Clear existing courses for this person
        self.db.query(PeopleCoursesTable).filter(PeopleCoursesTable.person_id == person_id).delete()
        
        # Add courses
        courses = person_data.get("courses", [])
        for i, course in enumerate(courses):
            course_id = f"{person_id}_course_{i}"
            course_table = PeopleCoursesTable(
                id=course_id,
                person_id=person_id,
                course_number=course.get("number", ""),
                course_name=course.get("name", ""),
                semester=course.get("semester", ""),
                course_url=course.get("url", "")
            )
            self.db.merge(course_table)

    def _generate_person_id(self, person_data: dict) -> str:
        """Generate a unique ID for a person"""
        # Use profile URL if available, otherwise use name
        if person_data.get("profile_url"):
            # Extract a unique part from the URL
            url = person_data["profile_url"]
            # Use the last part of the URL as basis for ID
            if "personid=" in url:
                return url.split("personid=")[-1].split("&")[0]
            else:
                # Fallback to hash of URL
                return str(uuid.uuid5(uuid.NAMESPACE_URL, url))
        else:
            # Generate ID from name
            name = person_data.get("name", "unknown")
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, name))

    def _generate_hash(self, person_data: dict) -> str:
        """Generate a hash for change detection"""
        # Create a hash of the person data to detect changes
        content = str(sorted(person_data.items()))
        return hashlib.md5(content.encode()).hexdigest()

    def _clear_existing_data(self):
        """Clear all existing people data - use with caution!"""
        try:
            # Delete child tables first
            self.db.query(PeopleCoursesTable).delete()
            self.db.query(PeopleRoleTable).delete()
            # Then delete parent table
            self.db.query(PeopleTable).delete()
            
            self.db.commit()
            self.logger.info("Successfully cleared existing people data")
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error clearing existing data: {str(e)}")
            raise