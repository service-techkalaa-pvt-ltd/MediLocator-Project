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
from .forms import CreateUserForm, FeedbackForm, PharmacyRegistrationForm
import joblib
from django.http import JsonResponse
import difflib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
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
    """Display search results page with pharmacy results for medicines"""
    from math import radians, cos, sin, asin, sqrt
    
    # Get parameters from URL
    medicines_param = request.GET.get('medicines', '')
    latitude = request.GET.get('lat')
    longitude = request.GET.get('lon')
    
    # Parse medicine names
    medicine_names = [m.strip() for m in medicines_param.split(',') if m.strip()] if medicines_param else []
    
    context = {
        'medicines': medicine_names,
        'pharmacies': [],
        'has_location': False,
        'total_medicines': len(medicine_names),
        'total_pharmacies': 0
    }
    
    if not medicine_names:
        # No medicines provided, show empty state
        return render(request, 'accounts/search_results.html', context)
    
    # Check location
    has_location = bool(latitude and longitude)
    if has_location:
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            context['has_location'] = True
            context['user_lat'] = latitude
            context['user_lon'] = longitude
        except (ValueError, TypeError):
            has_location = False
    
    # Haversine distance function
    def haversine(lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        return round(km, 2)
    
    # Search for medicines in database with fuzzy matching
    medicines_found = []
    medicine_ids = []
    
    # Get all medicines for fuzzy matching
    from rapidfuzz import fuzz, process
    all_medicines = {m.name: m for m in Medicine.objects.all()}
    
    for med_name in medicine_names:
        # Try exact match first
        try:
            medicine = Medicine.objects.get(name__iexact=med_name)
            if medicine.id not in medicine_ids:
                medicine_ids.append(medicine.id)
                medicines_found.append({
                    'name': medicine.name,
                    'generic_name': medicine.generic_name,
                    'searched_for': med_name
                })
                continue
        except Medicine.DoesNotExist:
            pass
        
        # Try fuzzy matching (70%+ similarity - lowered for better brand name matching)
        fuzzy_matches = process.extract(
            med_name, 
            all_medicines.keys(), 
            scorer=fuzz.ratio,
            limit=5
        )
        
        # Also try fuzzy matching on generic names
        generic_names = {m.generic_name: m for m in Medicine.objects.all() if m.generic_name}
        generic_fuzzy = process.extract(
            med_name,
            generic_names.keys(),
            scorer=fuzz.ratio,
            limit=5
        )
        
        # Combine matches from both name and generic name
        all_fuzzy_matches = list(fuzzy_matches) + [(name, score, idx) for name, score, idx in generic_fuzzy]
        all_fuzzy_matches.sort(key=lambda x: x[1], reverse=True)  # Sort by score
        
        for match_name, score, _ in all_fuzzy_matches[:5]:
            if score >= 70:  # 70% or higher similarity (lowered from 80%)
                # Get medicine from either dict
                medicine = all_medicines.get(match_name) or generic_names.get(match_name)
                if medicine and medicine.id not in medicine_ids:
                    medicine_ids.append(medicine.id)
                    medicines_found.append({
                        'name': medicine.name,
                        'generic_name': medicine.generic_name,
                        'searched_for': med_name,
                        'match_score': score
                    })
        
        # If still no match, try partial contains on both name and generic name
        if not any(m['searched_for'] == med_name for m in medicines_found):
            matches = Medicine.objects.filter(
                models.Q(name__icontains=med_name) |
                models.Q(generic_name__icontains=med_name)
            )[:3]
            for medicine in matches:
                if medicine.id not in medicine_ids:
                    medicine_ids.append(medicine.id)
                    medicines_found.append({
                        'name': medicine.name,
                        'generic_name': medicine.generic_name,
                        'searched_for': med_name,
                        'match_score': 60
                    })
    
    context['medicines_found'] = medicines_found
    
    if not medicine_ids:
        # No medicines found in database
        return render(request, 'accounts/search_results.html', context)
    
    # Find pharmacies with these medicines
    inventory_items = Inventory.objects.filter(
        medicine_id__in=medicine_ids,
        quantity__gt=0
    ).select_related('pharmacy', 'medicine')
    
    # Group by pharmacy
    pharmacy_dict = {}
    for item in inventory_items:
        pharmacy_id = item.pharmacy.id
        
        if pharmacy_id not in pharmacy_dict:
            pharmacy_dict[pharmacy_id] = {
                'pharmacy': item.pharmacy,
                'medicines': [],
                'distance': None
            }
        
        pharmacy_dict[pharmacy_id]['medicines'].append({
            'name': item.medicine.name,
            'generic_name': item.medicine.generic_name,
            'price': float(item.price),
            'quantity': item.quantity
        })
    
    # Calculate distances if location available
    if has_location:
        for pharmacy_id, data in pharmacy_dict.items():
            pharmacy = data['pharmacy']
            if pharmacy.latitude and pharmacy.longitude:
                distance = haversine(
                    longitude, latitude,
                    pharmacy.longitude, pharmacy.latitude
                )
                data['distance'] = distance
    
    # Sort pharmacies
    pharmacy_list = list(pharmacy_dict.values())
    
    if has_location:
        # Sort by distance (nearest first)
        pharmacy_list.sort(key=lambda x: x['distance'] if x['distance'] is not None else float('inf'))
    else:
        # Sort by rating
        pharmacy_list.sort(key=lambda x: x['pharmacy'].rating if x['pharmacy'].rating else 0, reverse=True)
    
    context['pharmacies'] = pharmacy_list
    context['total_pharmacies'] = len(pharmacy_list)
    
    return render(request, 'accounts/search_results.html', context)


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
    """Enhanced chatbot with automatic medicine search capability"""
    if request.method == "POST":
        try:
            import math
            import uuid
            
            data = json.loads(request.body)
            user_message = data.get("user_message", "").strip()
            message_lower = user_message.lower()
            user_lat = data.get("latitude")
            user_lon = data.get("longitude")
            session_id = data.get("session_id", str(uuid.uuid4()))

            # Get or create conversation session
            conversation = None
            if request.user.is_authenticated:
                conversation, created = ChatbotConversation.objects.get_or_create(
                    session_id=session_id,
                    defaults={'user': request.user}
                )
            
            # Save user message
            if conversation:
                conversation.add_message('user', user_message)
                conversation.save()

            # Expanded FAQ responses
            faq_responses = {
                # Greetings
                "hello": "Hello! 👋 Welcome to MediLocate. I'm here to help you with:<br>• Finding medicines and pharmacies<br>• Uploading prescriptions<br>• Answering health questions<br><br>What can I help you with today?",
                "hi": "Hi there! 😊 How can I assist you today? Try asking about medicines, pharmacies, or our services!",
                "hey": "Hey! Welcome to MediBot. What would you like to know?",
                "good morning": "Good morning! ☀️ How can I help you today?",
                "good afternoon": "Good afternoon! How may I assist you?",
                "good evening": "Good evening! 🌙 What can I do for you today?",
                
                # Goodbyes
                "bye": "Goodbye! 👋 Stay healthy and take care!",
                "goodbye": "Thank you for using MediLocate! Feel free to come back anytime. Stay healthy! 💚",
                "see you": "See you soon! Take care of your health! 😊",
                
                # Services & Help
                "services": "🏥 <strong>Our Services:</strong><br>1. 💊 <strong>Medicine Search</strong> - Find medicines and check availability<br>2. 📍 <strong>Pharmacy Locator</strong> - Find nearby pharmacies with your medicines<br>3. 📋 <strong>Prescription Upload</strong> - Upload and analyze prescriptions<br>4. 🤖 <strong>AI Health Assistant</strong> - Get answers to health questions<br><br>What would you like to try?",
                "help": "🆘 <strong>How I Can Help:</strong><br>• Search for any medicine by name<br>• Find pharmacies near you<br>• Answer questions about our services<br>• Guide you through prescription upload<br>• Provide health information<br><br>Just type your question or medicine name!",
                "what can you do": "I can help you:<br>✓ Find medicines and their availability<br>✓ Locate nearby pharmacies<br>✓ Upload prescriptions<br>✓ Answer questions about medicines and health<br><br>Try asking me anything!",
                
                # Prescription Upload FAQs
                "how do i upload my prescription": "📋 <strong>To Upload Your Prescription:</strong><br>1. Click on the '<strong>Upload Prescription</strong>' button in the menu<br>2. Take a clear photo of your prescription or select an existing image<br>3. Upload the image - our AI will analyze it<br>4. We'll extract medicine names and help you find nearby pharmacies<br><br>Need more help? Just ask!",
                "upload prescription": "You can upload prescriptions by clicking the 'Upload Prescription' button on our homepage or in the main menu. Our AI will scan and extract medicine names for you! 📸",
                "prescription upload": "To upload a prescription, go to the main menu and select 'Upload Prescription'. Make sure the image is clear and readable! 📋",
                "how to upload": "Click on 'Upload Prescription' from the menu, then select or capture an image of your prescription. Our system will process it automatically! ✨",
                
                # Medicine Search FAQs
                "how do i search for medicines": "🔍 <strong>Searching for Medicines:</strong><br>1. Simply type the medicine name (e.g., 'Paracetamol')<br>2. You can also search by generic name<br>3. I'll show you pharmacies that have it in stock<br>4. If I have your location, I'll sort by nearest pharmacies<br><br>Try searching now!",
                "how to search": "Just type any medicine name and I'll find it for you! Example: Try typing 'Aspirin' or 'Crocin'. 🔍",
                "search medicines": "Type any medicine name directly in the chat, and I'll search for pharmacies that have it in stock! 💊",
                
                # Pharmacy Locator FAQs  
                "find pharmacies near me": "📍 <strong>Finding Nearby Pharmacies:</strong><br>1. Share your location when prompted<br>2. Search for a medicine<br>3. I'll show pharmacies sorted by distance<br>4. View pharmacy details, ratings, and contact info<br><br>You can also browse all pharmacies without searching for a specific medicine!",
                "find pharmacies": "To find pharmacies, either search for a medicine or click 'Find Pharmacies' in the menu. Enable location access for best results! 📍",
                "nearby pharmacies": "I can show you nearby pharmacies! Just allow location access and search for a medicine, or browse all pharmacies in your area. 🏥",
                "pharmacies near me": "Enable location sharing and I'll find the closest pharmacies to you with their ratings, contact details, and available medicines! 📍",
                
                # Login/Account FAQs
                "help me with login": "🔐 <strong>Login Help:</strong><br>• Click '<strong>Login</strong>' in the top menu<br>• Enter your email and password<br>• Forgot password? Click 'Reset Password'<br>• Don't have an account? Click 'Register' to create one<br><br>Need specific help? Let me know!",
                "how to login": "Click the 'Login' button in the top-right corner, then enter your credentials. New user? You can register for free! 🔑",
                "login help": "For login issues: Check your email/password, clear browser cache, or use 'Forgot Password' to reset. Still stuck? Contact support! 💁",
                "register": "To create an account, click 'Register' in the menu, fill in your details (name, email, password), and submit! It's free and quick! ✅",
                "create account": "Click 'Register' in the top menu to create your free account. You'll need an email address and password. Simple! 📝",
                
                # About/General
                "what is medilocate": "MediLocate is your intelligent medicine and pharmacy finder! We help you locate medicines, find nearby pharmacies, and manage your prescriptions with AI assistance. 🏥💊",
                "about": "MediLocate helps you find medicines and pharmacies quickly. We use AI to make healthcare more accessible! 🚀",
                "who are you": "I'm MediBot, your AI health assistant! I help you find medicines, locate pharmacies, and answer health-related questions. 🤖💙",
                "thank you": "You're welcome! 😊 Feel free to ask anything else!",
                "thanks": "Happy to help! If you need anything else, just ask! 💚"
            }
            
            disease_links = {
                "diabetes": "Watch this YouTube video for more details: https://www.youtube.com/embed/-uK8a80vyeI",
                "hypertension": "Watch this video: https://www.youtube.com/embed/TjzwohzLJgA",
                "malaria": "Check this link: https://www.youtube.com/embed/zWf5ZaCo0BI",
                "heart disease": "Watch this: https://www.youtube.com/embed/SFWvoNZtUkk",
                "normal health": "Healthy living tips here: https://www.youtube.com/embed/PG2f3GF5RlI"
            }

            # Check for FAQ responses first
            if message_lower in faq_responses:
                bot_reply = faq_responses[message_lower]
                if conversation:
                    conversation.add_message('bot', bot_reply)
                    conversation.save()
                return JsonResponse({
                    "type": "text",
                    "bot_reply": bot_reply,
                    "session_id": session_id
                })
            
            # Check for partial matches in FAQs (more flexible matching)
            for key, response in faq_responses.items():
                if key in message_lower or message_lower in key:
                    bot_reply = response
                    if conversation:
                        conversation.add_message('bot', bot_reply)
                        conversation.save()
                    return JsonResponse({
                        "type": "text",
                        "bot_reply": bot_reply,
                        "session_id": session_id
                    })
            
            if message_lower in disease_links:
                bot_reply = f'<a href="{disease_links[message_lower]}" target="_blank">Click here to watch the video about {user_message}</a>'
                if conversation:
                    conversation.add_message('bot', bot_reply)
                    conversation.save()
                return JsonResponse({
                    "type": "text",
                    "bot_reply": bot_reply,
                    "session_id": session_id
                })

            # Detect if this is likely a question vs a medicine search
            question_indicators = [
                'how', 'what', 'where', 'when', 'why', 'who', 'can', 'do', 'does', 
                'is', 'are', 'should', 'could', 'would', 'help', 'explain', 'tell me',
                '?', 'which', 'will'
            ]
            
            is_question = any(indicator in message_lower for indicator in question_indicators)
            
            # If it's a question and we haven't answered it with FAQs, provide helpful response
            if is_question and len(user_message.split()) > 2:
                bot_reply = "Thank you for asking! 😊<br><br>I'm here to help with:<br>• Finding medicines and pharmacies<br>• Prescription uploads<br>• General health information<br><br>However, I don't have specific information about your question right now. Please try:<br>• Rephrasing your question<br>• Asking about our services (type 'help')<br>• Searching for a medicine name<br><br>Or you can contact our support team for more assistance! 💁‍♀️"
                if conversation:
                    conversation.add_message('bot', bot_reply)
                    conversation.save()
                return JsonResponse({
                    "type": "text",
                    "bot_reply": bot_reply,
                    "session_id": session_id
                })

            # AUTO-DETECT MEDICINE SEARCH
            # Only search for medicine if it looks like a medicine query (not a question)
            medicine_keywords = ['find', 'search', 'locate', 'need', 'want', 'looking for', 'pharmacy', 'store', 'available', 'price', 'buy', 'get']
            is_medicine_query = any(keyword in message_lower for keyword in medicine_keywords) or (len(user_message.split()) <= 3 and not is_question)
            
            # Search for medicine in database
            medicines = Medicine.objects.filter(
                name__icontains=user_message
            ) | Medicine.objects.filter(
                generic_name__icontains=user_message
            )
            
            if medicines.exists():
                # Medicine found - search for pharmacies
                medicine_ids = list(medicines.values_list('id', flat=True))
                medicine_list = list(medicines.values('id', 'name', 'generic_name', 'category', 'common_doses', 'description')[:5])
                
                # Find pharmacies with this medicine
                inventory = Inventory.objects.filter(
                    medicine_id__in=medicine_ids,
                    quantity__gt=0
                ).select_related('pharmacy', 'medicine').values(
                    'pharmacy__id', 'pharmacy__name', 'pharmacy__address', 'pharmacy__city',
                    'pharmacy__phone', 'pharmacy__latitude', 'pharmacy__longitude', 
                    'pharmacy__rating', 'medicine__name', 'medicine__generic_name',
                    'price', 'quantity'
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
                            'latitude': item['pharmacy__latitude'],
                            'longitude': item['pharmacy__longitude'],
                            'rating': item['pharmacy__rating'],
                            'medicines': []
                        }
                    
                    pharmacy_dict[pharm_id]['medicines'].append({
                        'name': item['medicine__name'],
                        'generic_name': item['medicine__generic_name'],
                        'price': float(item['price']) if item['price'] else 0,
                        'quantity': item['quantity']
                    })
                
                pharmacy_list = list(pharmacy_dict.values())
                
                # Calculate distances if user location provided
                if user_lat and user_lon:
                    for pharmacy in pharmacy_list:
                        dlat = math.radians(pharmacy['latitude'] - float(user_lat))
                        dlon = math.radians(pharmacy['longitude'] - float(user_lon))
                        a = math.sin(dlat/2)**2 + math.cos(math.radians(float(user_lat))) * math.cos(math.radians(pharmacy['latitude'])) * math.sin(dlon/2)**2
                        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                        distance = 6371 * c
                        pharmacy['distance'] = round(distance, 2)
                    
                    # Sort by distance
                    pharmacy_list.sort(key=lambda x: x.get('distance', float('inf')))
                else:
                    # Sort by rating if no location
                    pharmacy_list.sort(key=lambda x: x['rating'], reverse=True)
                
                # Save search to conversation
                if conversation:
                    search_result = f"Found {len(pharmacy_list)} pharmacies with {medicine_list[0]['name']}"
                    conversation.add_message('bot', search_result)
                    conversation.save()
                
                # Return medicine search results
                return JsonResponse({
                    "type": "medicine_search",
                    "medicine_found": True,
                    "medicines": medicine_list,
                    "pharmacies": pharmacy_list[:15],  # Top 15 pharmacies
                    "total_pharmacies": len(pharmacy_list),
                    "has_location": bool(user_lat and user_lon),
                    "session_id": session_id
                })
            
            # No medicine found - provide helpful response
            if is_medicine_query:
                bot_reply = f"🔍 I couldn't find '<strong>{user_message}</strong>' in our medicine database.<br><br>💡 <strong>Suggestions:</strong><br>• Check the spelling<br>• Try the generic name (e.g., 'Acetaminophen' instead of brand names)<br>• Search for a similar medicine<br>• Use simpler terms<br><br>Or type '<strong>help</strong>' to see what I can do! 😊"
            else:
                bot_reply = "Thank you for your message! 😊<br><br>I'm currently designed to help with:<br>• 💊 Medicine searches<br>• 🏥 Finding pharmacies<br>• 📋 Prescription uploads<br>• ❓ General service questions<br><br>Unfortunately, I'm not able to answer that specific question right now. Please feel free to:<br>• Ask about our services (type 'services')<br>• Search for a medicine<br>• Contact our support team<br><br>Thank you for your understanding! 💚"
            
            if conversation:
                conversation.add_message('bot', bot_reply)
                conversation.save()
            
            return JsonResponse({
                "type": "text",
                "bot_reply": bot_reply,
                "session_id": session_id
            })
            
        except Exception as e:
            print(f"Chatbot error: {str(e)}")
            return JsonResponse({
                "type": "text",
                "bot_reply": "Sorry, I encountered an error. Please try again or rephrase your question."
            })

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
@login_required(login_url='login')
def user_profile(request):
    """User profile page with edit functionality"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        # Update user information
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Update profile information
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_profile')
    
    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'accounts/user_profile.html', context)


@login_required(login_url='login')
def prescription_scanner(request):
    """Prescription upload page"""
    return render(request, 'accounts/PrescriptionScanner.html')


@login_required(login_url='login')
def process_prescription(request):
    """
    Process uploaded prescription using OCR text extraction
    Extracts medicine names from image and finds nearby pharmacies with stock
    Simple OCR-based approach without ML models
    """
    if request.method == 'POST':
        try:
            from math import radians, cos, sin, asin, sqrt
            
            # Get uploaded file
            prescription_file = request.FILES.get('prescription_file')
            
            if not prescription_file:
                return JsonResponse({
                    'success': False,
                    'error': 'No file uploaded'
                }, status=400)
            
            # Validate file type
            allowed_extensions = ['jpg', 'jpeg', 'png']
            file_extension = prescription_file.name.split('.')[-1].lower()
            
            if file_extension not in allowed_extensions:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
                }, status=400)
            
            # Save uploaded file temporarily
            fs = FileSystemStorage()
            filename = fs.save(prescription_file.name, prescription_file)
            file_path = fs.path(filename)
            
            print(f"🔍 Processing prescription file: {file_path}")
            
            # Extract text using OCR
            from .ocr_utils import extract_text_from_prescription, match_medicines_in_text
            
            ocr_result = extract_text_from_prescription(file_path)
            
            # Delete temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            if not ocr_result['success']:
                return JsonResponse({
                    'success': False,
                    'error': ocr_result.get('error', 'OCR processing failed'),
                    'extracted_text': ocr_result.get('text', '')
                })
            
            extracted_text = ocr_result['text']
            print(f"✅ Extracted text: {len(extracted_text)} characters")
            
            # Match medicines from database
            medicine_matches = match_medicines_in_text(extracted_text)
            
            if not medicine_matches:
                return JsonResponse({
                    'success': True,
                    'medicines_found': False,
                    'extracted_text': extracted_text,
                    'detected_medicines': [],
                    'message': 'No medicines found in the prescription. Please ensure the image is clear and medicines are readable.'
                })
            
            
            # Get user location
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            
            has_location = latitude and longitude
            
            if has_location:
                try:
                    latitude = float(latitude)
                    longitude = float(longitude)
                except (ValueError, TypeError):
                    has_location = False
            
            # Prepare medicine data for response
            medicines_found = []
            medicine_ids = []
            
            for medicine in medicine_matches:
                if medicine.id not in medicine_ids:
                    medicine_ids.append(medicine.id)
                    medicines_found.append({
                        'id': medicine.id,
                        'name': medicine.name,
                        'generic_name': medicine.generic_name,
                        'manufacturer': getattr(medicine, 'manufacturer', 'N/A'),
                        'category': getattr(medicine, 'category', 'General')
                    })
            
            # Find pharmacies with these medicines
            inventory_items = Inventory.objects.filter(
                medicine_id__in=medicine_ids,
                quantity__gt=0
            ).select_related('pharmacy', 'medicine')
            
            # Group by pharmacy
            pharmacy_dict = {}
            for item in inventory_items:
                pharmacy_id = item.pharmacy.id
                
                if pharmacy_id not in pharmacy_dict:
                    pharmacy_dict[pharmacy_id] = {
                        'pharmacy': item.pharmacy,
                        'medicines': [],
                        'distance': None
                    }
                
                pharmacy_dict[pharmacy_id]['medicines'].append({
                    'name': item.medicine.name,
                    'generic_name': item.medicine.generic_name,
                    'price': float(item.price),
                    'quantity': item.quantity
                })
            
            # Calculate distances if location available
            if has_location:
                def haversine(lon1, lat1, lon2, lat2):
                    """Calculate distance between two coordinates in km"""
                    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                    dlon = lon2 - lon1
                    dlat = lat2 - lat1
                    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                    c = 2 * asin(sqrt(a))
                    km = 6371 * c
                    return round(km, 2)
                
                for pharmacy_id, data in pharmacy_dict.items():
                    pharmacy = data['pharmacy']
                    if pharmacy.latitude and pharmacy.longitude:
                        distance = haversine(
                            longitude, latitude,
                            pharmacy.longitude, pharmacy.latitude
                        )
                        data['distance'] = distance
            
            # Sort pharmacies
            pharmacy_list = list(pharmacy_dict.values())
            
            if has_location:
                # Sort by distance (nearest first)
                pharmacy_list.sort(key=lambda x: x['distance'] if x['distance'] is not None else float('inf'))
            else:
                # Sort by rating
                pharmacy_list.sort(key=lambda x: x['pharmacy'].rating if x['pharmacy'].rating else 0, reverse=True)
            
            # Prepare response data
            pharmacies_data = []
            for data in pharmacy_list[:20]:  # Top 20 pharmacies
                pharmacy = data['pharmacy']
                pharmacies_data.append({
                    'id': pharmacy.id,
                    'name': pharmacy.name,
                    'address': pharmacy.address,
                    'phone': pharmacy.phone,
                    'rating': float(pharmacy.rating) if pharmacy.rating else 0,
                    'distance': data['distance'],
                    'latitude': float(pharmacy.latitude) if pharmacy.latitude else None,
                    'longitude': float(pharmacy.longitude) if pharmacy.longitude else None,
                    'medicines': data['medicines']
                })
            
            # Save prescription upload record
            try:
                medicine_names_str = ', '.join([m['name'] for m in medicines_found])
                PrescriptionUpload.objects.create(
                    user=request.user,
                    prescription_image=prescription_file.name,
                    extracted_text=extracted_text[:5000],  # Limit text length
                    medicines_detected=medicine_names_str[:500]
                )
            except Exception as e:
                print(f"Warning: Could not save prescription record: {str(e)}")
            
            return JsonResponse({
                'success': True,
                'medicines_found': True,
                'extracted_text': extracted_text,
                'detected_medicines': [m['name'] for m in medicines_found],
                'medicines': medicines_found,
                'pharmacies': pharmacies_data,
                'total_pharmacies': len(pharmacies_data),
                'has_location': has_location
            })
            
        except Exception as e:
            import traceback
            print(f"❌ Prescription processing error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while processing the prescription. Please try again.'
            }, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def search_medicines_manual(request):
    """
    Search for medicines manually entered by user (no OCR required)
    """
    try:
        import json
        from math import radians, cos, sin, asin, sqrt
        
        # Parse JSON request body
        data = json.loads(request.body)
        medicine_names = data.get('medicines', [])
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not medicine_names:
            return JsonResponse({
                'success': False,
                'error': 'No medicine names provided'
            }, status=400)
        
        print(f"Manual search for medicines: {medicine_names}")
        
        # Search for medicines in database
        medicines_found = []
        medicine_ids = []
        
        for medicine_name in medicine_names:
            # Try exact match first
            medicines = Medicine.objects.filter(name__iexact=medicine_name.strip())
            
            if not medicines.exists():
                # Try partial match (contains)
                medicines = Medicine.objects.filter(name__icontains=medicine_name.strip())
            
            if medicines.exists():
                for med in medicines[:3]:  # Limit to top 3 matches per search
                    if med.id not in medicine_ids:
                        medicines_found.append(med)
                        medicine_ids.append(med.id)
        
        if not medicines_found:
            return JsonResponse({
                'success': True,
                'medicines_found': False,
                'total_medicines': 0,
                'total_pharmacies': 0,
                'message': 'No medicines found with the given names. Please check spelling or try different names.'
            })
        
        print(f"Found {len(medicines_found)} medicines in database")
        
        # Get pharmacies with these medicines in stock
        inventory_items = Inventory.objects.filter(
            medicine__in=medicines_found,
            quantity__gt=0
        ).select_related('pharmacy', 'medicine')
        
        if not inventory_items.exists():
            return JsonResponse({
                'success': True,
                'medicines_found': True,
                'detected_medicines': [med.name for med in medicines_found],
                'total_medicines': len(medicines_found),
                'total_pharmacies': 0,
                'pharmacies': [],
                'message': 'Medicines found but not available in any pharmacy currently.'
            })
        
        # Group by pharmacy
        pharmacy_dict = {}
        for item in inventory_items:
            pharmacy_id = item.pharmacy.id
            if pharmacy_id not in pharmacy_dict:
                pharmacy_dict[pharmacy_id] = {
                    'pharmacy': item.pharmacy,
                    'medicines': [],
                    'distance': None
                }
            
            pharmacy_dict[pharmacy_id]['medicines'].append({
                'id': item.medicine.id,
                'name': item.medicine.name,
                'generic_name': item.medicine.generic_name or '',
                'price': float(item.price),
                'quantity': item.quantity
            })
        
        # Calculate distances if location provided
        has_location = latitude is not None and longitude is not None
        
        if has_location:
            def haversine(lon1, lat1, lon2, lat2):
                lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                km = 6371 * c
                return round(km, 2)
            
            for pharmacy_id, data in pharmacy_dict.items():
                pharmacy = data['pharmacy']
                if pharmacy.latitude and pharmacy.longitude:
                    distance = haversine(
                        longitude, latitude,
                        pharmacy.longitude, pharmacy.latitude
                    )
                    data['distance'] = distance
        
        # Sort pharmacies
        pharmacy_list = list(pharmacy_dict.values())
        
        if has_location:
            pharmacy_list.sort(key=lambda x: x['distance'] if x['distance'] is not None else float('inf'))
        else:
            pharmacy_list.sort(key=lambda x: x['pharmacy'].rating if x['pharmacy'].rating else 0, reverse=True)
        
        # Prepare response
        pharmacies_data = []
        for data in pharmacy_list[:20]:
            pharmacy = data['pharmacy']
            pharmacies_data.append({
                'id': pharmacy.id,
                'name': pharmacy.name,
                'address': pharmacy.address,
                'phone': pharmacy.phone,
                'rating': float(pharmacy.rating) if pharmacy.rating else 0,
                'distance': data['distance'],
                'latitude': float(pharmacy.latitude) if pharmacy.latitude else None,
                'longitude': float(pharmacy.longitude) if pharmacy.longitude else None,
                'medicines': data['medicines']
            })
        
        return JsonResponse({
            'success': True,
            'medicines_found': True,
            'detected_medicines': [med.name for med in medicines_found],
            'total_medicines': len(medicines_found),
            'total_pharmacies': len(pharmacies_data),
            'pharmacies': pharmacies_data,
            'has_location': has_location,
            'extracted_text': f"Manually searched: {', '.join(medicine_names)}"
        })
    
    except Exception as e:
        print(f"Error in manual medicine search: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


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
            
            # Calculate distance for all pharmacies if lat/lon provided
            lat = request.GET.get('lat')
            lon = request.GET.get('lon')
            has_location = False
            if lat and lon:
                import math
                lat, lon = float(lat), float(lon)
                has_location = True
                for pharm in results:
                    if pharm['latitude'] and pharm['longitude'] and pharm['latitude'] != 0 and pharm['longitude'] != 0:
                        dlat = math.radians(pharm['latitude'] - lat)
                        dlon = math.radians(pharm['longitude'] - lon)
                        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(pharm['latitude'])) * math.sin(dlon/2)**2
                        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                        distance = 6371 * c  # km
                        pharm['distance'] = round(distance, 2)
                    else:
                        pharm['distance'] = 999999  # Use a large number instead of Infinity for JSON compatibility
            
            # Sort results
            if sort_by == 'rating':
                # Highest rating first, then by distance if available, else by name
                if has_location:
                    results.sort(key=lambda x: (-x['rating'], x.get('distance', 999999)))
                else:
                    results.sort(key=lambda x: (-x['rating'], x['name']))
            elif sort_by == 'name':
                results.sort(key=lambda x: x['name'])
            elif sort_by == 'distance':
                if has_location:
                    results.sort(key=lambda x: x.get('distance', 999999))
                else:
                    # Fallback to rating if no location provided
                    results.sort(key=lambda x: -x['rating'])
            
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


# ============================================================================
# PHARMACY OWNER PORTAL VIEWS
# ============================================================================

def pharmacy_owner_required(view_func):
    """Decorator to ensure user is logged in and is a pharmacy owner"""
    @login_required(login_url='pharmacy_login')
    def wrapper(request, *args, **kwargs):
        if request.user.profile.role != 'PHARMACY_OWNER':
            messages.error(request, 'You need pharmacy owner access to view this page.')
            return redirect('pharmacy_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def pharmacy_register(request):
    """Pharmacy owner registration"""
    if request.method == 'POST':
        form = PharmacyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # City coordinates (same as in load_pharmacy_data.py)
            city_coordinates = {
                'Delhi': (28.6139, 77.2090),
                'Mumbai': (19.0760, 72.8777),
                'Bangalore': (12.9716, 77.5946),
                'Hyderabad': (17.3850, 78.4867),
                'Chennai': (13.0827, 80.2707),
                'Kolkata': (22.5726, 88.3639),
                'Pune': (18.5204, 73.8567),
                'Ahmedabad': (23.0225, 72.5714),
                'Jaipur': (26.9124, 75.7873),
                'Lucknow': (26.8467, 80.9462),
                'Chandigarh': (30.7333, 76.7794),
                'Indore': (22.7196, 75.8577),
                'Kochi': (9.9312, 76.2673),
                'Surat': (21.1458, 72.1640),
                'Visakhapatnam': (17.6869, 83.2185),
                'Nagpur': (21.1458, 79.0882),
                'Bhopal': (23.2599, 77.4126),
                'Vadodara': (22.3072, 73.1812),
                'Ghaziabad': (28.6692, 77.4538),
                'Ludhiana': (30.9010, 75.8573),
                'Pimpri-Chinchwad': (18.6298, 73.7997),
                'Navi Mumbai': (19.0330, 73.0297),
            }
            
            city = form.cleaned_data['city']
            
            # Get base coordinates for the city
            if city in city_coordinates:
                base_lat, base_lon = city_coordinates[city]
            else:
                # Try geocoding as fallback, but constrain to city center
                from geopy.geocoders import Nominatim
                geolocator = Nominatim(user_agent="medilocate")
                try:
                    location = geolocator.geocode(city)
                    base_lat = location.latitude if location else 23.2599
                    base_lon = location.longitude if location else 77.4126
                except:
                    base_lat, base_lon = 23.2599, 77.4126  # Default to Bhopal
            
            # Add random variation within ~4.5km radius (±0.040 degrees)
            # Using slightly smaller range to ensure we stay under 5km
            import random
            latitude = base_lat + random.uniform(-0.040, 0.040)
            longitude = base_lon + random.uniform(-0.040, 0.040)
            
            pharmacy = Pharmacy.objects.create(
                name=form.cleaned_data['pharmacy_name'],
                address=form.cleaned_data['pharmacy_address'],
                city=city,
                phone=form.cleaned_data['pharmacy_phone'],
                latitude=latitude,
                longitude=longitude,
                owner=user,
                verified=False
            )
            
            messages.success(request, f'Registration successful! Welcome {user.username}. Your pharmacy is pending verification.')
            
            # Log the user in
            login(request, user)
            return redirect('pharmacy_dashboard')
    else:
        form = PharmacyRegistrationForm()
    
    return render(request, 'pharmacy/pharmacy_register.html', {'form': form})


def pharmacy_login(request):
    """Pharmacy owner login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.profile.role == 'PHARMACY_OWNER':
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('pharmacy_dashboard')
            else:
                messages.error(request, 'Access denied. This portal is for pharmacy owners only.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'pharmacy/pharmacy_login.html')


def pharmacy_logout(request):
    """Pharmacy owner logout"""
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('pharmacy_login')


@pharmacy_owner_required
def pharmacy_dashboard(request):
    """Pharmacy dashboard home"""
    from django.utils import timezone
    from datetime import timedelta
    
    pharmacy = Pharmacy.objects.filter(owner=request.user).first()
    
    if not pharmacy:
        messages.error(request, 'No pharmacy found for your account. Please contact support.')
        return redirect('home')
    
    # Get inventory stats
    inventory = Inventory.objects.filter(pharmacy=pharmacy)
    total_medicines = inventory.count()
    in_stock = inventory.filter(quantity__gt=0).count()
    low_stock = inventory.filter(quantity__gt=0, quantity__lte=20).count()
    out_of_stock = inventory.filter(quantity=0).count()
    
    # Get low stock items
    low_stock_items = inventory.filter(quantity__gt=0, quantity__lte=20).select_related('medicine')[:10]
    
    context = {
        'pharmacy': pharmacy,
        'total_medicines': total_medicines,
        'in_stock': in_stock,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'low_stock_items': low_stock_items,
        'now': timezone.now(),
    }
    
    return render(request, 'pharmacy/pharmacy_dashboard.html', context)


@pharmacy_owner_required
def pharmacy_medicines(request):
    """List all medicines in pharmacy inventory"""
    from django.core.paginator import Paginator
    
    pharmacy = Pharmacy.objects.filter(owner=request.user).first()
    
    if not pharmacy:
        messages.error(request, 'No pharmacy found for your account.')
        return redirect('pharmacy_dashboard')
    
    # Get search query
    search_query = request.GET.get('search', '')
    
    medicines = Inventory.objects.filter(pharmacy=pharmacy).select_related('medicine')
    
    if search_query:
        medicines = medicines.filter(
            models.Q(medicine__name__icontains=search_query) |
            models.Q(medicine__generic_name__icontains=search_query)
        )
    
    medicines = medicines.order_by('-last_updated')
    
    # Pagination
    paginator = Paginator(medicines, 20)
    page_number = request.GET.get('page')
    medicines_page = paginator.get_page(page_number)
    
    context = {
        'pharmacy': pharmacy,
        'medicines': medicines_page,
        'search_query': search_query,
    }
    
    return render(request, 'pharmacy/pharmacy_medicines.html', context)


@pharmacy_owner_required
def pharmacy_add_medicine(request):
    """Add new medicine to inventory"""
    pharmacy = Pharmacy.objects.filter(owner=request.user).first()
    
    if not pharmacy:
        messages.error(request, 'No pharmacy found for your account.')
        return redirect('pharmacy_dashboard')
    
    if request.method == 'POST':
        medicine_name = request.POST.get('medicine_name')
        generic_name = request.POST.get('generic_name', '')
        category = request.POST.get('category', '')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        
        # Check if medicine exists
        medicine = Medicine.objects.filter(name__iexact=medicine_name).first()
        
        if not medicine:
            # Create new medicine
            medicine = Medicine.objects.create(
                name=medicine_name,
                generic_name=generic_name,
                category=category,
                description=description
            )
            messages.success(request, f'New medicine "{medicine_name}" added to MediLocate database!')
        else:
            # Update existing medicine if fields provided
            if category and not medicine.category:
                medicine.category = category
            if description and not medicine.description:
                medicine.description = description
            medicine.save()
        
        # Check if already in inventory
        inventory_item = Inventory.objects.filter(pharmacy=pharmacy, medicine=medicine).first()
        
        if inventory_item:
            messages.warning(request, f'{medicine_name} is already in your inventory. Use Edit to update.')
            return redirect('pharmacy_edit_medicine', inventory_item.id)
        
        # Add to inventory
        Inventory.objects.create(
            pharmacy=pharmacy,
            medicine=medicine,
            quantity=int(quantity),
            price=float(price)
        )
        
        messages.success(request, f'{medicine_name} added to your inventory successfully!')
        return redirect('pharmacy_medicines')
    
    return render(request, 'pharmacy/pharmacy_add_medicine.html', {'pharmacy': pharmacy})


@pharmacy_owner_required
def pharmacy_bulk_upload(request):
    """Bulk upload medicines from CSV/Excel file - Preview step"""
    import pandas as pd
    import json
    
    pharmacy = Pharmacy.objects.filter(owner=request.user).first()
    
    if not pharmacy:
        messages.error(request, 'No pharmacy found for your account.')
        return redirect('pharmacy_dashboard')
    
    if request.method == 'POST' and request.FILES.get('medicine_file'):
        file = request.FILES['medicine_file']
        file_name = file.name.lower()
        
        # Validate file type
        if not (file_name.endswith('.csv') or file_name.endswith('.xlsx')):
            messages.error(request, 'Invalid file format. Please upload CSV or Excel (.xlsx) file only.')
            return redirect('pharmacy_add_medicine')
        
        try:
            # Read file based on type
            if file_name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Validate columns (case-insensitive)
            required_columns = ['medicine_name', 'price', 'quantity']
            optional_columns = ['generic_name', 'category', 'description']
            all_expected_columns = required_columns + optional_columns
            
            # Normalize column names
            df.columns = df.columns.str.strip().str.lower()
            
            # Check required columns
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                messages.error(request, f'Missing required columns: {", ".join(missing_columns)}')
                return redirect('pharmacy_add_medicine')
            
            # Validate unexpected columns
            unexpected_columns = [col for col in df.columns if col not in all_expected_columns]
            if unexpected_columns:
                messages.warning(request, f'Warning: Unexpected columns will be ignored: {", ".join(unexpected_columns)}')
            
            # Check row limit
            if len(df) > 500:
                messages.error(request, f'Too many rows ({len(df)}). Maximum 500 medicines per upload.')
                return redirect('pharmacy_add_medicine')
            
            if len(df) == 0:
                messages.error(request, 'File is empty. Please add medicine data.')
                return redirect('pharmacy_add_medicine')
            
            # Process and validate each row
            valid_medicines = []
            invalid_medicines = []
            duplicate_medicines = []
            
            for index, row in df.iterrows():
                row_num = index + 2  # +2 because pandas is 0-indexed and we have header row
                errors = []
                
                try:
                    # Validate required fields
                    medicine_name = str(row.get('medicine_name', '')).strip()
                    if not medicine_name or medicine_name.lower() in ['nan', 'none', '']:
                        errors.append('Medicine name is required')
                    
                    # Validate price
                    try:
                        price = float(row.get('price', 0))
                        if price < 0:
                            errors.append('Price cannot be negative')
                    except (ValueError, TypeError):
                        errors.append('Invalid price format')
                        price = 0
                    
                    # Validate quantity
                    try:
                        quantity = int(row.get('quantity', 0))
                        if quantity < 0:
                            errors.append('Quantity cannot be negative')
                    except (ValueError, TypeError):
                        errors.append('Invalid quantity (must be whole number)')
                        quantity = 0
                    
                    # Optional fields
                    generic_name = str(row.get('generic_name', '')).strip() if pd.notna(row.get('generic_name')) else ''
                    category = str(row.get('category', '')).strip() if pd.notna(row.get('category')) else ''
                    description = str(row.get('description', '')).strip() if pd.notna(row.get('description')) else ''
                    
                    if errors:
                        invalid_medicines.append({
                            'row': row_num,
                            'medicine_name': medicine_name,
                            'errors': errors
                        })
                    else:
                        # Check if already in inventory
                        medicine_obj = Medicine.objects.filter(name__iexact=medicine_name).first()
                        if medicine_obj:
                            inventory_exists = Inventory.objects.filter(pharmacy=pharmacy, medicine=medicine_obj).exists()
                            if inventory_exists:
                                duplicate_medicines.append({
                                    'row': row_num,
                                    'medicine_name': medicine_name,
                                    'status': 'Already in inventory'
                                })
                                continue
                        
                        valid_medicines.append({
                            'row': row_num,
                            'medicine_name': medicine_name,
                            'generic_name': generic_name,
                            'category': category,
                            'price': price,
                            'quantity': quantity,
                            'description': description
                        })
                
                except Exception as e:
                    invalid_medicines.append({
                        'row': row_num,
                        'medicine_name': medicine_name if 'medicine_name' in locals() else 'Unknown',
                        'errors': [str(e)]
                    })
            
            # Store validated data in session
            request.session['bulk_upload_data'] = {
                'valid_medicines': valid_medicines,
                'invalid_medicines': invalid_medicines,
                'duplicate_medicines': duplicate_medicines
            }
            
            # Redirect to preview page
            return render(request, 'pharmacy/pharmacy_bulk_preview.html', {
                'pharmacy': pharmacy,
                'valid_medicines': valid_medicines,
                'invalid_medicines': invalid_medicines,
                'duplicate_medicines': duplicate_medicines,
                'total_valid': len(valid_medicines),
                'total_invalid': len(invalid_medicines),
                'total_duplicate': len(duplicate_medicines),
            })
            
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            return redirect('pharmacy_add_medicine')
    
    messages.error(request, 'No file uploaded.')
    return redirect('pharmacy_add_medicine')


@pharmacy_owner_required
def pharmacy_bulk_upload_confirm(request):
    """Confirm and save bulk upload to database"""
    from decimal import Decimal
    
    pharmacy = Pharmacy.objects.filter(owner=request.user).first()
    
    if not pharmacy:
        messages.error(request, 'No pharmacy found for your account.')
        return redirect('pharmacy_dashboard')
    
    # Get data from session
    bulk_data = request.session.get('bulk_upload_data')
    
    if not bulk_data or request.method != 'POST':
        messages.error(request, 'No upload data found. Please upload the file again.')
        return redirect('pharmacy_add_medicine')
    
    valid_medicines = bulk_data.get('valid_medicines', [])
    
    if not valid_medicines:
        messages.warning(request, 'No valid medicines to upload.')
        return redirect('pharmacy_add_medicine')
    
    # Process and save medicines
    success_count = 0
    error_count = 0
    errors = []
    
    for med_data in valid_medicines:
        try:
            medicine_name = med_data['medicine_name']
            generic_name = med_data.get('generic_name', '')
            category = med_data.get('category', '')
            description = med_data.get('description', '')
            price = med_data['price']
            quantity = med_data['quantity']
            
            # Check if medicine exists in Medicine table
            medicine = Medicine.objects.filter(name__iexact=medicine_name).first()
            
            if not medicine:
                # Create new medicine
                medicine = Medicine.objects.create(
                    name=medicine_name,
                    generic_name=generic_name,
                    category=category,
                    description=description
                )
            else:
                # Update medicine if new info provided
                if generic_name and not medicine.generic_name:
                    medicine.generic_name = generic_name
                if category and not medicine.category:
                    medicine.category = category
                if description and not medicine.description:
                    medicine.description = description
                medicine.save()
            
            # Create inventory item
            Inventory.objects.create(
                pharmacy=pharmacy,
                medicine=medicine,
                quantity=quantity,
                price=Decimal(str(price))
            )
            
            success_count += 1
            
        except Exception as e:
            errors.append(f'{medicine_name}: {str(e)}')
            error_count += 1
    
    # Clear session data
    request.session.pop('bulk_upload_data', None)
    
    # Summary message
    if success_count > 0:
        messages.success(request, f'✓ Successfully added {success_count} medicines to your inventory!')
    
    if error_count > 0:
        messages.error(request, f'✗ Failed to add {error_count} medicines')
        for error in errors[:3]:
            messages.error(request, error)
    
    return redirect('pharmacy_medicines')


@pharmacy_owner_required
def pharmacy_download_template(request):
    """Download sample CSV template for bulk upload"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="medicine_upload_template.csv"'
    
    writer = csv.writer(response)
    # Write header
    writer.writerow(['medicine_name', 'generic_name', 'category', 'price', 'quantity', 'description'])
    # Write sample rows
    writer.writerow(['Paracetamol 500mg', 'Acetaminophen', 'Pain Relief', '50.00', '100', 'For fever and pain relief'])
    writer.writerow(['Amoxicillin 250mg', 'Amoxicillin', 'Antibiotics', '120.50', '50', 'Antibiotic for bacterial infections'])
    writer.writerow(['Vitamin C 500mg', 'Ascorbic Acid', 'Vitamins', '35.00', '200', 'Boosts immune system'])
    
    return response


@pharmacy_owner_required
def pharmacy_edit_medicine(request, inventory_id):
    """Edit medicine in inventory"""
    pharmacy = Pharmacy.objects.filter(owner=request.user).first()
    
    if not pharmacy:
        messages.error(request, 'No pharmacy found for your account.')
        return redirect('pharmacy_dashboard')
    
    inventory = get_object_or_404(Inventory, id=inventory_id, pharmacy=pharmacy)
    
    if request.method == 'POST':
        category = request.POST.get('category', '')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        
        # Update medicine details
        if category:
            inventory.medicine.category = category
        if description:
            inventory.medicine.description = description
        inventory.medicine.save()
        
        # Update inventory
        inventory.price = float(price)
        inventory.quantity = int(quantity)
        inventory.save()
        
        messages.success(request, f'{inventory.medicine.name} updated successfully!')
        return redirect('pharmacy_medicines')
    
    context = {
        'pharmacy': pharmacy,
        'inventory': inventory,
    }
    
    return render(request, 'pharmacy/pharmacy_edit_medicine.html', context)


@pharmacy_owner_required
def pharmacy_delete_medicine(request, inventory_id):
    """Delete medicine from inventory"""
    pharmacy = Pharmacy.objects.filter(owner=request.user).first()
    
    if not pharmacy:
        messages.error(request, 'No pharmacy found for your account.')
        return redirect('pharmacy_dashboard')
    
    inventory = get_object_or_404(Inventory, id=inventory_id, pharmacy=pharmacy)
    
    if request.method == 'POST':
        medicine_name = inventory.medicine.name
        inventory.delete()
        messages.success(request, f'{medicine_name} removed from your inventory.')
        return redirect('pharmacy_medicines')
    
    context = {
        'pharmacy': pharmacy,
        'inventory': inventory,
    }
    
    return render(request, 'pharmacy/pharmacy_delete_medicine.html', context)


@pharmacy_owner_required
def pharmacy_settings(request):
    """Pharmacy settings and profile management"""
    pharmacy = Pharmacy.objects.filter(owner=request.user).first()
    
    if not pharmacy:
        messages.error(request, 'No pharmacy found for your account.')
        return redirect('pharmacy_dashboard')
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'pharmacy')
        
        if form_type == 'pharmacy':
            # Update pharmacy info
            pharmacy.name = request.POST.get('pharmacy_name')
            pharmacy.address = request.POST.get('address')
            pharmacy.city = request.POST.get('city')
            pharmacy.phone = request.POST.get('phone')
            pharmacy.save()
            messages.success(request, 'Pharmacy information updated successfully!')
        
        elif form_type == 'account':
            # Update user account
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', '')
            request.user.save()
            
            phone_number = request.POST.get('phone_number', '')
            if phone_number:
                request.user.profile.phone_number = phone_number
                request.user.profile.save()
            
            messages.success(request, 'Account settings updated successfully!')
        
        elif form_type == 'password':
            # Change password
            from django.contrib.auth import update_session_auth_hash
            current_password = request.POST.get('current_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            
            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password1 != new_password2:
                messages.error(request, 'New passwords do not match.')
            else:
                request.user.set_password(new_password1)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully!')
        
        return redirect('pharmacy_settings')
    
    context = {
        'pharmacy': pharmacy,
    }
    
    return render(request, 'pharmacy/pharmacy_settings.html', context)


@pharmacy_owner_required
def pharmacy_orders(request):
    """View orders and prescription uploads"""
    pharmacy = Pharmacy.objects.filter(owner=request.user).first()
    
    if not pharmacy:
        messages.error(request, 'No pharmacy found for your account.')
        return redirect('pharmacy_dashboard')
    
    # Get search logs for this pharmacy
    from datetime import timedelta
    from django.utils import timezone
    from django.db.models import Count
    
    # Get medicines in this pharmacy
    pharmacy_medicines = Inventory.objects.filter(pharmacy=pharmacy).values_list('medicine_id', flat=True)
    
    # Get base queryset for search logs (without slicing)
    search_logs_base = SearchLog.objects.filter(
        search_timestamp__gte=timezone.now() - timedelta(days=30)
    )
    
    # Calculate stats BEFORE slicing
    total_searches = search_logs_base.count()
    recent_searches = SearchLog.objects.filter(
        search_timestamp__gte=timezone.now() - timedelta(days=7)
    ).count()
    unique_users = search_logs_base.values('user').distinct().count()
    
    # NOW slice for display (after distinct calculations)
    search_logs = search_logs_base.order_by('-search_timestamp')[:50]
    
    # Get prescription uploads (recent ones)
    prescriptions = PrescriptionUpload.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).order_by('-created_at')[:50]
    
    context = {
        'pharmacy': pharmacy,
        'search_logs': search_logs,
        'prescriptions': prescriptions,
        'total_searches': total_searches,
        'recent_searches': recent_searches,
        'unique_users': unique_users,
    }
    
    return render(request, 'pharmacy/pharmacy_orders.html', context)


@pharmacy_owner_required
def pharmacy_analytics(request):
    """Analytics and reports"""
    pharmacy = Pharmacy.objects.filter(owner=request.user).first()
    
    if not pharmacy:
        messages.error(request, 'No pharmacy found for your account.')
        return redirect('pharmacy_dashboard')
    
    from django.db.models import Sum, Count
    from datetime import timedelta
    from django.utils import timezone
    
    # Inventory stats
    inventory = Inventory.objects.filter(pharmacy=pharmacy)
    total_medicines = inventory.count()
    in_stock = inventory.filter(quantity__gt=0).count()
    low_stock = inventory.filter(quantity__gt=0, quantity__lte=20).count()
    out_of_stock = inventory.filter(quantity=0).count()
    
    # Calculate total inventory value
    total_inventory_value = inventory.aggregate(
        total=Sum(models.F('price') * models.F('quantity'))
    )['total'] or 0
    
    # Search stats
    search_logs = SearchLog.objects.filter(
        search_timestamp__gte=timezone.now() - timedelta(days=30)
    )
    total_searches = search_logs.count()
    unique_users = search_logs.values('user').distinct().count()
    
    # Low stock items
    low_stock_items = inventory.filter(quantity__gt=0, quantity__lte=20).select_related('medicine')
    
    # Top searched medicines (placeholder - would need proper implementation)
    top_medicines = []
    
    context = {
        'pharmacy': pharmacy,
        'total_medicines': total_medicines,
        'in_stock': in_stock,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'total_inventory_value': round(total_inventory_value, 2),
        'total_searches': total_searches,
        'unique_users': unique_users,
        'low_stock_items': low_stock_items,
        'top_medicines': top_medicines,
    }
    
    return render(request, 'pharmacy/pharmacy_analytics.html', context)
