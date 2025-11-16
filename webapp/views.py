import numpy as np
import os
from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import CreateUserForm
import joblib
from django.http import JsonResponse
import difflib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import FileResponse
import re
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pickle
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import io

# Create your views here.
def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)
                return redirect('login')

        context = {'form': form}
        return render(request, 'accounts/register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'accounts/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def home(request):
    return render(request, 'accounts/index.html')


def search_results_page(request):
    """Display search results page"""
    return render(request, 'accounts/search_results.html')


@login_required(login_url='login')
def search_manual_page(request):
    """Display manual pharmacy search page"""
    return render(request, 'accounts/search_manual.html')


@login_required(login_url='login')
def search_gps_page(request):
    """Display GPS-based pharmacy search page"""
    return render(request, 'accounts/search_gps.html')


def chatbot_page(request):
    return render(request, "accounts/chatbot.html")

def about_us(request):
    return render(request, "accounts/about_us.html")

@login_required(login_url='login')
def home1(request):
    return render(request, 'accounts/PrescriptionScanner.html')

@login_required(login_url='login')
def predict(request):
    city=(request.POST.dict()['fulltextarea'])
    print(city)
    b=[]
    b.append(city)
    print(b)

    # --- Put your addresses here (or read from file) ---
    addresses = b

    # --- Updated cleaning/shortening function ---
    def shorten_address(addr, keep_parts=3):
        if not addr:
            return ""
        s = str(addr)

        # 1) remove Indian pincode (5-6 digits)
        s = re.sub(r"\b\d{5,6}\b", "", s)

        # 2) remove common noisy words
        noisy = r"\b(shop|shop no|shop no\.|ground floor|ground|floor|opp|opp\.|opposite|near|nearby|near to|opp to|flat|unit|building|block|plot|phase|phase no|phase)\b"
        s = re.sub(noisy, "", s, flags=re.I)

        # 3) remove special chars (keep commas, alnum + spaces)
        s = re.sub(r"[^A-Za-z0-9, ]+", " ", s)

        # 4) collapse whitespace and trim
        s = re.sub(r"\s+", " ", s).strip()

        # 5) split by commas
        parts = [p.strip() for p in s.split(",") if p.strip()]

        # 6) Always keep parts containing "Nagar"
        nagar_parts = [p for p in parts if "nagar" in p.lower()]

        # 7) Keep last `keep_parts` meaningful parts
        main_parts = parts[-keep_parts:]

        # 8) Combine unique parts (keep Nagar parts first)
        combined_parts = nagar_parts + [p for p in main_parts if p not in nagar_parts]

        short = ", ".join(combined_parts)
        if short and "india" not in short.lower():
            short = short + ", India"
        return short

    # --- geocoder init ---
    geolocator = Nominatim(user_agent="my_geocode_script_example@example.com")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    # --- geocode addresses ---
    rows = []
    for orig in addresses:
        short = shorten_address(orig, keep_parts=3)
        loc = None

        try:
            if short:
                loc = geocode(short, timeout=10)
        except Exception:
            loc = None

        # fallback: if nothing found, try appending the detected city
        if not loc:
            o = orig.lower()
            try:
                if "pune" in o or "pimpri" in o or "pcmc" in o:
                    loc = geocode((short + ", Pune, India").strip(), timeout=10)
                elif "mumbai" in o or "navi mumbai" in o or "thane" in o:
                    loc = geocode((short + ", Mumbai, India").strip(), timeout=10)
            except Exception:
                loc = None

        rows.append({
            "original_address": orig,
            "short_address": short,
            "latitude": loc.latitude if loc else None,
            "longitude": loc.longitude if loc else None
        })

    # print(rows)

    # Extract latitude and longitude
    lat_lon = [[rows[0]['latitude'], rows[0]['longitude']]]

    # --- Step: Load model for testing/query ---
    loaded = pickle.load(open('knn_address_model.sav', 'rb'))
    model = loaded['model']
    scaler = loaded['scaler']
    df = loaded['df']

    # --- Step: Query
    query_point = lat_lon  # latitude & longitude
    query_scaled = scaler.transform(query_point)

    # --- Step: Get top 3 nearest addresses
    distances, indices = model.kneighbors(query_scaled, n_neighbors=3)

    # --- Step: Fetch addresses and ratings
    nearest_addresses = df.iloc[indices[0]]['Address'].values
    nearest_ratings = df.iloc[indices[0]]['Rating'].values
    medical_names = df.iloc[indices[0]]['Medical Names'].values

    nearest_addresses_store = []
    nearest_ratings_store = []
    nearest_meds = []

    # --- Step: Print results ---
    for addr, rating,med in zip(nearest_addresses, nearest_ratings,medical_names):
        nearest_addresses_store.append(addr)
        nearest_ratings_store.append(rating)
        nearest_meds.append(med)
        # print(f"Address: {addr}, Rating: {rating}")

    print("this is meds", nearest_ratings_store)
    print("this is add",nearest_addresses_store)
    print("this is rat",nearest_ratings_store)


    return render(request, 'accounts/medical_reco.html',{"med1": nearest_meds[0], "med2": nearest_meds[1], "med3": nearest_meds[2],"add1": nearest_addresses_store[0], "add2": nearest_addresses_store[1], "add3": nearest_addresses_store[2], "rat1": nearest_ratings_store[0],"rat2": nearest_ratings_store[1],"rat3": nearest_ratings_store[2]})


@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("user_message", "").lower()

        responses = {
            "breakfast diet": "A healthy breakfast includes protein, fiber, and healthy fats. Try eggs, oatmeal, or fruit smoothies.",
            "lunch diet": "For lunch, opt for lean proteins like chicken or tofu with veggies and whole grains.",
            "dinner diet": "Dinner should be light with soups, salads, and grilled proteins.",
            "exercise tips": "Regular exercise boosts health! Check this video: https://www.youtube.com/embed/TjzwohzLJgA"
        }
        disease_links = {
            "diabetes": "Watch this YouTube video for more details: https://www.youtube.com/embed/-uK8a80vyeI",
            "hypertension": "Watch this video: https://www.youtube.com/embed/TjzwohzLJgA",
            "malaria": "Check this link: https://www.youtube.com/embed/zWf5ZaCo0BI",
            "heart disease": "Watch this: https://www.youtube.com/embed/SFWvoNZtUkk",
            "normal health": "Healthy living tips here: https://www.youtube.com/embed/PG2f3GF5RlI"
        }

        bot_reply = responses.get(user_message, disease_links.get(user_message, "Sorry, I don't understand that."))
        return JsonResponse({"bot_reply": bot_reply})

    return JsonResponse({"error": "Invalid request"}, status=400)


from django.shortcuts import render, redirect
from .forms import FeedbackForm
from .models import Feedback


def feedback_view(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "accounts/feedback_success.html")
    else:
        form = FeedbackForm()

    return render(request, "accounts/feedback.html", {"form": form})


# Additional views for premium features
@login_required(login_url='login')
def user_profile(request):
    """User profile page"""
    return render(request, 'accounts/user_profile.html')


@login_required(login_url='login')
def prescription_scanner(request):
    """Prescription upload page"""
    return render(request, 'accounts/PrescriptionScanner.html')


@login_required(login_url='login')
def pharmacy_dashboard(request):
    """Pharmacy owner dashboard"""
    if request.user.profile.role != 'PHARMACY_OWNER':
        messages.warning(request, 'You need pharmacy owner access to view this page.')
        return redirect('home')
    return render(request, 'accounts/pharmacy_dashboard.html')


@login_required(login_url='login')
def admin_dashboard(request):
    """Admin dashboard"""
    if not (request.user.is_staff or request.user.profile.role == 'ADMIN'):
        messages.warning(request, 'You need admin access to view this page.')
        return redirect('home')
    return render(request, 'accounts/admin_dashboard.html')


@csrf_exempt
def keep_alive(request):
    """API endpoint to keep session alive"""
    if request.method == 'POST' and request.user.is_authenticated:
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)


