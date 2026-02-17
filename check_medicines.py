import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from webapp.models import Medicine

# Medicines from the prescription
prescription_meds = ['Levosiz', 'Zimig', 'Forcan', 'Levocetirizine', 'Ketoconazole', 'Fluconazole']

print("Checking medicines from prescription:\n")
for med in prescription_meds:
    results = Medicine.objects.filter(name__icontains=med)
    print(f'Checking "{med}":')
    print(f'  Found {results.count()} matches')
    for r in results[:5]:
        print(f'    - {r.name} (Generic: {r.generic_name})')
    print()

print("\n" + "="*50)
print("All medicines in database:")
print("="*50)
all_meds = Medicine.objects.all()
print(f"Total: {all_meds.count()}\n")
for m in all_meds[:30]:
    print(f"  {m.name} - {m.generic_name}")
