"""
Data Normalizer Service for People Pipeline
Cleans and normalizes raw crawled data before model mapping
"""
import re
import hashlib
from typing import Dict, List, Optional
from shared.src.core.logging import get_main_fetcher_logger

logger = get_main_fetcher_logger(__name__)


class PeopleDataNormalizer:
    """Normalizes raw crawled people data"""

    def __init__(self):
        self.logger = logger

    def normalize_person_data(self, raw_person: Dict) -> Dict:
        """
        Normalize a single person's raw data
        
        Args:
            raw_person: Raw person data from crawler
            
        Returns:
            Normalized person data ready for model mapping
        """
        try:
            self.logger.debug(f"Normalizing person: {raw_person.get('name', 'Unknown')}")
            self.logger.debug(f"  Raw faculty: '{raw_person.get('faculty', 'NOT_FOUND')}'")
            self.logger.debug(f"  Raw basic_info: {raw_person.get('basic_info', {})}")
            
            normalized = {
                "person_id": self._generate_person_id(raw_person),
                "name": self._clean_text(raw_person.get("name", "")),
                "profile_url": self._normalize_url(raw_person.get("profile_url")),
                "email": self._normalize_email(raw_person.get("email")),
                "phone": self._normalize_phone(raw_person.get("phone")),
                "address": self._clean_text(raw_person.get("address", "")),
                "faculty": self._clean_text(raw_person.get("faculty", "")),
                "basic_info": self._normalize_basic_info(raw_person.get("basic_info", {})),
                "roles": self._normalize_roles(raw_person.get("roles", [])),
                "courses": self._normalize_courses(raw_person.get("courses", [])),
            }
            
            normalized["academic_title"] = self._extract_academic_title(raw_person)
            
            return normalized
            
        except Exception as e:
            self.logger.error(f"Failed to normalize person data: {e}")
            self.logger.debug(f"Raw person data: {raw_person}")
            raise

    def normalize_batch(self, raw_people: List[Dict]) -> List[Dict]:
        """
        Normalize a batch of raw people data
        
        Args:
            raw_people: List of raw person data from crawler
            
        Returns:
            List of normalized person data
        """
        normalized_people = []
        failed_count = 0
        
        for i, raw_person in enumerate(raw_people):
            try:
                normalized = self.normalize_person_data(raw_person)
                normalized_people.append(normalized)
                
                if (i + 1) % 50 == 0:
                    self.logger.debug(f"Normalized {i + 1}/{len(raw_people)} people")
                    
            except Exception as e:
                failed_count += 1
                self.logger.warning(f"Failed to normalize person {raw_person.get('name', 'Unknown')}: {e}")
                continue
        
        self.logger.info(f"Normalized {len(normalized_people)}/{len(raw_people)} people successfully (failed: {failed_count})")
        return normalized_people

    def _generate_person_id(self, person_data: Dict) -> str:
        """Generate a unique ID for the person"""
        name = person_data.get("name", "")
        profile_url = person_data.get("profile_url", "")
        
        if profile_url:
            match = re.search(r'personal\.pid=(\d+)', profile_url)
            if match:
                return f"{match.group(1)}"
        
        content = f"{name}_{profile_url}"
        return f"{hashlib.md5(content.encode()).hexdigest()[:8]}"

    def _clean_text(self, text: str) -> str:
        """Clean up text by removing extra whitespace and common prefixes"""
        if not text:
            return ""
        
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'^(Name:|Funktion:|Dienstadresse:|E-Mail:|Dienstzimmer:)', '', text)
        return text.strip()

    def _normalize_url(self, url: Optional[str]) -> Optional[str]:
        """Normalize URL to full absolute URL"""
        if not url:
            return None
            
        url = url.strip()
        if url.startswith('/'):
            return f"https://lsf.verwaltung.uni-muenchen.de{url}"
        return url

    def _normalize_email(self, email: Optional[str]) -> Optional[str]:
        """Normalize email address"""
        if not email:
            return None
            
        email = self._clean_text(email)
        if '@' in email and '.' in email:
            return email.lower()
        return None

    def _normalize_phone(self, phone: Optional[str]) -> Optional[str]:
        """Normalize phone number"""
        if not phone:
            return None
            
        phone = self._clean_text(phone)
        phone = re.sub(r'[^\d\+\-\s\(\)]', '', phone)
        phone = phone.strip()
        
        if not phone or len(phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')) < 5:
            return None
            
        return phone

    def _normalize_basic_info(self, basic_info: Dict) -> Dict:
        """Normalize basic info fields"""
        normalized = {}
        
        field_mapping = {
            "first_name": "first_name",
            "last_name": "last_name", 
            "gender": "gender",
            "title": "title",
            "academic_degree": "academic_degree",
            "employment_status": "employment_status",
            "name_suffix": "name_suffix",
            "status": "status",
            "note": "note",
            "office_hours": "office_hours"
        }
        
        for raw_key, normalized_key in field_mapping.items():
            value = basic_info.get(raw_key, "")
            normalized[normalized_key] = self._clean_text(value) if value else ""
            
        return normalized

    def _normalize_roles(self, roles: List[Dict]) -> List[Dict]:
        """Normalize roles data"""
        normalized_roles = []
        
        for role in roles:
            if not isinstance(role, dict):
                continue
                
            lsf_role_enum = self._clean_text(role.get("lsf_role_enum", ""))
            
            normalized_role = {
                "role_name": lsf_role_enum,
                "lsf_role_enum": lsf_role_enum,
                "institutions": self._normalize_institutions(role.get("institutions", []))
            }
            
            if normalized_role["lsf_role_enum"] or normalized_role["institutions"]:
                normalized_roles.append(normalized_role)
        
        return normalized_roles

    def _normalize_institutions(self, institutions: List) -> List[Dict]:
        """Normalize institutions data"""
        if not institutions:
            return []
            
        normalized_institutions = []
        
        for inst in institutions:
            if isinstance(inst, str):
                normalized_institutions.append({
                    "name": self._clean_text(inst),
                    "url": None,
                    "id": None,
                    "data": None
                })
            elif isinstance(inst, dict):
                normalized_institutions.append({
                    "name": self._clean_text(inst.get("name", "")),
                    "url": self._normalize_url(inst.get("url")),
                    "id": inst.get("id"),
                    "data": inst.get("data")
                })
        
        return normalized_institutions

    def _normalize_courses(self, courses: List[Dict]) -> List[Dict]:
        """Normalize courses data"""
        normalized_courses = []
        
        for course in courses:
            if not isinstance(course, dict):
                continue
                
            normalized_course = {
                "number": self._clean_text(course.get("number", "")),
                "name": self._clean_text(course.get("name", "")),
                "semester": self._clean_text(course.get("semester", "")),
                "url": self._normalize_url(course.get("url"))
            }
            
            if any(normalized_course.values()):
                normalized_courses.append(normalized_course)
        
        return normalized_courses

    def _extract_academic_title(self, person_data: Dict) -> str:
        """Extract academic title from name or basic_info"""
        name = person_data.get("name", "")
        self.logger.debug(f"Extracting academic title from name: '{name}'")
        
        if name:
            title_patterns = [
                r'(Prof\.?\s*Dr\.?\s*[A-Za-z\.\s]*)',
                r'(Dr\.?\s*[A-Za-z\.\s]*)',
                r'(apl\.?\s*Prof\.?\s*Dr\.?)',
                r'(PD\s*Dr\.?)'
            ]
            
            for pattern in title_patterns:
                match = re.search(pattern, name, re.IGNORECASE)
                if match:
                    extracted_title = self._clean_text(match.group(1))
                    self.logger.debug(f"Extracted academic title: '{extracted_title}' using pattern: {pattern}")
                    return extracted_title
        
        basic_info = person_data.get("basic_info", {})
        academic_degree = basic_info.get("academic_degree", "")
        
        if academic_degree:
            self.logger.debug(f"Using academic_degree from basic_info: '{academic_degree}'")
        else:
            self.logger.debug("No academic title found in name or basic_info")
        
        return self._clean_text(academic_degree) if academic_degree else "" 