@csrf_exempt
def search_pharmacies(request):
    """
    Search pharmacies by location and radius with medicine availability
    GET /api/search-pharmacies/?lat=18.5&lon=73.8&radius=5&medicine=paracetamol&sort=distance
    sort options: distance, rating, available
    """
    if request.method == 'GET':
        try:
            import math
            
            lat = float(request.GET.get('lat', 0))
            lon = float(request.GET.get('lon', 0))
            radius = float(request.GET.get('radius', 5))  # km
            medicine_name = request.GET.get('medicine', '').strip()
            sort_by = request.GET.get('sort', 'distance')  # distance, rating, available
            city = request.GET.get('city', '').strip()  # Add city parameter
            
            if not lat or not lon:
                return JsonResponse({
                    'success': False,
                    'error': 'Latitude and longitude are required',
                    'pharmacies': []
                }, status=400)
            
            # Search pharmacies within radius using distance formula
            # Approximate: 1 degree = 111 km
            lat_range = radius / 111.0
            lon_range = radius / (111.0 * abs(math.cos(math.radians(lat))))
            
            pharmacy_filter = Pharmacy.objects.filter(
                latitude__gte=lat - lat_range,
                latitude__lte=lat + lat_range,
                longitude__gte=lon - lon_range,
                longitude__lte=lon + lon_range,
                verified=True
            )
            
            # If city is provided, filter by city
            if city:
                pharmacy_filter = pharmacy_filter.filter(city__iexact=city)
            
            pharmacies = pharmacy_filter.values('id', 'name', 'address', 'city', 'phone', 'latitude', 'longitude', 'rating')
            
            # Calculate distance for each pharmacy and get medicine info
            pharmacy_list = []
            for pharmacy in pharmacies:
                # Haversine formula for accurate distance
                dlat = math.radians(pharmacy['latitude'] - lat)
                dlon = math.radians(pharmacy['longitude'] - lon)
                a = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(pharmacy['latitude'])) * math.sin(dlon/2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                distance = 6371 * c  # km
                
                if distance <= radius:
                    # Get medicines available at this pharmacy
                    inventory_items = Inventory.objects.filter(
                        pharmacy_id=pharmacy['id'],
                        quantity__gt=0
                    ).select_related('medicine').values('medicine__name')[:5]
                    
                    available_medicines = [
                        {
                            'name': item['medicine__name']
                        }
                        for item in inventory_items
                    ]
                    
                    # Check if specific medicine is available
                    medicine_available = False
                    if medicine_name:
                        medicine_available = Inventory.objects.filter(
                            pharmacy_id=pharmacy['id'],
                            medicine__name__icontains=medicine_name,
                            quantity__gt=0
                        ).exists()
                    
                    pharmacy_list.append({
                        'id': pharmacy['id'],
                        'name': pharmacy['name'],
                        'address': pharmacy['address'],
                        'city': pharmacy['city'],
                        'phone': pharmacy['phone'],
                        'latitude': pharmacy['latitude'],
                        'longitude': pharmacy['longitude'],
                        'rating': pharmacy['rating'],
                        'distance': round(distance, 2),
                        'medicine_available': medicine_available,
                        'available_medicines': available_medicines,
                    })
            
            # Sort by requested criteria
            if sort_by == 'rating':
                pharmacy_list.sort(key=lambda x: (-x['rating'], x['distance']))
            elif sort_by == 'available':
                pharmacy_list.sort(key=lambda x: (-x['medicine_available'], -x['rating'], x['distance']))
            else:  # default: distance
                pharmacy_list.sort(key=lambda x: x['distance'])
            
            return JsonResponse({
                'success': True,
                'total': len(pharmacy_list),
                'medicine': medicine_name,
                'sort_by': sort_by,
                'pharmacies': pharmacy_list[:20]  # Return top 20
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'pharmacies': []
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Only GET requests are supported',
        'pharmacies': []
    }, status=405)


@csrf_exempt
def search_medicines(request):
    """
    Search for a specific medicine and find all pharmacies carrying it
    GET /api/search-medicines/?medicine=paracetamol&lat=18.5&lon=73.8&radius=10&sort=rating
    sort options: rating, distance
    """
    if request.method == 'GET':
        try:
            import math
            
            medicine_name = request.GET.get('medicine', '').strip()
            lat = float(request.GET.get('lat', 0)) if request.GET.get('lat') else None
            lon = float(request.GET.get('lon', 0)) if request.GET.get('lon') else None
            radius = float(request.GET.get('radius', 10))  # km
            sort_by = request.GET.get('sort', 'distance')  # price, distance, rating, quantity
            
            if not medicine_name:
                return JsonResponse({
                    'success': False,
                    'error': 'Medicine name is required',
                    'pharmacies': []
                }, status=400)
            
            # Search for medicine
            medicines = Medicine.objects.filter(
                name__icontains=medicine_name
            ).values_list('id', flat=True)
            
            if not medicines:
                return JsonResponse({
                    'success': True,
                    'total': 0,
                    'medicine': medicine_name,
                    'pharmacies': []
                })
            
            # Find all pharmacies carrying these medicines
            inventory = Inventory.objects.filter(
                medicine_id__in=medicines,
                quantity__gt=0
            ).select_related('pharmacy', 'medicine').values(
                'pharmacy__id', 'pharmacy__name', 'pharmacy__address', 'pharmacy__city',
                'pharmacy__phone', 'pharmacy__latitude', 'pharmacy__longitude', 'pharmacy__rating',
                'medicine__name'
            )
            
            # Group by pharmacy to avoid duplicates
            pharmacy_dict = {}
            for item in inventory:
                pharm_id = item['pharmacy__id']
                if pharm_id not in pharmacy_dict:
                    pharmacy_dict[pharm_id] = {
                        'id': item['pharmacy__id'],
                        'name': item['pharmacy__name'],
                        'address': item['pharmacy__address'],
                        'city': item['pharmacy__city'],
                        'phone': item['pharmacy__phone'],
                        'latitude': item['pharmacy__latitude'],
                        'longitude': item['pharmacy__longitude'],
                        'rating': item['pharmacy__rating'],
                        'medicine_available': True,
                        'available_medicines': [],
                    }
                
                pharmacy_dict[pharm_id]['available_medicines'].append({
                    'name': item['medicine__name']
                })
            
            results = list(pharmacy_dict.values())
            
            # Calculate distances if coordinates provided
            if lat and lon:
                for pharmacy in results:
                    dlat = math.radians(pharmacy['latitude'] - lat)
                    dlon = math.radians(pharmacy['longitude'] - lon)
                    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(pharmacy['latitude'])) * math.sin(dlon/2)**2
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                    distance = 6371 * c  # km
                    pharmacy['distance'] = round(distance, 2)
            
            # Filter by radius if coordinates provided
            if lat and lon:
                results = [p for p in results if p.get('distance', float('inf')) <= radius]
            
            # Sort results
            if sort_by == 'rating':
                results.sort(key=lambda x: (-x['rating'], x.get('distance', float('inf'))))
            else:  # default: distance
                if lat and lon:
                    results.sort(key=lambda x: x.get('distance', float('inf')))
            
            return JsonResponse({
                'success': True,
                'total': len(results),
                'medicine': medicine_name,
                'sort_by': sort_by,
                'pharmacies': results[:20]  # Return top 20 with 'pharmacies' key
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'pharmacies': []
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Only GET requests are supported',
        'pharmacies': []
    }, status=405)


