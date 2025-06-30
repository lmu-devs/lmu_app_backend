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
        """Collect people data and store in database role by role"""
        self.logger.info("⬆️  Collecting and storing people data role by role...")
        
        if not self.crawler.functions:
            self.logger.error("No functions available!")
            return
        
        total_roles = len(self.crawler.functions)
        total_people_processed = 0
        successful_roles = 0
        failed_roles = 0
        
        self.logger.info(f"📋 Found {total_roles} roles to process")
        
        for i, (pfid, role_name) in enumerate(self.crawler.functions.items(), 1):
            try:
                self.logger.info(f"🔄 [{i}/{total_roles}] Processing role {pfid}: '{role_name}'")
                
                # Crawl this specific role
                people = self.crawler.crawl_single_role(pfid)
                
                if not people:
                    self.logger.info(f"   – No entries for '{role_name}'")
                    continue
                
                self.logger.info(f"   📥 Found {len(people)} people, processing...")
                
                # Process and store people for this role
                role_processed = 0
                role_updated = 0
                role_created = 0
                
                for person_data in people:
                    try:
                        # Check if person exists before processing
                        person_id = self._generate_person_id(person_data)
                        existing_person = self.db.query(PeopleTable).filter(PeopleTable.id == person_id).first()
                        
                        if existing_person:
                            role_updated += 1
                        else:
                            role_created += 1
                            
                        self._upsert_person(person_data)
                        role_processed += 1
                    except Exception as e:
                        self.logger.error(f"Error processing person {person_data.get('name', 'Unknown')}: {str(e)}")
                        continue
                
                # Commit after each role
                self.db.commit()
                total_people_processed += role_processed
                successful_roles += 1
                
                self.logger.info(f"   ✅ Processed {role_processed} people from '{role_name}' (🆕 {role_created} new, 🔄 {role_updated} updated)")
                self.logger.info(f"   📊 Progress: {successful_roles}/{total_roles} roles, {total_people_processed} total people")
                
            except Exception as e:
                self.db.rollback()
                failed_roles += 1
                self.logger.error(f"   ❌ Failed to process role {pfid} '{role_name}': {str(e)}")
                self.logger.info(f"   🔄 Continuing with next role...")
                continue
        
        # Final summary
        self.logger.info("=" * 50)
        self.logger.info(f"🏁 Collection completed!")
        self.logger.info(f"   ✅ Successful roles: {successful_roles}/{total_roles}")
        self.logger.info(f"   ❌ Failed roles: {failed_roles}/{total_roles}")
        self.logger.info(f"   👥 Total people processed: {total_people_processed}")
        self.logger.info("=" * 50)

    def _upsert_person(self, person_data: dict):
        """Insert or update a person with smart duplicate handling"""
        
        # Generate a unique ID for the person
        person_id = self._generate_person_id(person_data)
        
        # Check if person already exists
        existing_person = self.db.query(PeopleTable).filter(PeopleTable.id == person_id).first()
        
        if existing_person:
            # Person exists - update with new data if it's more complete
            self._update_existing_person(existing_person, person_data)
        else:
            # Person doesn't exist - create new record
            self._create_new_person(person_id, person_data)
        
        # Always process roles and courses (they get merged)
        self._upsert_person_roles(person_id, person_data)
        self._upsert_person_courses(person_id, person_data)

    def _create_new_person(self, person_id: str, person_data: dict):
        """Create a new person record"""
        basic_info = person_data.get("basic_info", {})
        
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
        
        self.db.add(person_table)
        self.logger.debug(f"Created new person: {person_data.get('name', 'Unknown')}")

    def _update_existing_person(self, existing_person: PeopleTable, person_data: dict):
        """Update existing person with new data if it's more complete"""
        basic_info = person_data.get("basic_info", {})
        updated = False
        
        # Update fields if new data is more complete (not empty and different)
        updates = {
            'profile_url': person_data.get("profile_url"),
            'name': person_data.get("name", ""),
            'first_name': basic_info.get("first_name", ""),
            'last_name': basic_info.get("last_name", ""),
            'gender': basic_info.get("gender", ""),
            'title': basic_info.get("title", ""),
            'academic_degree': basic_info.get("academic_degree", ""),
            'employment_status': basic_info.get("employment_status", ""),
            'name_suffix': basic_info.get("name_suffix", ""),
            'status': basic_info.get("status", ""),
            'note': basic_info.get("note", ""),
            'office_hours': basic_info.get("office_hours", ""),
            'email': person_data.get("email", ""),
            'address': person_data.get("address", ""),
            'faculty': person_data.get("faculty", ""),
        }
        
        for field, new_value in updates.items():
            if new_value and new_value.strip():  # Only update if new value is not empty
                current_value = getattr(existing_person, field)
                if not current_value or current_value.strip() == "":
                    setattr(existing_person, field, new_value)
                    updated = True
                elif current_value != new_value:
                    # If both have values but they're different, prefer the more detailed one
                    if len(new_value) > len(current_value):
                        setattr(existing_person, field, new_value)
                        updated = True
        
        # Always update hash to reflect latest data
        existing_person.hash = self._generate_hash(person_data)
        
        if updated:
            self.logger.debug(f"Updated existing person: {person_data.get('name', 'Unknown')}")

    def _upsert_person_roles(self, person_id: str, person_data: dict):
        """Add roles for this person without duplicating existing ones"""
        
        # Add LSF role from crawler (if present and not already exists)
        role_info = person_data.get("role")
        if role_info:
            # Create unique role ID using LSF role ID
            role_id = f"{person_id}_lsf_role_{role_info.get('id')}"
            existing_role = self.db.query(PeopleRoleTable).filter(PeopleRoleTable.id == role_id).first()
            
            if not existing_role:
                lsf_role = PeopleRoleTable(
                    id=role_id,
                    person_id=person_id,
                    institution="LMU",
                    role=role_info.get("name", ""),
                    lsf_role_id=role_info.get("id"),
                    lsf_role_name=role_info.get("name", "")
                )
                self.db.add(lsf_role)
        
        # Add detailed roles from person details
        roles = person_data.get("roles", [])
        for role in roles:
            # Create a unique role ID based on content to avoid duplicates
            role_content = f"{role.get('institution', '')}_{role.get('role', '')}"
            role_hash = hashlib.md5(role_content.encode()).hexdigest()[:8]
            role_id = f"{person_id}_role_{role_hash}"
            
            existing_role = self.db.query(PeopleRoleTable).filter(PeopleRoleTable.id == role_id).first()
            
            if not existing_role:
                role_table = PeopleRoleTable(
                    id=role_id,
                    person_id=person_id,
                    institution=role.get("institution", ""),
                    role=role.get("role", ""),
                    institution_url=role.get("institution_url", "")
                )
                self.db.add(role_table)

    def _upsert_person_courses(self, person_id: str, person_data: dict):
        """Add courses for this person without duplicating existing ones"""
        
        courses = person_data.get("courses", [])
        for course in courses:
            # Create a unique course ID based on content to avoid duplicates
            course_content = f"{course.get('number', '')}_{course.get('name', '')}_{course.get('semester', '')}"
            course_hash = hashlib.md5(course_content.encode()).hexdigest()[:8]
            course_id = f"{person_id}_course_{course_hash}"
            
            existing_course = self.db.query(PeopleCoursesTable).filter(PeopleCoursesTable.id == course_id).first()
            
            if not existing_course:
                course_table = PeopleCoursesTable(
                    id=course_id,
                    person_id=person_id,
                    course_number=course.get("number", ""),
                    course_name=course.get("name", ""),
                    semester=course.get("semester", ""),
                    course_url=course.get("url", "")
                )
                self.db.add(course_table)

    def _generate_person_id(self, person_data: dict) -> str:
        """Generate a unique ID for a person using personal.pid from URL"""
        # Use profile URL if available
        if person_data.get("profile_url"):
            url = person_data["profile_url"]
            # Extract personal.pid from the URL (FIXED: was looking for "personid=")
            if "personal.pid=" in url:
                pid = url.split("personal.pid=")[-1].split("&")[0]
                return f"lmu_person_{pid}"
            else:
                # Fallback to hash of URL
                return str(uuid.uuid5(uuid.NAMESPACE_URL, url))
        else:
            # Generate ID from name and email combination for better uniqueness
            name = person_data.get("name", "unknown")
            email = person_data.get("email", "")
            # Use both name and email for better uniqueness
            unique_string = f"{name}_{email}" if email else name
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))

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