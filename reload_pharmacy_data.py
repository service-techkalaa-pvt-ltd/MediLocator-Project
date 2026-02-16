"""
Clear old pharmacy data and reload with new realistic names
Run: python reload_pharmacy_data.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from webapp.models import Pharmacy
from load_pharmacy_data import load_pharmacies

def reload_pharmacies():
    """Clear old pharmacies and load new ones"""
    
    print("\n" + "="*60)
    print("  🔄 Reloading Pharmacy Data with Realistic Names")
    print("="*60 + "\n")
    
    # Count existing pharmacies
    old_count = Pharmacy.objects.count()
    print(f"📊 Current pharmacies in database: {old_count}")
    
    # Ask for confirmation
    if old_count > 0:
        print(f"\n⚠️  This will delete all {old_count} existing pharmacy records!")
        confirm = input("Do you want to continue? (yes/no): ").strip().lower()
        
        if confirm not in ['yes', 'y']:
            print("❌ Operation cancelled.")
            return
        
        # Delete all dummy pharmacies (those with generic names)
        deleted_count = 0
        for pharmacy in Pharmacy.objects.all():
            # Delete pharmacies with pattern "City Number" or "Prefix Suffix - City Number"
            name = pharmacy.name
            if any(f" {i}" in name for i in range(1, 10)) or " - " in name:
                # Check if it ends with a number pattern
                words = name.split()
                if words[-1].isdigit() or (len(words) > 1 and words[-1].isdigit()):
                    pharmacy.delete()
                    deleted_count += 1
        
        print(f"🗑️  Deleted {deleted_count} old pharmacy records")
    
    # Load new pharmacies
    print(f"\n📦 Loading pharmacies with realistic names...")
    load_pharmacies()
    
    print("\n" + "="*60)
    print("  ✅ Reload Complete!")
    print("="*60 + "\n")


if __name__ == '__main__':
    reload_pharmacies()
