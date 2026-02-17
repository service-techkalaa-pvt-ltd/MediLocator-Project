"""
Add inventory for brand name medicines to existing pharmacy stock
"""
import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from webapp.models import Medicine, Pharmacy, Inventory
from decimal import Decimal

# Get brand medicines we just added
brand_medicines = Medicine.objects.filter(category='Brand Medicine')

print(f"Found {brand_medicines.count()} brand medicines")
print(f"Found {Pharmacy.objects.count()} pharmacies")

# Get all pharmacies
pharmacies = list(Pharmacy.objects.all())

if not pharmacies:
    print("❌ No pharmacies in database! Please add pharmacies first.")
    exit(1)

added = 0
skipped = 0

print("\nAdding inventory for brand medicines...")
print("=" * 60)

for medicine in brand_medicines:
    # Add to random pharmacies (30-70% of pharmacies have each medicine)
    num_pharmacies = random.randint(int(len(pharmacies) * 0.3), int(len(pharmacies) * 0.7))
    selected_pharmacies = random.sample(pharmacies, min(num_pharmacies, len(pharmacies)))
    
    for pharmacy in selected_pharmacies:
        # Check if inventory already exists
        existing = Inventory.objects.filter(pharmacy=pharmacy, medicine=medicine).first()
        
        if existing:
            skipped += 1
            continue
        
        # Create inventory
        Inventory.objects.create(
            pharmacy=pharmacy,
            medicine=medicine,
            quantity=random.randint(10, 100),
            price=Decimal(str(random.uniform(10.0, 500.0))),
            last_updated=django.utils.timezone.now()
        )
        added += 1
    
    print(f"✓ {medicine.name} → {len(selected_pharmacies)} pharmacies")

print("=" * 60)
print(f"\nSummary:")
print(f"  ✓ Inventory added: {added}")
print(f"  - Skipped (existing): {skipped}")
print(f"  📊 Total inventory items: {Inventory.objects.count()}")
print("\n✅ Done! Inventory added for brand medicines.")
