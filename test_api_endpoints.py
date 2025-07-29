#!/usr/bin/env python3
"""
Test script to debug API endpoints
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared', 'src'))

from shared.src.services.directus_service import DirectusService
from pathlib import Path

def test_graphql_connection():
    print("🧪 Testing GraphQL Connection\n" + "="*50)
    
    # Test basic connection
    directus = DirectusService()
    
    # Test a simple query first
    simple_query = """
    query TestConnection {
        people(limit: 1) {
            id
            name
        }
    }
    """
    
    try:
        print("Testing simple people query...")
        result = directus.query(simple_query)
        print(f"✅ Simple query successful: {result}")
        return True
    except Exception as e:
        print(f"❌ Simple query failed: {e}")
        return False

def test_get_all_people():
    print("\n🔍 Testing GetAllPeople query\n" + "="*50)
    
    directus = DirectusService()
    base_path = Path(__file__).parent
    query_path = base_path / "api" / "src" / "v1" / "people" / "graphql" / "new_people_queries.graphql"
    
    try:
        print("Testing GetAllPeople query...")
        result = directus.execute_query_file(
            query_file_path=query_path,
            variables={"limit": 1, "offset": 0},
            operation_name="GetAllPeople"
        )
        print(f"✅ GetAllPeople successful: {result}")
        return True
    except Exception as e:
        print(f"❌ GetAllPeople failed: {e}")
        return False

def test_get_person_by_id():
    print("\n🔍 Testing GetPersonById query\n" + "="*50)
    
    directus = DirectusService()
    base_path = Path(__file__).parent
    query_path = base_path / "api" / "src" / "v1" / "people" / "graphql" / "new_people_queries.graphql"
    
    try:
        print("Testing GetPersonById query...")
        result = directus.execute_query_file(
            query_file_path=query_path,
            variables={"id": "17355"},  # Test with the person ID you mentioned
            operation_name="GetPersonById"
        )
        print(f"✅ GetPersonById successful: {result}")
        return True
    except Exception as e:
        print(f"❌ GetPersonById failed: {e}")
        return False

def main():
    print("🚀 API Endpoints Test\n" + "="*50)
    
    # Test 1: Basic connection
    if not test_graphql_connection():
        print("❌ Basic connection failed, stopping tests")
        return
    
    # Test 2: GetAllPeople
    test_get_all_people()
    
    # Test 3: GetPersonById
    test_get_person_by_id()
    
    print("\n🏁 Test completed")

if __name__ == "__main__":
    main() 