@csrf_exempt
def search_by_city(request):
    """
    Search for all pharmacies in a city, optionally filtered by medicine
    GET /api/search-by-city/?city=mumbai&sort=rating
    GET /api/search-by-city/?city=mumbai&medicine=paracetamol&sort=rating
    sort options: rating (desc), name, distance
    """
    if request.method == 'GET':
        try:
            city_name = request.GET.get('city', '').strip()
            medicine_name = request.GET.get('medicine', '').strip()
            sort_by = request.GET.get('sort', 'rating')  # rating, name, distance
            
            if not city_name:
                return JsonResponse({
                    'success': False,
                    'error': 'City name is required',
                    'pharmacies': []
                }, status=400)
            
            # If medicine is provided, filter pharmacies that have this medicine
            if medicine_name:
                # Find medicine IDs that match the search
                medicines = Medicine.objects.filter(
                    name__icontains=medicine_name
                ).values_list('id', flat=True)
                
                if not medicines:
                    return JsonResponse({
                        'success': True,
                        'total': 0,
                        'city': city_name,
                        'medicine': medicine_name,
                        'pharmacies': [],
                        'message': f'No pharmacies in {city_name} have {medicine_name}'
                    })
                
                # Find pharmacies in city that have this medicine
                pharmacy_ids = Inventory.objects.filter(
                    medicine_id__in=medicines,
                    quantity__gt=0,
                    pharmacy__city__iexact=city_name
                ).values_list('pharmacy_id', flat=True).distinct()
                
                pharmacies = Pharmacy.objects.filter(
                    id__in=pharmacy_ids
                ).values(
                    'id', 'name', 'address', 'city', 'phone', 'latitude', 
                    'longitude', 'rating'
                )
            else:
                # Search for all pharmacies in the city (exact match, case-insensitive)
                pharmacies = Pharmacy.objects.filter(
                    city__iexact=city_name
                ).values(
                    'id', 'name', 'address', 'city', 'phone', 'latitude', 
                    'longitude', 'rating'
                )
            
            if not pharmacies:
                message = f'No pharmacies found in {city_name}'
                if medicine_name:
                    message = f'No pharmacies in {city_name} have {medicine_name}'
                return JsonResponse({
                    'success': True,
                    'total': 0,
                    'city': city_name,
                    'medicine': medicine_name if medicine_name else None,
                    'pharmacies': [],
                    'message': message
                })
            
            # Convert to list and build response
            results = []
            for pharm in pharmacies:
                # Get available medicines for this pharmacy
                inventory_filter = Inventory.objects.filter(
                    pharmacy_id=pharm['id'],
                    quantity__gt=0
                ).select_related('medicine')
                
                # If searching for specific medicine, mark if this pharmacy has it
                medicine_available = False
                if medicine_name:
                    inventory_filter = inventory_filter.filter(medicine_id__in=medicines)
                    medicine_available = inventory_filter.exists()
                
                # Get medicine names
                inventory_items = inventory_filter.select_related('medicine')[:10]
                available_medicines = [
                    {'name': item.medicine.name}
                    for item in inventory_items
                ]
                
                results.append({
                    'id': pharm['id'],
                    'name': pharm['name'],
                    'address': pharm['address'],
                    'city': pharm['city'],
                    'phone': pharm['phone'],
                    'latitude': pharm['latitude'],
                    'longitude': pharm['longitude'],
                    'rating': pharm['rating'],
                    'medicine_available': medicine_available if medicine_name else True,
                    'total_medicines': len(available_medicines),
                    'available_medicines': available_medicines
                })
            
            # Sort results
            if sort_by == 'rating':
                results.sort(key=lambda x: (-x['rating'], x['name']))  # Highest rating first, then by name
            elif sort_by == 'name':
                results.sort(key=lambda x: x['name'])
            elif sort_by == 'distance':
                # User can pass lat/lon to calculate distance
                lat = request.GET.get('lat')
                lon = request.GET.get('lon')
                if lat and lon:
                    import math
                    lat, lon = float(lat), float(lon)
                    for pharm in results:
                        dlat = math.radians(pharm['latitude'] - lat)
                        dlon = math.radians(pharm['longitude'] - lon)
                        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(pharm['latitude'])) * math.sin(dlon/2)**2
                        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                        distance = 6371 * c  # km
                        pharm['distance'] = round(distance, 2)
                    results.sort(key=lambda x: x.get('distance', float('inf')))
            
            return JsonResponse({
                'success': True,
                'total': len(results),
                'city': city_name,
                'medicine': medicine_name if medicine_name else None,
                'sort_by': sort_by,
                'pharmacies': results
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'pharmacies': []
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Only GET requests are supported',
        'pharmacies': []
    }, status=405)


