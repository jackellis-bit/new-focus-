#!/usr/bin/env python3
"""
Test Apify Integration
======================

Quick test to verify Apify is working with real LinkedIn data.
Run this with: python test_apify.py

Requires:
    export APIFY_TOKEN="apify_api_xxxxx"
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Force real Apify mode for this test
os.environ['USE_MOCK_DATA'] = 'false'

from scrapers.apify import ApifyClient


def test_single_company():
    """Test Apify with a single company search."""
    
    print("=" * 60)
    print("APIFY INTEGRATION TEST")
    print("=" * 60)
    
    # Check token
    token = os.getenv('APIFY_TOKEN')
    if not token:
        print("\n❌ ERROR: APIFY_TOKEN not set!")
        print("\nTo fix, run:")
        print('  export APIFY_TOKEN="apify_api_your_token_here"')
        print("\nGet your token at: https://console.apify.com/account#/integrations")
        return False
    
    print(f"\n✓ APIFY_TOKEN found: {token[:15]}...")
    print(f"✓ USE_MOCK_DATA: {os.getenv('USE_MOCK_DATA', 'true')}")
    
    # Initialize client
    client = ApifyClient()
    
    if not client.client:
        print("\n❌ ERROR: Apify client failed to initialize")
        return False
    
    print("\n✓ Apify client initialized")
    
    # Test with Netflix (a major target company)
    print("\n" + "-" * 60)
    print("TEST: Finding LinkedIn profiles at Netflix")
    print("-" * 60)
    
    test_roles = [
        "Editor",
        "Post Production Supervisor",
        "VFX Supervisor"
    ]
    
    print(f"\nSearching for: {', '.join(test_roles)}")
    print("Company: Netflix")
    print("Max results: 5")
    print("\nRunning Apify actor... (this may take 30-60 seconds)")
    
    try:
        employees = client.discover_company_employees(
            company_name="Netflix",
            company_linkedin_url="https://www.linkedin.com/company/netflix/",
            target_roles=test_roles,
            max_results=5
        )
        
        if not employees:
            print("\n⚠️  No employees returned. This could mean:")
            print("   - The actor needs different input parameters")
            print("   - Rate limiting or access restrictions")
            return False
        
        print(f"\n✓ SUCCESS! Found {len(employees)} profiles:\n")
        
        for i, emp in enumerate(employees, 1):
            print(f"  {i}. {emp.get('name', 'Unknown')}")
            print(f"     Title: {emp.get('title', 'N/A')}")
            print(f"     LinkedIn: {emp.get('linkedin_url', 'N/A')}")
            print(f"     Location: {emp.get('location', 'N/A')}")
            print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_profile_scraper():
    """Test scraping a specific LinkedIn profile."""
    print("\n" + "-" * 60)
    print("TEST: Scraping a specific LinkedIn profile")
    print("-" * 60)
    
    client = ApifyClient()
    
    # Test with a known public profile
    test_url = "https://www.linkedin.com/in/reed-hastings/"
    print(f"\nScraping: {test_url}")
    print("Running Apify actor... (this may take 30-60 seconds)")
    
    try:
        profile = client.scrape_profile(test_url)
        
        if profile:
            print(f"\n✓ SUCCESS! Profile data:")
            print(f"   Name: {profile.get('name', 'N/A')}")
            print(f"   Title: {profile.get('title', 'N/A')}")
            print(f"   Location: {profile.get('location', 'N/A')}")
            return True
        else:
            print("\n⚠️  No profile data returned")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


if __name__ == '__main__':
    print("\n")
    
    # Run the company search test
    success = test_single_company()
    
    if success:
        print("\n" + "=" * 60)
        print("✓ APIFY TEST PASSED - Ready to scrape real LinkedIn data!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Run full discovery: python main.py --discover --market tier1")
        print("  2. Or test with one company: python main.py --discover --market usa")
    else:
        print("\n" + "=" * 60)
        print("❌ APIFY TEST FAILED - Check configuration above")
        print("=" * 60)
    
    print("\n")
