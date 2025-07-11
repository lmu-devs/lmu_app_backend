#!/usr/bin/env python3
"""
Test script for the PeopleService (CMS integration)
Now sends a complex payload with roles, enums, and courses.
"""
import sys
import os
import uuid
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared', 'src'))

from shared.src.services.people_service import PeopleService
from shared.src.enums import FacultyEnum, AcademicTitleEnum, LSFRoleEnum

TEST_PERSON_NAME = "Test User CMS Complex"


def main():
    print("🧪 PeopleService CMS Integration Test (Complex)\n" + "="*50)
    service = PeopleService(test_mode=False)

    # 1. Test connection by listing people
    print("\n🔍 Testing CMS connection and list...")
    try:
        people = service.get_all_people(limit=1)
        if hasattr(people, '__await__'):
            import asyncio
            people = asyncio.run(people)
        print(f"✅ CMS connection/list works. Found {people.total_count} people.")
    except Exception as e:
        print(f"❌ CMS connection/list failed: {e}")
        return

    # 2. Test create person (complex)
    print("\n🆕 Testing create person (complex payload)...")
    test_id = str(uuid.uuid4())
    person_data = {
        "id": test_id,
        "name": TEST_PERSON_NAME,
        "profile_url": "https://example.com/profile/testuser",
        "email": "testuser@example.com",
        "phone": "+49 123 4567890",
        "address": "Teststraße 1, 12345 München",
        "faculty_enum": FacultyEnum.MEDICINE.value,
        "academic_title_enum": AcademicTitleEnum.DR_MED.value,
        "primary_role": "Professor",
        "basic_info": {
            "first_name": "Test",
            "last_name": "User",
            "gender_enum": None,
            "title": "Dr.",
            "academic_degree": "PhD",
            "employment_status_enum": None,
            "name_suffix": None,
            "status": "active",
            "note": "Test note",
            "office_hours": "Mo 10-12"
        },
        "roles": [
            {
                "role_name": "Dozent",
                "lsf_role_enum_obj": LSFRoleEnum.EXTERNER_DOZENT.value,
                "institutions": [
                    {"name": "Test Institut", "url": "https://example.com/institut", "id": None, "data": None}
                ]
            }
        ],
        "courses": [
            {
                "number": "12345",
                "name": "Testkurs",
                "semester": "SoSe 2025",
                "url": "https://example.com/course"
            }
        ]
    }
    try:
        service.collect_and_store_people([person_data])
        print(f"✅ Complex person created with id {test_id}")
    except Exception as e:
        print(f"❌ Complex person creation failed: {e}")
        return

    # 3. Test read person
    print("\n🔎 Testing read person...")
    try:
        import asyncio
        person = asyncio.run(service.get_person_by_id(test_id))
        if person and person.name == TEST_PERSON_NAME:
            print(f"✅ Person read successful: {person.name}")
        else:
            print(f"❌ Person not found or data mismatch: {person}")
    except Exception as e:
        print(f"❌ Person read failed: {e}")

    print("\n🏁 Test completed\n")
    print("Stopping data_fetcher container...")
    os.system("docker-compose stop data_fetcher")

if __name__ == "__main__":
    main() 