@csrf_exempt
def get_medicine_list(request):
    """
    Get list of all medicines for autocomplete
    GET /api/get-medicines/?search=para&limit=10
    """
    if request.method == 'GET':
        try:
            search_term = request.GET.get('search', '').strip()
            limit = int(request.GET.get('limit', 20))
            
            if len(search_term) < 2:
                return JsonResponse({
                    'success': False,
                    'medicines': [],
                    'message': 'Search term must be at least 2 characters'
                })
            
            medicines = Medicine.objects.filter(
                name__icontains=search_term
            ).values('id', 'name', 'category').distinct()[:limit]
            
            medicine_list = [
                {
                    'id': med['id'],
                    'name': med['name'],
                    'category': med['category']
                }
                for med in medicines
            ]
            
            return JsonResponse({
                'success': True,
                'total': len(medicine_list),
                'medicines': medicine_list
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'medicines': []
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Only GET requests are supported',
        'medicines': []
    }, status=405)


@csrf_exempt
def get_medicine_detail(request, medicine_id):
    """
    Get detailed information about a medicine
    GET /api/medicine-detail/<id>/
    """
    if request.method == 'GET':
        try:
            medicine = Medicine.objects.filter(id=medicine_id).values(
                'id', 'name', 'generic_name', 'category', 'common_doses', 'description'
            ).first()
            
            if not medicine:
                return JsonResponse({
                    'success': False,
                    'error': 'Medicine not found'
                }, status=404)
            
            # Get count of pharmacies carrying this medicine
            pharmacy_count = Inventory.objects.filter(
                medicine_id=medicine_id,
                quantity__gt=0
            ).distinct('pharmacy').count()
            
            # Get average price and availability
            inventory_stats = Inventory.objects.filter(
                medicine_id=medicine_id,
                quantity__gt=0
            ).aggregate(
                avg_price=__import__('django.db.models', fromlist=['Avg']).Avg('price'),
                min_price=__import__('django.db.models', fromlist=['Min']).Min('price'),
                max_price=__import__('django.db.models', fromlist=['Max']).Max('price'),
            )
            
            return JsonResponse({
                'success': True,
                'medicine': {
                    'id': medicine['id'],
                    'name': medicine['name'],
                    'generic_name': medicine['generic_name'],
                    'category': medicine['category'],
                    'dosage': medicine['common_doses'],
                    'description': medicine['description'],
                    'available_in_pharmacies': pharmacy_count,
                    'price_range': {
                        'min': float(inventory_stats['min_price'] or 0),
                        'max': float(inventory_stats['max_price'] or 0),
                        'average': float(inventory_stats['avg_price'] or 0)
                    }
                }
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Only GET requests are supported'
    }, status=405)


