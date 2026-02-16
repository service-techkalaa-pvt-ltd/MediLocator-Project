"""
Clear ALL pharmacies and reload with new realistic names within 5km radius
Run: python clear_and_reload_pharmacies.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from webapp.models import Pharmacy
from load_pharmacy_data import load_pharmacies

def clear_and_reload():
    """Clear ALL pharmacies and load new ones"""
    
    print("\n" + "="*60)
    print("  🔄 Clear & Reload Pharmacies (5km Radius)")
    print("="*60 + "\n")
    
    # Count existing pharmacies
    old_count = Pharmacy.objects.count()
    print(f"📊 Current pharmacies in database: {old_count}")
    
    if old_count > 0:
        print(f"\n⚠️  This will DELETE ALL {old_count} pharmacy records!")
        confirm = input("Continue? (yes/no): ").strip().lower()
        
        if confirm not in ['yes', 'y']:
            print("❌ Cancelled.")
            return
        
        # Delete ALL pharmacies
        deleted = Pharmacy.objects.all().delete()
        print(f"🗑️  Deleted all pharmacy records")
    
    # Load new pharmacies with corrected coordinates
    print(f"\n📦 Loading pharmacies within 5km radius...")
    load_pharmacies()
    
    print("\n" + "="*60)
    print("  ✅ All pharmacies now within 5km radius!")
    print("="*60 + "\n")


if __name__ == '__main__':
    clear_and_reload()
