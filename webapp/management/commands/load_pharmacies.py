"""
Management command to load pharmacy data into database
Usage: python manage.py load_pharmacies
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from webapp.models import Pharmacy
import random


class Command(BaseCommand):
    help = 'Load pharmacy data into database'

    def handle(self, *args, **options):
        # Get or create admin user for pharmacy owner
        admin_user, _ = User.objects.get_or_create(
            username='pharmacy_admin',
            defaults={'email': 'admin@medilocator.com', 'is_staff': True}
        )

        # Real data from your dataset
        pharmacies_data = [
            {'name': 'Janwa Medical', 'address': 'Shop No 01, near sancheti school, opposite krantiveer nagar, Laxman Nagar, Thergaon, Pimpri-Chinchwad, Maharashtra 411033', 'city': 'Pimpri-Chinchwad', 'rating': 4.9, 'lat': 18.6402164, 'lon': 73.8000315},
            {'name': 'Wellness Forever Pharmacy', 'address': 'Shop No 4, Ground Floor, Shiralkar Hospital, Pawana Nagar Housing Society, Chinchwad, Pune, Pimpri-Chinchwad, Maharashtra 411033', 'city': 'Pimpri-Chinchwad', 'rating': 3.4, 'lat': 18.683052, 'lon': 73.7295409},
            {'name': 'Morya Medical', 'address': 'Morya Medical, opp. Moraya Multispeciality Hospital, Gandhi Peth, Prabhat Colony, Chinchwad Gaon, Chinchwad, Pune, Pimpri-Chinchwad, Maharashtra 411033', 'city': 'Pimpri-Chinchwad', 'rating': 5.0, 'lat': 18.683052, 'lon': 73.7295409},
            {'name': 'Siddhivinayak Medical', 'address': 'Shop No 2, Jayavant Chember, Gandhi Peth, Prabhat Colony, Chinchwad Gaon, Chinchwad, Pimpri-Chinchwad, Maharashtra 411033', 'city': 'Pimpri-Chinchwad', 'rating': 4.8, 'lat': 18.6402164, 'lon': 73.8000315},
            {'name': 'Priyanka Medical', 'address': '141440, PCMC Link Rd, Wolf Colony, Chinchwad, Pimpri-Chinchwad, Maharashtra 411033', 'city': 'Pimpri-Chinchwad', 'rating': 4.9, 'lat': 18.6402164, 'lon': 73.8000315},
            {'name': 'Wellness Forever Pharmacy - Shivajinagar', 'address': 'Shop No 4, Ground Floor, Gokul Nagar, Fergusson College Rd, Sud Nagar, Shivajinagar, Pune, Maharashtra 411005', 'city': 'Pune', 'rating': 3.8, 'lat': 18.5325915, 'lon': 73.8513115},
            {'name': 'Mauli Medico', 'address': 'SHOP NO 4, MORYA RESIDENCY, TUKARAM PADUKA CHAUK, opposite DEENDAYAL HOSPITAL, Sud Nagar, Shivajinagar, Pune, Maharashtra 411005', 'city': 'Pune', 'rating': 4.3, 'lat': 18.5325915, 'lon': 73.8513115},
            {'name': 'Rahul Medicals', 'address': '1132/3, Fergusson College Rd, Rage Path, Model Colony, Shivajinagar, Pune, Maharashtra 411016', 'city': 'Pune', 'rating': 4.1, 'lat': 18.5325915, 'lon': 73.8513115},
            {'name': 'Phanse Medical', 'address': '211, near Panch Mukhi Maruti Temple, Gaothan, Shivajinagar, Pune, Maharashtra 411005', 'city': 'Pune', 'rating': 4.9, 'lat': 18.5325915, 'lon': 73.8513115},
            {'name': 'Medical House', 'address': '1133-2, Fergusson College Rd, Rage Path, Model Colony, Shivajinagar, Pune, Maharashtra 411016', 'city': 'Pune', 'rating': 4.2, 'lat': 18.5325915, 'lon': 73.8513115},
            {'name': 'Wellness Forever Pharmacy - Viman Nagar', 'address': 'Ground Floor, Clower Mews Co-Operative Society, Lohegaon, Viman Nagar, Pune, Maharashtra 411014', 'city': 'Pune', 'rating': 4.4, 'lat': 18.5703877, 'lon': 73.9133336},
            {'name': 'Pride Medico', 'address': 'Viman Nagar Rd, Clover Park, Viman Nagar, Pune, Maharashtra 411014', 'city': 'Pune', 'rating': 3.4, 'lat': 18.566367, 'lon': 73.918357},
            {'name': 'Apollo Pharmacy', 'address': 'Shop No 8, Gera Enclave, Ganapathi Chowk, Sainik Nagar, Clover Park, Viman Nagar, Pune, Maharashtra 411014', 'city': 'Pune', 'rating': 4.1, 'lat': 18.5703877, 'lon': 73.9133336},
            {'name': 'Zeno Health Pharmacy', 'address': 'Shop no. 3, Lunkad Plaza, Viman Nagar Rd, near Bangalore Iyangar Bakery, near Telephone Exchange, Clover Park, Viman Nagar, Pune, Maharashtra 411014', 'city': 'Pune', 'rating': 4.8, 'lat': 18.566367, 'lon': 73.918357},
            {'name': 'MedPlus', 'address': 'Shop no.9, Viman Pride, next to Bank of India, behind Phoenix Boundary Road, Clover Park, Viman Nagar, Pune, Maharashtra 411014', 'city': 'Pune', 'rating': 3.4, 'lat': 18.5703877, 'lon': 73.9133336},
            {'name': 'Shree Siddhivinayak Medical', 'address': 'Shop No.9, Sun Paradise - 1, Off Sinhgad Road, Sun City Rd, Anand Nagar, Pune, Maharashtra 411051', 'city': 'Pune', 'rating': 4.9, 'lat': 18.4782576, 'lon': 73.823807},
            {'name': 'Shraddha Generic Medical store', 'address': 'Shop no 5, Parshwa vihar society Near Saraswat bank, Sun City road, Sinhgad Rd, Pune, Maharashtra 411051', 'city': 'Pune', 'rating': 4.3, 'lat': 18.4538138, 'lon': 73.8388505},
            {'name': 'Harinandan medical', 'address': 'Shop no.7, Sr.no.9/1/2, Shivpatangmala building, near sinhgad college, Vadgaon Budruk, Maharashtra 411046', 'city': 'Pune', 'rating': 4.9, 'lat': 18.4675224, 'lon': 73.8355708},
            {'name': 'Keshav Medical', 'address': 'Sinhgad Rd, near hdfc bank, Vishranti Nagar, Vitthalwadi, Hingne Khurd, Pune, Maharashtra 411051', 'city': 'Pune', 'rating': 4.3, 'lat': 18.5213738, 'lon': 73.8545071},
            {'name': 'Shree Krupa Medical', 'address': 'Shop No 4, Shivpusha Park Suncity Road, Sinhgad Rd, Vadgaon Budruk, Pune, Maharashtra 411051', 'city': 'Pune', 'rating': 5.0, 'lat': 18.4674971, 'lon': 73.825365},
            {'name': 'Sai Medical', 'address': 'Ground Floor, Yashraj Complex, Shop No. 3, Sasane Nagar Rd, Chowk, Hadapsar, Pune, Maharashtra 411028', 'city': 'Pune', 'rating': 5.0, 'lat': 18.4934732, 'lon': 73.9326269},
            {'name': 'Wellness Forever Pharmacy - Hadapsar', 'address': 'Ground Floor, Kanifnath Colony, Sasane Nagar, Hadapsar, Pune, Maharashtra 411028', 'city': 'Pune', 'rating': 3.6, 'lat': 18.4934732, 'lon': 73.9326269},
            {'name': 'Chaitanya Medical', 'address': 'Near, S.No. 29B/4+5,Shop No. 3 & 4 Pratik Nagar Co-Op. Hsg. Soc, Railway, Crossing, Sasane Nagar, Hadapsar, Pune, Maharashtra 411028', 'city': 'Pune', 'rating': 3.6, 'lat': 18.4934732, 'lon': 73.9326269},
            {'name': 'Navjeevan Medical', 'address': 'Sai Nagar, Laxminarayan Colony, Satavwadi, Hadapsar, Pune, Maharashtra 411028', 'city': 'Pune', 'rating': 4.4, 'lat': 18.4934732, 'lon': 73.9326269},
            {'name': 'MedPlus Hadapsar', 'address': 'Matru Smruti Complex, SN 3, S No 227, Hadapsar, Pune, Maharashtra 411028', 'city': 'Pune', 'rating': 3.3, 'lat': 18.5007741, 'lon': 73.9379146},
            {'name': 'Wellness Forever Pharmacy - Hinjewadi', 'address': 'Shop No 16, Blue Ridge, Hinjewadi Phase 1 Rd, Unit, Pune, Maharashtra 411057', 'city': 'Pune', 'rating': 3.9, 'lat': 18.5927532, 'lon': 73.7382151},
            {'name': 'Vighnaharta medical and general store', 'address': 'Jay Ganesh colony, Plot no.65,milkat no.4861 Rajiv Gandhi Infotech park hinjewadi ph3,near TCS company Bhoirwadi, Pune, Maharashtra 411057', 'city': 'Pune', 'rating': 5.0, 'lat': 18.5213738, 'lon': 73.8545071},
            {'name': 'Pride Medico - Hinjewadi', 'address': 'Shop Number 1, Bappa Residency Society, Sakhare Vasti Road, Hinjewadi Phase 1 Rd, Hinjewadi, Pune, Maharashtra 411057', 'city': 'Pune', 'rating': 5.0, 'lat': 18.5927532, 'lon': 73.7382151},
            {'name': 'Arogya Medical', 'address': 'Laxmi chowk, sakhre dhawale vasti , Hinjewadi, Marunji Rd, Phase 1, Hinjewadi Rajiv Gandhi Infotech Park, Hinjewadi, Pimpri-Chinchwad, Maharashtra 411057', 'city': 'Pimpri-Chinchwad', 'rating': 4.8, 'lat': 18.5927532, 'lon': 73.7382151},
            {'name': 'Max Health Medico', 'address': 'Shop no.3 & 4.Fountain Market, Megapolis Cir, Phase 3, Hinjewadi, Pune, Maharashtra 411057', 'city': 'Pune', 'rating': 4.9, 'lat': 18.5927532, 'lon': 73.7382151},
            {'name': 'The Parel Chemist', 'address': 'Shop no 6,7, Lahar Bros. Mansion, opp. to KMS Hospital, Parel East, Parel, Mumbai, Maharashtra 400012', 'city': 'Mumbai', 'rating': 4.7, 'lat': 19.0094817, 'lon': 72.8376614},
            {'name': 'Shah Medical Store', 'address': 'Acharya Donde Marg, Parel East, Parel, Mumbai, Maharashtra 400012', 'city': 'Mumbai', 'rating': 4.2, 'lat': 19.0094817, 'lon': 72.8376614},
            {'name': 'National Chemist', 'address': '2345, Dr Ernest Borges Rd, Opp to KMS Hospital, Parel East, Parel, Mumbai, Maharashtra 400012', 'city': 'Mumbai', 'rating': 3.8, 'lat': 19.0094817, 'lon': 72.8376614},
            {'name': 'Ocean Pharmacy', 'address': 'Shop No.19, Pruthvi Vandan, NM Joshi Marg, Lower Parel East, BDD Chawl, Lower Parel, Mumbai, Maharashtra 400011', 'city': 'Mumbai', 'rating': 5.0, 'lat': 18.99568, 'lon': 72.8302756},
            {'name': 'Dhanlaxmi medical', 'address': 'Gd, Ambekar Nagar, B3 khaprideo chs ltd, parmanand wadi, Bhoiwada, Parel, Mumbai, Maharashtra 400012', 'city': 'Mumbai', 'rating': 4.3, 'lat': 18.99568, 'lon': 72.8302756},
            {'name': 'Lucky medical stores', 'address': '5/2, GREENLAND APARTMENT, S B Singh Colony, J B Nagar, Andheri East, Mumbai, Maharashtra 400059', 'city': 'Mumbai', 'rating': 3.8, 'lat': 19.1067657, 'lon': 72.8639412},
            {'name': 'Shastri Medical', 'address': 'Shop No. A-1, Ramniketan, Shivaji Chowk, Sahar Rd, Koldongri, Andheri East, Mumbai, Maharashtra 400069', 'city': 'Mumbai', 'rating': 3.9, 'lat': 19.1158835, 'lon': 72.854202},
            {'name': 'Krishna Medico', 'address': 'Shop No.6, Saroj Apartment, M. C. Road, opp. Holy Spirit Hospital, Sunder Nagar, Andheri East, Mumbai, Maharashtra 400093', 'city': 'Mumbai', 'rating': 3.1, 'lat': 19.1158835, 'lon': 72.854202},
            {'name': 'Zeno Health Pharmacy - Andheri', 'address': 'Shop No.1, Prajakta Apartment Circle, Andheri - Kurla Rd, opp. Amar juice Centre, Akal Society, Kanti Nagar, J B Nagar, Andheri East, Mumbai, Maharashtra 400059', 'city': 'Mumbai', 'rating': 4.7, 'lat': 19.1158835, 'lon': 72.854202},
            {'name': 'Andheri Chemist', 'address': 'Ashirwad Building, Sahar Rd, Railway Colony, Andheri East, Mumbai, Maharashtra 400069', 'city': 'Mumbai', 'rating': 4.2, 'lat': 19.1158835, 'lon': 72.854202},
            {'name': 'Deepak Medical Stores', 'address': 'Shop Number 1, Ground Floor, Classic Heritage, Aarey Rd, Peru Baug, Churi Wadi, Goregaon, Mumbai, Maharashtra 400063', 'city': 'Mumbai', 'rating': 4.1, 'lat': 19.1648688, 'lon': 72.8495492},
            {'name': 'Hari Om Medical', 'address': 'Vijay bhavan, 5, Aarey Rd, opp. police chowki, Jay Prakash Nagar, Goregaon, Mumbai, Maharashtra 400063', 'city': 'Mumbai', 'rating': 4.5, 'lat': 19.1642497, 'lon': 72.8395324},
            {'name': 'Khona Medical Store', 'address': 'SHOP 17, India, 400063, Vishveshwar Nagar Rd, Churi Wadi, Goregaon, Mumbai, Maharashtra 400063', 'city': 'Mumbai', 'rating': 4.3, 'lat': 19.1642497, 'lon': 72.8395324},
            {'name': 'Krishna Medical Store', 'address': 'Shop, A1, Suraj Heights, Vallabhbhai Patel Road, Shiv Shankar Nagar, Goregaon, Mumbai, Maharashtra 400063', 'city': 'Mumbai', 'rating': 5.0, 'lat': 19.1642497, 'lon': 73.918357},
            {'name': 'Ravi Medical', 'address': 'C.H.S.Ltd, Raj Residency, Shop no 8 & 9, B wing, Mahatma Gandhi Rd, Motilal Nagar III, Goregaon West, Mumbai, Maharashtra 400104', 'city': 'Mumbai', 'rating': 4.8, 'lat': 19.1642497, 'lon': 72.8395324},
            {'name': 'Zeno Health Pharmacy - Borivali', 'address': 'Shop No.5, Eugenia Building, Holy Cross Rd, I C Colony, Borivali West, Mumbai, Maharashtra 400103', 'city': 'Mumbai', 'rating': 4.9, 'lat': 19.2298129, 'lon': 72.8471376},
            {'name': 'Health Plus Medicals', 'address': '6V83+Q35, Khushali niwas,Ram Baug lane, Swami Vivekananda Rd, Dattani Nagar, Borivali West, Mumbai, Maharashtra 400092', 'city': 'Mumbai', 'rating': 4.9, 'lat': 19.2310267, 'lon': 72.8555369},
            {'name': 'Prithvi Chemist', 'address': 'Shop No: 1, 2, 3 Ganesh Darshan C.H.S, Lokmanya Tilak Rd, Lokmanya Tilak Nagar, Borivali West, Mumbai, Maharashtra 400092', 'city': 'Mumbai', 'rating': 3.5, 'lat': 19.2221864, 'lon': 72.8611566},
            {'name': 'Dharamnath Chemist & Medico', 'address': 'Gumpha Darshan C chs., Asara Colony Rd, opposite Shri gaon devi temple, Jaya Nagar, Borivali East, Mumbai, Maharashtra 400066', 'city': 'Mumbai', 'rating': 4.9, 'lat': 19.2221864, 'lon': 72.8611566},
            {'name': 'Vassu Medical', 'address': 'B-3, /10/0:3, PLOT NO.1, Juhu Nagar, Sector 15, Vashi, Navi Mumbai, Maharashtra 400703', 'city': 'Navi Mumbai', 'rating': 5.0, 'lat': 19.0868905, 'lon': 73.0032927},
            {'name': 'Satish Medical', 'address': 'SS-III/230, Xerox Ln, Sector 2, Vashi, Navi Mumbai, Mumbai, Maharashtra 400703', 'city': 'Navi Mumbai', 'rating': 4.5, 'lat': 19.1511011, 'lon': 72.9995356},
            {'name': 'Classic Medico', 'address': 'Mahavir Center, 11/B, near Golden Punjab Hotel, Sector 17, Vashi, Navi Mumbai, Maharashtra 400703', 'city': 'Navi Mumbai', 'rating': 3.9, 'lat': 19.0632481, 'lon': 72.9987966},
            {'name': 'Health First Medical', 'address': 'Shop No 2, Shivam Complex, Plot No 47, Palm Beach Rd, Sector 19E, Vashi, Navi Mumbai, Maharashtra 400703', 'city': 'Navi Mumbai', 'rating': 3.5, 'lat': 19.0632481, 'lon': 72.9987966},
            {'name': 'Navi Mumbai Medico', 'address': 'plot number.20 d, Balaji Sadan, Shop Number.7, Sector 15, Vashi, Navi Mumbai, Maharashtra 400705', 'city': 'Navi Mumbai', 'rating': 5.0, 'lat': 19.0632481, 'lon': 72.9987966},
            {'name': 'Care Medico', 'address': 'First Floor, Shop No.122, Arenja Arcade Premises Co-operative Society Limited, Plot 4, Vashi Flyover, Navi Mumbai, Maharashtra 400705', 'city': 'Navi Mumbai', 'rating': 4.8, 'lat': 19.0682628, 'lon': 73.0009189},
            {'name': 'Krishna Medico', 'address': 'New Era Talkies Compound, G1-3, Swami Vivekananda Rd, Malad, Navy Colony, Mamledarwadi, Malad West, Mumbai, Maharashtra 400064', 'city': 'Mumbai', 'rating': 3.1, 'lat': 19.1852851, 'lon': 72.8358611},
            {'name': 'Zeno Health Pharmacy - Malad', 'address': 'Shop no.3, Modern Vivek CHS, near Bmc Office, opp. Post office, Malad, Navy Colony, Mamledarwadi, Malad West, Mumbai, Maharashtra 400064', 'city': 'Mumbai', 'rating': 4.8, 'lat': 19.1852851, 'lon': 72.8358611},
            {'name': 'Maharastra Medical', 'address': 'Shop No.7, Dheeraj Platinum, Chincholi Bunder Rd, Malad, Chincholi Bunder, Malad West, Mumbai, Maharashtra 400064', 'city': 'Mumbai', 'rating': 4.6, 'lat': 19.1852851, 'lon': 72.8358611},
            {'name': 'Noble Medical', 'address': 'Nav Meena Apt, 4, Mamalatdar Wadi Road, opposite Abhijeet Hospital, Malad, Navy Colony, Mamledarwadi, Malad West, Mumbai, Maharashtra 400064', 'city': 'Mumbai', 'rating': 3.4, 'lat': 19.1852851, 'lon': 72.8358611},
            {'name': 'Triveni Medical', 'address': 'TRIVENI MEDICAL STORE , SHOP NO. 1, Vijay Nagar, ASHRAM, Mumbai, Maharashtra 400064', 'city': 'Mumbai', 'rating': 4.4, 'lat': 19.029517, 'lon': 72.872744},
        ]

        # Add 100+ dummy pharmacies across various Indian cities
        dummy_pharmacies = self._generate_dummy_pharmacies()
        all_pharmacies = pharmacies_data + dummy_pharmacies

        # Bulk create pharmacies
        created_count = 0
        for pharmacy_data in all_pharmacies:
            pharmacy, created = Pharmacy.objects.get_or_create(
                name=pharmacy_data['name'],
                latitude=pharmacy_data['lat'],
                longitude=pharmacy_data['lon'],
                defaults={
                    'address': pharmacy_data['address'],
                    'city': pharmacy_data['city'],
                    'phone': '9876543210',
                    'owner': admin_user,
                    'verified': True,
                    'rating': pharmacy_data['rating'],
                }
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} pharmacies')
        )

    def _generate_dummy_pharmacies(self):
        """Generate 100+ dummy pharmacies"""
        pharmacy_names = [
            'Health Plus', 'MedCare', 'City Pharmacy', 'Express Medicals', 'Quick Health',
            'Star Pharmacy', 'Prime Medicals', 'Elite Health', 'Sunrise Pharmacy', 'Best Medicals',
            'Universal Health', 'Noble Pharmacy', 'Divine Medicals', 'Care Plus', 'Life Pharmacy',
            'Smart Medicals', 'Safe Health', 'Total Pharmacy', 'Pure Health', 'Gold Medicals',
            'Silver Pharmacy', 'Bright Health', 'Hope Medicals', 'Unity Pharmacy', 'Trust Health',
            'Apex Medicals', 'Crown Pharmacy', 'Royal Health', 'Gem Medicals', 'Pearl Pharmacy',
            'Comfort Health', 'Wellness Hub', 'Healing Pharmacy', 'Vitality Medicals', 'Remedy Health',
            'Guardian Pharmacy', 'Shield Medicals', 'Haven Health', 'Peak Pharmacy', 'Victory Medicals',
        ]

        cities_with_coords = [
            ('Delhi', 28.7041, 77.1025),
            ('Mumbai', 19.0760, 72.8777),
            ('Bangalore', 12.9716, 77.5946),
            ('Hyderabad', 17.3850, 78.4867),
            ('Chennai', 13.0827, 80.2707),
            ('Kolkata', 22.5726, 88.3639),
            ('Pune', 18.5204, 73.8567),
            ('Ahmedabad', 23.0225, 72.5714),
            ('Jaipur', 26.9124, 75.7873),
            ('Lucknow', 26.8467, 80.9462),
            ('Chandigarh', 30.7333, 76.7794),
            ('Indore', 22.7196, 75.8577),
            ('Kochi', 9.9312, 76.2673),
            ('Surat', 21.1458, 72.1640),
            ('Visakhapatnam', 17.6869, 83.2185),
        ]

        dummy_pharmacies = []
        created = 0

        for city, base_lat, base_lon in cities_with_coords:
            for i in range(8):  # 8 pharmacies per city = 120 total
                if created >= 100:
                    break
                
                name = f"{random.choice(pharmacy_names)} - {city}"
                # Add slight variation to coordinates to create different locations
                lat = base_lat + random.uniform(-0.05, 0.05)
                lon = base_lon + random.uniform(-0.05, 0.05)
                rating = round(random.uniform(3.0, 5.0), 1)
                
                dummy_pharmacies.append({
                    'name': name,
                    'address': f"Shop {i+1}, {random.choice(['Main Street', 'Market Road', 'Square', 'Plaza'])} {city}, India",
                    'city': city,
                    'rating': rating,
                    'lat': lat,
                    'lon': lon,
                })
                created += 1

        return dummy_pharmacies