@csrf_exempt
def get_trending_medicines(request):
    """
    Get trending/most searched medicines
    GET /api/trending-medicines/?limit=10
    """
    if request.method == 'GET':
        try:
            import math
            from django.db.models import Count, Avg, Min, Max
            
            limit = int(request.GET.get('limit', 10))
            
            # Get medicines with inventory in most pharmacies
            popular_medicines = Inventory.objects.filter(
                quantity__gt=0
            ).values('medicine__name', 'medicine__id', 'medicine__category').annotate(
                pharmacy_count=Count('pharmacy', distinct=True),
                avg_price=Avg('price'),
                min_price=Min('price'),
                max_price=Max('price')
            ).order_by('-pharmacy_count')[:limit]
            
            medicines_list = []
            for med in popular_medicines:
                medicines_list.append({
                    'id': med['medicine__id'],
                    'name': med['medicine__name'],
                    'category': med['medicine__category'],
                    'available_in': med['pharmacy_count'],
                    'avg_price': float(med['avg_price'] or 0),
                    'min_price': float(med['min_price'] or 0),
                    'max_price': float(med['max_price'] or 0)
                })
            
            return JsonResponse({
                'success': True,
                'total': len(medicines_list),
                'trending_medicines': medicines_list
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'trending_medicines': []
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Only GET requests are supported',
        'trending_medicines': []
    }, status=405)


