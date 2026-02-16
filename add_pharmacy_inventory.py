"""
Add medicines to all pharmacy inventories
Run: python add_pharmacy_inventory.py
"""
import os
import django
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from webapp.models import Pharmacy, Medicine, Inventory
from decimal import Decimal

def add_inventory_to_pharmacies():
    """Add medicines to all pharmacies that don't have inventory"""
    
    print("\n" + "="*60)
    print("  💊 Adding Medicines to All Pharmacies")
    print("="*60 + "\n")
    
    # Get all medicines
    medicines = list(Medicine.objects.all())
    total_medicines = len(medicines)
    
    if total_medicines == 0:
        print("❌ No medicines found in database! Please load medicines first.")
        return
    
    print(f"📋 Found {total_medicines} medicines in database")
    
    # Get all pharmacies
    pharmacies = Pharmacy.objects.all()
    total_pharmacies = pharmacies.count()
    
    print(f"🏪 Found {total_pharmacies} pharmacies\n")
    
    created_count = 0
    updated_count = 0
    
    for pharmacy in pharmacies:
        # Check if pharmacy already has inventory
        existing_inventory_count = Inventory.objects.filter(pharmacy=pharmacy).count()
        
        if existing_inventory_count > 0:
            print(f"⊘ {pharmacy.name} - Already has {existing_inventory_count} medicines")
            continue
        
        # Randomly select 30-80 medicines for this pharmacy
        num_medicines = random.randint(30, 80)
        selected_medicines = random.sample(medicines, min(num_medicines, total_medicines))
        
        # Create inventory items for each medicine
        for medicine in selected_medicines:
            # Random price between 20 and 500
            price = Decimal(str(round(random.uniform(20.0, 500.0), 2)))
            
            # Random quantity between 10 and 200
            quantity = random.randint(10, 200)
            
            Inventory.objects.create(
                pharmacy=pharmacy,
                medicine=medicine,
                quantity=quantity,
                price=price
            )
            created_count += 1
        
        print(f"✓ {pharmacy.name} - Added {len(selected_medicines)} medicines")
    
    print(f"\n" + "="*60)
    print(f"  ✅ Created {created_count} inventory items")
    print(f"  📊 Average: {created_count // total_pharmacies if total_pharmacies > 0 else 0} medicines per pharmacy")
    print("="*60 + "\n")


if __name__ == '__main__':
    add_inventory_to_pharmacies()
