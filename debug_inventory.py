#!/usr/bin/env python
"""Debug inventory - find what medicines we actually have"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from webapp.models import Inventory, Medicine

print("\n" + "="*70)
print("DEBUG: INVENTORY DATA CHECK")
print("="*70)

# Check medicines that exist
print("\n1. Checking Paracetamol medicines:")
para_meds = Medicine.objects.filter(name__icontains='paracetamol')
print(f"   Found: {para_meds.count()}")
for med in para_meds[:5]:
    print(f"   - {med.id}: {med.name} (Generic: {med.generic_name})")

# Check inventory for these medicines
print("\n2. Checking Inventory for Paracetamol:")
para_inv = Inventory.objects.filter(medicine__name__icontains='paracetamol', quantity__gt=0)
print(f"   Found: {para_inv.count()} inventory items")
for inv in para_inv[:5]:
    print(f"   - Pharmacy: {inv.pharmacy.name}")
    print(f"     Medicine: {inv.medicine.name}")
    print(f"     Qty: {inv.quantity}, Price: {inv.price}")

# Sample inventory from first pharmacy
print("\n3. Sample Inventory from first pharmacy:")
from webapp.models import Pharmacy
first = Pharmacy.objects.first()
if first:
    print(f"   Pharmacy: {first.name}")
    items = Inventory.objects.filter(pharmacy=first, quantity__gt=0)
    print(f"   Total items in stock: {items.count()}")
    for item in items[:5]:
        print(f"   - {item.medicine.name}: {item.quantity} units @ ₹{item.price}")

# Check all medicine names (sample)
print("\n4. Sample of all medicines in database:")
all_meds = Medicine.objects.all()[:20]
for med in all_meds:
    print(f"   - {med.name}")

print("\n" + "="*70 + "\n")