@csrf_exempt
def search_all_pharmacies(request):
    """
    Get all pharmacies sorted by distance or rating
    GET /api/all-pharmacies/?lat=18.5&lon=73.8&radius=10&sort=distance&city=Pune
    Returns all pharmacies without filtering by medicine
    """
    if request.method == 'GET':
        try:
            import math
            
            # Get parameters
            lat = float(request.GET.get('lat', 0))
            lon = float(request.GET.get('lon', 0))
            radius = float(request.GET.get('radius', 10))
            sort_by = request.GET.get('sort', 'distance')  # distance, rating
            city_filter = request.GET.get('city', '')
            
            # Get all pharmacies or filtered by city
            if city_filter:
                pharmacies = Pharmacy.objects.filter(city__icontains=city_filter)
            else:
                pharmacies = Pharmacy.objects.all()
            
            results = []
            
            # Calculate distance for each pharmacy
            for pharmacy in pharmacies:
                # Haversine formula to calculate distance
                def haversine(lat1, lon1, lat2, lon2):
                    R = 6371  # Earth's radius in km
                    phi1 = math.radians(lat1)
                    phi2 = math.radians(lat2)
                    delta_phi = math.radians(lat2 - lat1)
                    delta_lambda = math.radians(lon2 - lon1)
                    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
                    c = 2 * math.asin(math.sqrt(a))
                    return R * c
                
                if lat != 0 and lon != 0:
                    distance = haversine(lat, lon, float(pharmacy.latitude), float(pharmacy.longitude))
                else:
                    distance = 0
                
                # Filter by radius if location is provided
                if lat != 0 and lon != 0 and distance > radius:
                    continue
                
                # Get available medicines count
                available_medicines_count = Inventory.objects.filter(
                    pharmacy=pharmacy,
                    quantity__gt=0
                ).count()
                
                results.append({
                    'id': pharmacy.id,
                    'name': pharmacy.name,
                    'address': pharmacy.address,
                    'city': pharmacy.city,
                    'phone': pharmacy.phone,
                    'latitude': float(pharmacy.latitude),
                    'longitude': float(pharmacy.longitude),
                    'rating': float(pharmacy.rating),
                    'distance': round(distance, 2),
                    'medicines_count': available_medicines_count
                })
            
            # Sort results
            if sort_by == 'rating':
                results.sort(key=lambda x: x['rating'], reverse=True)
            elif sort_by == 'medicines':
                results.sort(key=lambda x: x['medicines_count'], reverse=True)
            else:  # default: distance
                results.sort(key=lambda x: x['distance'])
            
            return JsonResponse({
                'success': True,
                'total': len(results),
                'sort_by': sort_by,
                'radius': radius,
                'pharmacies': results
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Only GET requests are supported'
    }, status=405)


