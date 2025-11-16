#!/usr/bin/env python
"""Test script to diagnose API issues"""
import os
import django
import math

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from webapp.models import Pharmacy, Inventory, Medicine

print("\n" + "="*60)
print("DATABASE DIAGNOSTIC TEST")
print("="*60)

# Test 1: Check if pharmacies exist
pharm_count = Pharmacy.objects.count()
print(f"\n✓ Total Pharmacies in DB: {pharm_count}")

# Test 2: Check if medicines exist
med_count = Medicine.objects.count()
print(f"✓ Total Medicines in DB: {med_count}")

# Test 3: Check if inventory exists
inv_count = Inventory.objects.count()
print(f"✓ Total Inventory Links: {inv_count}")

# Test 4: Test search near Pune
print("\n" + "-"*60)
print("Testing search near Pune (18.5204, 73.8567):")
print("-"*60)

lat, lon, radius = 18.5204, 73.8567, 10
nearby = []

for p in Pharmacy.objects.all():
    dlat = math.radians(p.latitude - lat)
    dlon = math.radians(p.longitude - lon)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(p.latitude)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = 6371 * c
    if distance <= radius:
        nearby.append((p, distance))

nearby.sort(key=lambda x: x[1])
print(f"✓ Found {len(nearby)} pharmacies within {radius}km")

for i, (pharm, dist) in enumerate(nearby[:10], 1):
    # Check if has paracetamol
    has_para = Inventory.objects.filter(
        pharmacy=pharm,
        medicine__name__icontains='paracetamol',
        quantity__gt=0
    ).exists()
    para_str = "✓ HAS PARACETAMOL" if has_para else "✗ NO PARACETAMOL"
    print(f"{i}. {pharm.name} - {dist:.2f}km - ⭐{pharm.rating} - {para_str}")

# Test 5: Check medicines with paracetamol
print("\n" + "-"*60)
print("Medicines containing 'paracetamol':")
print("-"*60)

para_meds = Medicine.objects.filter(name__icontains='paracetamol')[:5]
print(f"✓ Found {para_meds.count()} medicines")
for med in para_meds:
    stock_count = Inventory.objects.filter(medicine=med, quantity__gt=0).count()
    print(f"  - {med.name} ({med.generic_name}) - Available in {stock_count} stores")

# Test 6: Check inventory for first pharmacy
print("\n" + "-"*60)
print("First pharmacy inventory sample:")
print("-"*60)

first_pharm = Pharmacy.objects.first()
if first_pharm:
    print(f"Pharmacy: {first_pharm.name}")
    items = Inventory.objects.filter(pharmacy=first_pharm, quantity__gt=0)[:5]
    print(f"Items in stock: {items.count()}")
    for item in items:
        print(f"  - {item.medicine.name}: {item.quantity} units @ {item.price}")

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60 + "\n")
