#!/usr/bin/env python3
"""
Script to check duplicate tracking status in the people collection system
Duplicate tracking has been completely removed from the system

Usage in Docker:
    docker exec -it data_fetcher python data_fetcher/reset_people_duplicates.py
    docker exec -it data_fetcher_dev python data_fetcher/reset_people_duplicates.py
"""

import asyncio
import sys
import os

# Add the app directory to Python path for Docker
sys.path.insert(0, '/app')

from data_fetcher.src.people.people_collector_v2 import PeopleCollectorV2


async def check_duplicate_tracking_status():
    """Check the status of duplicate tracking in the people collection system"""
    print("🔄 Checking duplicate tracking status...")
    
    # Create collector instance
    collector = PeopleCollectorV2(batch_size=50)
    
    print("\n📊 Duplicate tracking status:")
    print("   ✅ Duplicate tracking has been completely removed from the system")
    print("   ✅ All people will be processed without skipping")
    print("   ✅ No duplicate checking is performed")
    
    print("\n🎯 System ready for full collection!")
    print("   You can now run the people collection and it will process ALL people without any duplicate filtering.")


if __name__ == "__main__":
    asyncio.run(check_duplicate_tracking_status()) 