@csrf_exempt
def search_all_medicines(request):
    """
    Get all medicines with optional filtering
    GET /api/all-medicines/?search=para&category=antipyretic&limit=100&offset=0
    Returns all medicines or filtered by category
    """
    if request.method == 'GET':
        try:
            search = request.GET.get('search', '')
            category = request.GET.get('category', '')
            limit = int(request.GET.get('limit', 50))
            offset = int(request.GET.get('offset', 0))
            
            # Get medicines
            medicines_query = Medicine.objects.all()
            
            # Filter by search term
            if search:
                medicines_query = medicines_query.filter(
                    name__icontains=search
                ) | medicines_query.filter(
                    generic_name__icontains=search
                )
            
            # Filter by category
            if category:
                medicines_query = medicines_query.filter(category__icontains=category)
            
            total_count = medicines_query.count()
            
            # Apply pagination
            medicines = medicines_query[offset:offset + limit]
            
            medicines_list = []
            for med in medicines:
                medicines_list.append({
                    'id': med.id,
                    'name': med.name,
                    'generic_name': med.generic_name,
                    'category': med.category,
                    'dosage': med.common_doses,
                    'description': med.description
                })
            
            return JsonResponse({
                'success': True,
                'total': total_count,
                'returned': len(medicines_list),
                'offset': offset,
                'limit': limit,
                'medicines': medicines_list
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Only GET requests are supported'
    }, status=405)


@csrf_exempt
def search_locations_list(request):
    """
    Get all available cities/locations in database
    GET /api/locations-list/?search=pune
    Returns list of all cities where pharmacies are located
    """
    if request.method == 'GET':
        try:
            search = request.GET.get('search', '')
            
            # Get unique cities
            if search:
                cities = Pharmacy.objects.filter(
                    city__icontains=search
                ).values_list('city', flat=True).distinct().order_by('city')
            else:
                cities = Pharmacy.objects.values_list('city', flat=True).distinct().order_by('city')
            
            return JsonResponse({
                'success': True,
                'total': len(list(cities)),
                'locations': list(cities)
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Only GET requests are supported'
    }, status=405)


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in kilometers
    """
    import math
    R = 6371  # Earth's radius in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


def geocode_address(address_string):
    """
    Convert address string to coordinates using Nominatim API
    Returns tuple (latitude, longitude) or (None, None) if failed
    """
    try:
        geolocator = Nominatim(user_agent="medilocator_app")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        location = geocode(address_string, timeout=10)
        
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        print(f"Geocoding error: {str(e)}")
        return None, None


@csrf_exempt
def search_manual(request):
    """
    Manual pharmacy search by medicine name and location
    POST /api/search-manual/
    
    Request body:
    {
        "medicine_name": "Paracetamol",
        "address": "123 Main St, Mumbai 400001",
        "radius": 10
    }
    
    Returns:
    {
        "success": true,
        "latitude": 19.0760,
        "longitude": 72.8777,
        "message": "Location coordinates found"
    }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            medicine_name = data.get('medicine_name', '').strip()
            address = data.get('address', '').strip()
            radius = int(data.get('radius', 10))
            city = data.get('city', '').strip()  # Add city parameter
            
            if not medicine_name:
                return JsonResponse({
                    'success': False,
                    'error': 'Medicine name is required'
                }, status=400)
            
            if not address:
                return JsonResponse({
                    'success': False,
                    'error': 'Address is required'
                }, status=400)
            
            # Geocode the address
            lat, lon = geocode_address(address)
            
            if lat is None or lon is None:
                return JsonResponse({
                    'success': False,
                    'error': f'Could not find location for address: {address}. Please check the address and try again.'
                }, status=400)
            
            # Log the search
            SearchLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                medicines=[medicine_name],
                latitude=lat,
                longitude=lon,
                results_count=0
            )
            
            return JsonResponse({
                'success': True,
                'latitude': lat,
                'longitude': lon,
                'message': 'Location coordinates found'
            })
        
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Only POST requests are supported'
    }, status=405)


