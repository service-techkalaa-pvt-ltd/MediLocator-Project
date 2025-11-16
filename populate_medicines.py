#!/usr/bin/env python
"""Populate pharmacies with random medicines"""
import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from webapp.models import Pharmacy, Medicine, Inventory

print("\n" + "="*70)
print("POPULATING PHARMACIES WITH MEDICINES")
print("="*70)

# Get all pharmacies and medicines
pharmacies = Pharmacy.objects.all()
medicines = list(Medicine.objects.all())

print(f"\nFound: {pharmacies.count()} pharmacies, {len(medicines)} medicines")

# For each pharmacy, add 20-40 random medicines
total_added = 0
for pharmacy in pharmacies:
    # Randomly select 20-40 medicines for this pharmacy
    num_medicines = random.randint(20, 40)
    selected_medicines = random.sample(medicines, min(num_medicines, len(medicines)))
    
    for medicine in selected_medicines:
        # Check if already exists
        if not Inventory.objects.filter(pharmacy=pharmacy, medicine=medicine).exists():
            qty = random.randint(5, 100)
            price = random.uniform(50, 500)
            
            Inventory.objects.create(
                pharmacy=pharmacy,
                medicine=medicine,
                quantity=qty,
                price=round(price, 2)
            )
            total_added += 1

print(f"\n✓ Added {total_added} inventory items!")

# Verify
print("\n" + "-"*70)
print("VERIFICATION:")
print("-"*70)

inv_count = Inventory.objects.count()
print(f"✓ Total Inventory items: {inv_count}")

# Test search for Paracetamol again
para_inv = Inventory.objects.filter(medicine__name__icontains='paracetamol', quantity__gt=0)
print(f"✓ Paracetamol in stock at: {para_inv.count()} pharmacies")

# Test a pharmacy near Pune
import math
lat, lon, radius = 18.5204, 73.8567, 10
nearby = []
for p in Pharmacy.objects.all():
    dlat = math.radians(p.latitude - lat)
    dlon = math.radians(p.longitude - lon)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(p.latitude)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = 6371 * c
    if distance <= radius:
        nearby.append(p)

print(f"✓ Pharmacies near Pune (10km): {len(nearby)}")
if nearby:
    pharmacy = nearby[0]
    items = Inventory.objects.filter(pharmacy=pharmacy, quantity__gt=0)
    print(f"✓ First pharmacy ({pharmacy.name}) has {items.count()} items in stock")

print("\n" + "="*70 + "\n")
