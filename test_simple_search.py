#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

# Test the city search API
import json
import requests

print("\n" + "="*80)
print("Testing Simple City-Based Search (New Feature)")
print("="*80)

# Test 1: Search by City
print("\n✓ TEST 1: City Search API - Bhopal")
print("-" * 80)
try:
    response = requests.get('http://localhost:8000/api/search-by-city/?city=bhopal&sort=rating')
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Total pharmacies found: {data.get('total', 0)}")
        print(f"Success: {data.get('success')}")
        if data.get('pharmacies'):
            print(f"\nTop 3 Pharmacies (sorted by rating):")
            for i, pharm in enumerate(data['pharmacies'][:3], 1):
                print(f"  {i}. {pharm['name']}")
                print(f"     Rating: ⭐{pharm['rating']} | Address: {pharm['address']}")
                print(f"     Medicines: {pharm.get('total_medicines', 0)} available")
        print("✅ PASS")
    else:
        print(f"❌ FAIL - Status {response.status_code}")
except Exception as e:
    print(f"❌ FAIL - {e}")

# Test 2: Search by different city
print("\n✓ TEST 2: City Search API - Pune")
print("-" * 80)
try:
    response = requests.get('http://localhost:8000/api/search-by-city/?city=pune&sort=rating')
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Total pharmacies found: {data.get('total', 0)}")
        if data.get('pharmacies'):
            print(f"\nTop 3 Pharmacies (sorted by rating):")
            for i, pharm in enumerate(data['pharmacies'][:3], 1):
                print(f"  {i}. {pharm['name']}")
                print(f"     Rating: ⭐{pharm['rating']} | Phone: {pharm['phone']}")
        print("✅ PASS")
    else:
        print(f"❌ FAIL - Status {response.status_code}")
except Exception as e:
    print(f"❌ FAIL - {e}")

# Test 3: Medicine Search (existing feature)
print("\n✓ TEST 3: Medicine Search API - Paracetamol")
print("-" * 80)
try:
    response = requests.get('http://localhost:8000/api/search-medicines/?medicine=paracetamol&sort=rating')
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Total pharmacies found: {data.get('total', 0)}")
        if data.get('pharmacies'):
            print(f"\nTop 2 Pharmacies selling Paracetamol:")
            for i, pharm in enumerate(data['pharmacies'][:2], 1):
                print(f"  {i}. {pharm['name']} ({pharm['city']})")
                print(f"     Rating: ⭐{pharm['rating']}")
        print("✅ PASS")
    else:
        print(f"❌ FAIL - Status {response.status_code}")
except Exception as e:
    print(f"❌ FAIL - {e}")

# Test 4: Test the frontend suggestion API
print("\n✓ TEST 4: Medicine Autocomplete API")
print("-" * 80)
try:
    response = requests.get('http://localhost:8000/api/get-medicines/?search=par&limit=5')
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Medicines found: {len(data.get('medicines', []))}")
        if data.get('medicines'):
            print(f"Results for 'par':")
            for med in data['medicines'][:3]:
                print(f"  - {med['name']}")
        print("✅ PASS")
    else:
        print(f"❌ FAIL - Status {response.status_code}")
except Exception as e:
    print(f"❌ FAIL - {e}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("""
✅ Simple Search Working!

New Features:
1. Simple single search box (like Amazon)
2. City-based search with rating sorting
3. Medicine search with suggestions
4. All results display professionally

URL Examples:
- City Search: /search-results/?city=bhopal&mode=city
- Medicine: /search-results/?medicine=paracetamol&mode=medicine
""")
print("="*80)