@csrf_exempt
def search_gps(request):
    """
    GPS-based pharmacy search by medicine name and GPS coordinates
    POST /api/search-gps/
    
    Request body:
    {
        "medicine_name": "Paracetamol",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "radius": 10
    }
    
    Returns:
    {
        "success": true,
        "pharmacies": [
            {
                "id": 1,
                "name": "Apollo Pharmacy",
                "address": "123 Main St",
                "city": "Mumbai",
                "phone": "9876543210",
                "latitude": 19.0761,
                "longitude": 72.8778,
                "rating": 4.5,
                "distance": 0.15,
                "medicine_available": true,
                "available_medicines": [
                    {
                        "name": "Paracetamol"
                    }
                ]
            }
        ]
    }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            medicine_name = data.get('medicine_name', '').strip()
            latitude = float(data.get('latitude', 0))
            longitude = float(data.get('longitude', 0))
            radius = int(data.get('radius', 10))
            city = data.get('city', '').strip()  # Add city parameter
            
            if not medicine_name:
                return JsonResponse({
                    'success': False,
                    'error': 'Medicine name is required',
                    'pharmacies': []
                }, status=400)
            
            if latitude == 0 or longitude == 0:
                return JsonResponse({
                    'success': False,
                    'error': 'Valid latitude and longitude are required',
                    'pharmacies': []
                }, status=400)
            
            # Search for medicine
            medicines = Medicine.objects.filter(
                name__icontains=medicine_name
            ).values_list('id', flat=True)
            
            if not medicines:
                return JsonResponse({
                    'success': True,
                    'total': 0,
                    'medicine': medicine_name,
                    'pharmacies': [],
                    'message': f'No pharmacies found with medicine: {medicine_name}'
                })
            
            # Find all pharmacies carrying these medicines
            inventory_filter = Inventory.objects.filter(
                medicine_id__in=medicines,
                quantity__gt=0,
                pharmacy__verified=True
            )
            
            # If city is provided, filter by city
            if city:
                inventory_filter = inventory_filter.filter(pharmacy__city__iexact=city)
            
            inventory = inventory_filter.select_related('pharmacy', 'medicine').values(
                'pharmacy__id', 'pharmacy__name', 'pharmacy__address', 'pharmacy__city',
                'pharmacy__phone', 'pharmacy__latitude', 'pharmacy__longitude', 'pharmacy__rating',
                'medicine__name'
            )
            
            # Group by pharmacy
            pharmacy_dict = {}
            for item in inventory:
                pharm_id = item['pharmacy__id']
                if pharm_id not in pharmacy_dict:
                    pharmacy_dict[pharm_id] = {
                        'id': item['pharmacy__id'],
                        'name': item['pharmacy__name'],
                        'address': item['pharmacy__address'],
                        'city': item['pharmacy__city'],
                        'phone': item['pharmacy__phone'],
                        'latitude': float(item['pharmacy__latitude']),
                        'longitude': float(item['pharmacy__longitude']),
                        'rating': float(item['pharmacy__rating']),
                        'medicine_available': True,
                        'available_medicines': [],
                    }
                
                pharmacy_dict[pharm_id]['available_medicines'].append({
                    'name': item['medicine__name']
                })
            
            results = list(pharmacy_dict.values())
            
            # Calculate distances and filter by radius
            final_results = []
            for pharmacy in results:
                distance = haversine_distance(
                    latitude, longitude,
                    pharmacy['latitude'], pharmacy['longitude']
                )
                
                if distance <= radius:
                    pharmacy['distance'] = round(distance, 2)
                    final_results.append(pharmacy)
            
            # Sort by: medicine availability (always true), then distance, then rating
            final_results.sort(key=lambda x: (x['distance'], -x['rating']))
            
            # Log the search
            SearchLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                medicines=[medicine_name],
                latitude=latitude,
                longitude=longitude,
                results_count=len(final_results)
            )
            
            return JsonResponse({
                'success': True,
                'total': len(final_results),
                'medicine': medicine_name,
                'radius': radius,
                'pharmacies': final_results[:50]  # Return top 50
            })
        
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON in request body',
                'pharmacies': []
            }, status=400)
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid data type: {str(e)}',
                'pharmacies': []
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'pharmacies': []
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Only POST requests are supported',
        'pharmacies': []
    }, status=405)




