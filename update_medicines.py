"""
Update medicines with new comprehensive list and populate inventory
"""
import os
import sys
import django
import random
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from webapp.models import Medicine, Pharmacy, Inventory

# Comprehensive medicine list
MEDICINES = [
    "Paracetamol (Tylenol)",
    "Ibuprofen (Advil)",
    "Amoxicillin",
    "Azithromycin",
    "Metformin",
    "Atorvastatin",
    "Amlodipine",
    "Losartan",
    "Pantoprazole",
    "Omeprazole",
    "Levothyroxine",
    "Cetirizine",
    "Montelukast",
    "Salbutamol (Albuterol)",
    "Aspirin",
    "Clopidogrel",
    "Metoprolol",
    "Lisinopril",
    "Hydrochlorothiazide",
    "Furosemide",
    "Insulin",
    "Prednisolone",
    "Diclofenac",
    "Tramadol",
    "Sertraline",
    "Fluoxetine",
    "Alprazolam",
    "Lorazepam",
    "Vitamin D (Cholecalciferol)",
    "Calcium + Vitamin D",
    "Cetirizine + Montelukast",
    "Cefixime",
    "Cefuroxime",
    "Doxycycline",
    "Ciprofloxacin",
    "Levofloxacin",
    "Ranitidine",
    "Esomeprazole",
    "Famotidine",
    "Domperidone",
    "Ondansetron",
    "Iron + Folic Acid",
    "Multivitamin Tablets",
    "Glimepiride",
    "Sitagliptin",
    "Pioglitazone",
    "Gliclazide",
    "Insulin Glargine",
    "Insulin Aspart",
    "Paracetamol + Caffeine",
    "Naproxen",
    "Diclofenac + Paracetamol",
    "Mefenamic Acid",
    "Nimesulide",
    "Cyclobenzaprine",
    "Tizanidine",
    "Gabapentin",
    "Pregabalin",
    "Pantoprazole + Domperidone",
    "Sucralfate",
    "Lactulose",
    "Bisacodyl",
    "Loperamide",
    "ORS (Oral Rehydration Solution)",
    "Zinc Sulphate",
    "Azithromycin + Lactic Acid Bacillus",
    "Clotrimazole",
    "Fluconazole",
    "Ketoconazole",
    "Betamethasone",
    "Hydrocortisone",
    "Mometasone",
    "Levocetirizine",
    "Fexofenadine",
    "Loratadine",
    "Budesonide",
    "Fluticasone",
    "Ipratropium Bromide",
    "Tiotropium",
    "Amoxicillin + Clavulanic Acid",
    "Cefpodoxime",
    "Ceftriaxone",
    "Metronidazole",
    "Tinidazole",
    "Ornidazole",
    "Chloroquine",
    "Hydroxychloroquine",
    "Albendazole",
    "Ivermectin",
    "Paracetamol + Ibuprofen",
    "Azithromycin + Paracetamol",
    "Vitamin B-Complex",
    "Omega-3 Fatty Acids",
    "Ferrous Ascorbate",
    "Vitamin C (Ascorbic Acid)",
    "Melatonin",
    "Sildenafil",
    "Tadalafil",
    "Levonorgestrel",
    "Dextromethorphan + Chlorpheniramine + Phenylephrine",
]

def main():
    print("=" * 60)
    print("UPDATING MEDICINES DATABASE")
    print("=" * 60)
    
    # Step 1: Clear old medicines and inventory
    print("\n[1/4] Clearing old data...")
    old_medicine_count = Medicine.objects.count()
    old_inventory_count = Inventory.objects.count()
    Inventory.objects.all().delete()
    Medicine.objects.all().delete()
    print(f"✓ Deleted {old_medicine_count} medicines")
    print(f"✓ Deleted {old_inventory_count} inventory records")
    
    # Step 2: Add new medicines
    print("\n[2/4] Adding new medicines...")
    medicines_created = []
    for med_name in MEDICINES:
        medicine, created = Medicine.objects.get_or_create(
            name=med_name,
            defaults={
                'generic_name': med_name.split('(')[0].strip() if '(' in med_name else med_name,
                'category': 'General',
                'description': f'{med_name} - Available at verified pharmacies'
            }
        )
        medicines_created.append(medicine)
        if created:
            print(f"  ✓ Added: {med_name}")
    
    print(f"\n✓ Total medicines: {len(medicines_created)}")
    
    # Step 3: Get all pharmacies
    print("\n[3/4] Loading pharmacies...")
    pharmacies = list(Pharmacy.objects.all())
    print(f"✓ Found {len(pharmacies)} pharmacies")
    
    # Step 4: Populate inventory
    print("\n[4/4] Populating inventory...")
    inventory_count = 0
    
    for pharmacy in pharmacies:
        # Each pharmacy will have 60-90% of medicines in stock
        num_medicines = random.randint(int(len(medicines_created) * 0.6), int(len(medicines_created) * 0.9))
        selected_medicines = random.sample(medicines_created, num_medicines)
        
        for medicine in selected_medicines:
            # Random stock quantity and price
            quantity = random.randint(10, 200)
            base_price = random.randint(20, 500)
            price = Decimal(str(base_price + random.randint(0, 50)))
            
            Inventory.objects.create(
                pharmacy=pharmacy,
                medicine=medicine,
                quantity=quantity,
                price=price
            )
            inventory_count += 1
        
        print(f"  ✓ {pharmacy.name}: {len(selected_medicines)} medicines")
    
    print(f"\n✓ Created {inventory_count} inventory records")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Medicines: {Medicine.objects.count()}")
    print(f"Pharmacies: {Pharmacy.objects.count()}")
    print(f"Inventory Records: {Inventory.objects.count()}")
    print(f"Average medicines per pharmacy: {inventory_count / len(pharmacies):.1f}")
    
    # Test search
    print("\n" + "=" * 60)
    print("TESTING MEDICINE SEARCH")
    print("=" * 60)
    
    test_medicines = ['Paracetamol', 'Ibuprofen', 'Amoxicillin', 'Alprazolam']
    for test_med in test_medicines:
        med = Medicine.objects.filter(name__icontains=test_med).first()
        if med:
            inv_count = Inventory.objects.filter(medicine=med, quantity__gt=0).count()
            print(f"✓ {med.name}: Available at {inv_count} pharmacies")
        else:
            print(f"✗ {test_med}: Not found")
    
    print("\n" + "=" * 60)
    print("✅ UPDATE COMPLETE!")
    print("=" * 60)

if __name__ == '__main__':
    main()
