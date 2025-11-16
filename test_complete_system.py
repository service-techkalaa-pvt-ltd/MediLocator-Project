#!/usr/bin/env python
"""Comprehensive test of all three search modes"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.test import Client
import json

client = Client()

print("\n" + "="*80)
print("COMPREHENSIVE SEARCH TEST - ALL THREE MODES")
print("="*80)

# TEST 1: MODE 1 - BOTH (Location + Medicine)
print("\n" + "-"*80)
print("TEST 1: MODE 1 - BOTH (Location + Medicine Search)")
print("-"*80)
print("URL: /search-results/?lat=18.5204&lon=73.8567&radius=10&medicine=Amlong&mode=both")
print("Scenario: User searches for 'Amlong' near Pune within 10km radius")

response = client.get('/search-results/', {
    'lat': '18.5204',
    'lon': '73.8567',
    'radius': '10',
    'medicine': 'Amlong',
    'mode': 'both'
})

print(f"Response Status: {response.status_code}")
if response.status_code == 200:
    print("✓ Page loaded successfully")
    if 'resultsContainer' in response.content.decode():
        print("✓ Results container found in HTML")
    if 'pharmacy-card' in response.content.decode():
        print("✓ Pharmacy card template present")
else:
    print(f"✗ Error: {response.status_code}")

# TEST 2: MODE 2 - LOCATION ONLY
print("\n" + "-"*80)
print("TEST 2: MODE 2 - LOCATION ONLY")
print("-"*80)
print("URL: /search-results/?lat=18.5204&lon=73.8567&radius=10&mode=location")
print("Scenario: User searches for all pharmacies near Pune within 10km")

response = client.get('/search-results/', {
    'lat': '18.5204',
    'lon': '73.8567',
    'radius': '10',
    'mode': 'location'
})

print(f"Response Status: {response.status_code}")
if response.status_code == 200:
    print("✓ Page loaded successfully")
else:
    print(f"✗ Error: {response.status_code}")

# TEST 3: MODE 3 - MEDICINE ONLY
print("\n" + "-"*80)
print("TEST 3: MODE 3 - MEDICINE ONLY")
print("-"*80)
print("URL: /search-results/?medicine=Amlong&mode=medicine")
print("Scenario: User searches for all pharmacies nationwide with 'Amlong'")

response = client.get('/search-results/', {
    'medicine': 'Amlong',
    'mode': 'medicine'
})

print(f"Response Status: {response.status_code}")
if response.status_code == 200:
    print("✓ Page loaded successfully")
else:
    print(f"✗ Error: {response.status_code}")

# TEST 4: API ENDPOINT - /api/search-pharmacies/
print("\n" + "-"*80)
print("TEST 4: API ENDPOINT - /api/search-pharmacies/ (BOTH mode)")
print("-"*80)

response = client.get('/api/search-pharmacies/', {
    'lat': '18.5204',
    'lon': '73.8567',
    'radius': '10',
    'medicine': 'Amlong',
    'sort': 'distance'
})

data = json.loads(response.content)
print(f"Status: {response.status_code}")
print(f"Success: {data.get('success')}")
print(f"Total Pharmacies: {data.get('total', 0)}")
if data.get('pharmacies'):
    print(f"✓ Returned {len(data['pharmacies'])} pharmacies")
    pharmacy = data['pharmacies'][0]
    print(f"\nFirst result:")
    print(f"  Name: {pharmacy['name']}")
    print(f"  Distance: {pharmacy['distance']}km")
    print(f"  Rating: ⭐{pharmacy['rating']}")
    print(f"  Medicines: {len(pharmacy['available_medicines'])} items")
else:
    print("✗ No pharmacies returned")

# TEST 5: API ENDPOINT - /api/all-pharmacies/
print("\n" + "-"*80)
print("TEST 5: API ENDPOINT - /api/all-pharmacies/ (LOCATION mode)")
print("-"*80)

response = client.get('/api/all-pharmacies/', {
    'lat': '18.5204',
    'lon': '73.8567',
    'radius': '10',
    'sort': 'distance'
})

data = json.loads(response.content)
print(f"Status: {response.status_code}")
print(f"Success: {data.get('success')}")
print(f"Total Pharmacies: {data.get('total', 0)}")
if data.get('pharmacies'):
    print(f"✓ Returned {len(data['pharmacies'])} pharmacies")
else:
    print("✗ No pharmacies returned")

# TEST 6: API ENDPOINT - /api/search-medicines/
print("\n" + "-"*80)
print("TEST 6: API ENDPOINT - /api/search-medicines/ (MEDICINE mode)")
print("-"*80)

response = client.get('/api/search-medicines/', {
    'medicine': 'Amlong',
    'sort': 'distance'
})

data = json.loads(response.content)
print(f"Status: {response.status_code}")
print(f"Success: {data.get('success')}")
print(f"Total Pharmacies: {data.get('total', 0)}")
if data.get('pharmacies'):
    print(f"✓ Returned {len(data['pharmacies'])} pharmacies")
else:
    print("✗ No pharmacies returned")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80 + "\n")
