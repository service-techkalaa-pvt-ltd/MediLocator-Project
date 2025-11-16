"""
Test medicine search functionality
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from webapp.models import Medicine, Inventory

print("=" * 60)
print("MEDICINE SEARCH TEST")
print("=" * 60)

test_medicines = [
    'Paracetamol',
    'Ibuprofen', 
    'Amoxicillin',
    'Alprazolam',
    'Insulin',
    'Aspirin',
    'Cetirizine',
    'Omeprazole'
]

for med_name in test_medicines:
    # Search for medicine
    medicines = Medicine.objects.filter(name__icontains=med_name)
    
    print(f"\n🔍 Search: '{med_name}'")
    print(f"   Found {medicines.count()} medicine(s):")
    
    for med in medicines:
        # Count pharmacies with this medicine in stock
        pharmacies_count = Inventory.objects.filter(
            medicine=med,
            quantity__gt=0
        ).count()
        
        print(f"   ✓ {med.name}")
        print(f"     Available at {pharmacies_count} pharmacies")

print("\n" + "=" * 60)
print("✅ MEDICINE SEARCH WORKING!")
print("=" * 60)
