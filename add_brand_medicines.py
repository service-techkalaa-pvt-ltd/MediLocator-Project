"""
Add common brand name medicines to database
Maps brand names to generic names for better prescription OCR
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from webapp.models import Medicine

# Common brand names to add (Brand Name: Generic Name)
BRAND_MEDICINES = {
    # From prescription example
    'Levosiz': 'Levocetirizine',
    'Levosiz 5mg': 'Levocetirizine',
    'Zimig': 'Ketoconazole',
    'Zimig 1%': 'Ketoconazole',
    'Forcan': 'Fluconazole',
    'Forcan 150mg': 'Fluconazole',
    
    # Common antihistamines
    'Levocet': 'Levocetirizine',
    'Zyrtec': 'Cetirizine',
    'Cetzine': 'Cetirizine',
    'Allegra': 'Fexofenadine',
    
    # Common antifungals
    'Diflucan': 'Fluconazole',
    'Flucon': 'Fluconazole',
    'Ketocip': 'Ketoconazole',
    'Nizral': 'Ketoconazole',
    
    # Common antibiotics
    'Mox': 'Amoxicillin',
    'Novamox': 'Amoxicillin',
    'Mox 500': 'Amoxicillin',
    'Amoxil': 'Amoxicillin',
    'Zithromax': 'Azithromycin',
    'Azee': 'Azithromycin',
    'Azithral': 'Azithromycin',
    'Azee 500': 'Azithromycin',
    'Augmentin': 'Amoxicillin + Clavulanic Acid',
    'Cipcal': 'Ciprofloxacin',
    'Ciplox': 'Ciprofloxacin',
    
    # Common pain/fever
    'Crocin': 'Paracetamol',
    'Dolo 650': 'Paracetamol',
    'Calpol': 'Paracetamol',
    'Metacin': 'Paracetamol',
    'Brufen': 'Ibuprofen',
    'Combiflam': 'Ibuprofen + Paracetamol',
    'Saridon': 'Paracetamol + Caffeine',
    
    # Blood pressure
    'Amlodac': 'Amlodipine',
    'Amlong': 'Amlodipine',
    'Norvasc': 'Amlodipine',
    'Telma': 'Telmisartan',
    'Stamlo': 'Amlodipine',
    
    # Cholesterol
    'Atorva': 'Atorvastatin',
    'Lipitor': 'Atorvastatin',
    'Deplatt': 'Clopidogrel',
    'Storvas': 'Atorvastatin',
    
    # Diabetes
    'Glycomet': 'Metformin',
    'Glucophage': 'Metformin',
    'Januvia': 'Sitagliptin',
    'Janumet': 'Sitagliptin + Metformin',
    
    # Proton pump inhibitors
    'Pan 40': 'Pantoprazole',
    'Pantocid': 'Pantoprazole',
    'Esoz': 'Esomeprazole',
    'Omez': 'Omeprazole',
    'Rablet': 'Rabeprazole',
    'Pantodac': 'Pantoprazole',
}

def add_brand_medicines():
    """Add brand name medicines to database"""
    added = 0
    skipped = 0
    updated = 0
    
    print("Adding brand name medicines to database...")
    print("=" * 60)
    
    for brand_name, generic_name in BRAND_MEDICINES.items():
        # Check if already exists
        existing = Medicine.objects.filter(name__iexact=brand_name).first()
        
        if existing:
            # Update generic name if different
            if existing.generic_name != generic_name:
                existing.generic_name = generic_name
                existing.save()
                print(f"✓ Updated: {brand_name} → {generic_name}")
                updated += 1
            else:
                print(f"- Skipped: {brand_name} (already exists)")
                skipped += 1
        else:
            # Create new medicine entry
            Medicine.objects.create(
                name=brand_name,
                generic_name=generic_name,
                description=f'Brand name for {generic_name}',
                category='Brand Medicine'
            )
            print(f"+ Added: {brand_name} → {generic_name}")
            added += 1
    
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  ✓ Added: {added}")
    print(f"  ↻ Updated: {updated}")
    print(f"  - Skipped: {skipped}")
    print(f"  📊 Total medicines now: {Medicine.objects.count()}")
    print("\n✅ Done! Brand names added successfully.")

if __name__ == '__main__':
    add_brand_medicines()
