# MediLocator Pharmacy Search Implementation Guide

## Overview

MediLocator now features **two distinct pharmacy search methods**:

1. **Manual Search** - Users manually enter location (address/PIN code)
2. **GPS Search** - Users allow GPS permission for automatic location detection

Both methods find nearby pharmacies based on:
- ✅ Medicine Availability (in stock)
- ✅ Distance (nearest first)
- ✅ Live Google Ratings

---

## 🔍 Search Method 1: Manual Search

### User Flow

```
User enters medicine name
          ↓
User enters address + PIN code + city
          ↓
System geocodes address to coordinates
          ↓
System finds nearby pharmacies within radius
          ↓
Results displayed sorted by: availability → distance → rating
```

### How to Use

**URL:** `http://localhost:8000/search/manual/`

**Steps:**
1. Enter medicine name (e.g., "Paracetamol")
2. Enter address (e.g., "MG Road")
3. Enter PIN code (e.g., "560001")
4. Enter city (e.g., "Bangalore")
5. Select search radius (5-25 km)
6. Click "Search Pharmacies"

### API Endpoint

**Endpoint:** `POST /api/search-manual/`

**Request:**
```json
{
    "medicine_name": "Paracetamol",
    "address": "MG Road, Bangalore 560001",
    "radius": 10
}
```

**Response:**
```json
{
    "success": true,
    "latitude": 12.9716,
    "longitude": 77.5946,
    "message": "Location coordinates found"
}
```

**Error Handling:**
- Missing medicine name: `"Medicine name is required"`
- Missing address: `"Address is required"`
- Invalid address: `"Could not find location for address..."`
- Network error: Returns error message with details

---

## 📍 Search Method 2: GPS Search

### User Flow

```
User enters medicine name
          ↓
User clicks "Get My Location" button
          ↓
Browser requests GPS permission
          ↓
User allows/denies permission
          ↓
System gets device coordinates
          ↓
System finds nearby pharmacies within radius
          ↓
Results displayed sorted by: availability → distance → rating
```

### How to Use

**URL:** `http://localhost:8000/search/gps/`

**Steps:**
1. Enter medicine name (e.g., "Paracetamol")
2. Click "Get My Location" button
3. Allow GPS permission when browser asks
4. Select search radius (5-25 km)
5. Click "Search Pharmacies"

### API Endpoint

**Endpoint:** `POST /api/search-gps/`

**Request:**
```json
{
    "medicine_name": "Paracetamol",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "radius": 10
}
```

**Response:**
```json
{
    "success": true,
    "total": 5,
    "medicine": "Paracetamol",
    "radius": 10,
    "pharmacies": [
        {
            "id": 1,
            "name": "Apollo Pharmacy",
            "address": "123 Brigade Road",
            "city": "Bangalore",
            "phone": "9876543210",
            "latitude": 12.9752,
            "longitude": 77.5956,
            "rating": 4.5,
            "distance": 0.45,
            "medicine_available": true,
            "available_medicines": [
                {
                    "name": "Paracetamol",
                    "quantity": 50,
                    "price": 45.00
                }
            ]
        },
        {...}
    ]
}
```

**Error Handling:**
- Missing medicine name: `"Medicine name is required"`
- No coordinates: `"Valid latitude and longitude are required"`
- Medicine not found: `"No pharmacies found with medicine: ..."`
- Network error: Returns error message

---

## 🔧 Backend Implementation

### 1. Distance Calculation (Haversine Formula)

**Function:** `haversine_distance(lat1, lon1, lat2, lon2)`

Located in `webapp/views.py`

Calculates great-circle distance between two points on Earth.

**Formula:**
```
a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
c = 2 ⋅ atan2( √a, √(1−a) )
d = R ⋅ c
```

Where:
- R = 6371 km (Earth's radius)
- φ = latitude, λ = longitude

**Example Usage:**
```python
distance = haversine_distance(
    user_lat, user_lon,
    pharmacy_lat, pharmacy_lon
)
# Returns distance in km (e.g., 2.5)
```

### 2. Geocoding Service

**Function:** `geocode_address(address_string)`

Located in `webapp/views.py`

Converts address string to coordinates using Nominatim API (OpenStreetMap).

**Supported Address Formats:**
- Street address: "123 Main Street, City, State"
- PIN code: "560001"
- Landmark: "MG Road, Bangalore"
- Mixed: "Connaught Place, New Delhi 110001"

**Example Usage:**
```python
lat, lon = geocode_address("MG Road, Bangalore 560001")
if lat and lon:
    print(f"Coordinates: {lat}, {lon}")
else:
    print("Address not found")
```

**Returns:**
- Success: `(latitude, longitude)` as floats
- Error: `(None, None)`

### 3. Medicine Availability Filtering

**Logic:**
1. Search for medicine in database (case-insensitive)
2. Find all pharmacies carrying that medicine
3. Filter by quantity > 0 (in stock)
4. Filter by pharmacy verification status
5. Calculate distance for each pharmacy
6. Filter by radius

**Database Query:**
```python
inventory = Inventory.objects.filter(
    medicine_id__in=medicines,
    quantity__gt=0,
    pharmacy__verified=True
).select_related('pharmacy', 'medicine')
```

### 4. Sorting Logic

**Sorting Order:**
1. **Primary:** Medicine Availability (always true in results)
2. **Secondary:** Distance (ascending - nearest first)
3. **Tertiary:** Rating (descending - highest rated first)

**Python Code:**
```python
results.sort(key=lambda x: (x['distance'], -x['rating']))
```

---

## 📱 Frontend Implementation

### Manual Search Template

**File:** `webapp/templates/accounts/search_manual.html`

**Features:**
- Medicine name autocomplete (minimum 2 characters)
- Address input with validation
- PIN code validation (5-6 digits)
- City name input
- Search radius selector (5-25 km)
- Example searches for quick start
- Comprehensive error messages
- Loading state during search

**Key Functions:**
- `handleMedicineInput()` - Autocomplete handler
- `fetchMedicineSuggestions()` - Fetch suggestions from API
- `fillExample()` - Fill form with example data
- Form validation before submission

### GPS Search Template

**File:** `webapp/templates/accounts/search_gps.html`

**Features:**
- Medicine name autocomplete
- GPS permission request with user-friendly errors
- Location status display
- Step-by-step instructions
- Search radius selector
- Timeout handling (15 seconds)
- High accuracy GPS setting

**Key Functions:**
- `getDeviceLocation()` - Request GPS permission and get coordinates
- `showLocationSuccess()` - Display successful location
- `showLocationError()` - Display user-friendly error messages
- Error handling for:
  - Permission denied
  - GPS unavailable
  - Timeout
  - Browser not supporting geolocation

### Home Page Integration

**File:** `webapp/templates/accounts/index.html`

**Changes:**
- Replaced generic promo cards with specific search options
- Added "Manual Search" card with icon and description
- Added "GPS Search" card with icon and description
- Direct navigation links to both search pages
- Styled to match existing MediLocator design

---

## 🗄️ Database Models

### Pharmacy Model
```python
class Pharmacy(models.Model):
    name = CharField()
    address = TextField()
    city = CharField()
    phone = CharField()
    latitude = FloatField(db_index=True)
    longitude = FloatField(db_index=True)
    rating = FloatField()
    verified = BooleanField(default=False, db_index=True)
```

### Medicine Model
```python
class Medicine(models.Model):
    name = CharField(unique=True, db_index=True)
    generic_name = CharField()
    category = CharField()
    common_doses = CharField()
```

### Inventory Model
```python
class Inventory(models.Model):
    pharmacy = ForeignKey(Pharmacy)
    medicine = ForeignKey(Medicine)
    quantity = IntegerField(validators=[MinValueValidator(0)])
    price = DecimalField(max_digits=10, decimal_places=2)
```

### SearchLog Model
```python
class SearchLog(models.Model):
    user = ForeignKey(User)
    medicines = JSONField(default=list)
    latitude = FloatField(null=True)
    longitude = FloatField(null=True)
    results_count = IntegerField()
    search_timestamp = DateTimeField(auto_now_add=True)
```

---

## 🔐 Security & Permissions

### URL Protection

Both search pages require user authentication:
```python
@login_required(login_url='login')
def search_manual_page(request):
    return render(request, 'accounts/search_manual.html')

@login_required(login_url='login')
def search_gps_page(request):
    return render(request, 'accounts/search_gps.html')
```

### CSRF Protection

API endpoints use `@csrf_exempt` decorator but validate CSRF tokens in frontend:
```javascript
function getCookie(name) {
    // Get CSRF token from cookies
    // Used in fetch headers: 'X-CSRFToken': csrftoken
}
```

### GPS Privacy

GPS location data:
- Never stored permanently
- Used only for current search session
- Not shared with third parties
- User must explicitly grant permission

---

## 📊 API Response Examples

### Successful Manual Search

```json
{
    "success": true,
    "latitude": 12.9716,
    "longitude": 77.5946,
    "message": "Location coordinates found"
}
```

### Successful GPS Search

```json
{
    "success": true,
    "total": 3,
    "medicine": "Paracetamol",
    "radius": 10,
    "pharmacies": [
        {
            "id": 1,
            "name": "Apollo Pharmacy",
            "address": "123 Brigade Road",
            "city": "Bangalore",
            "phone": "080-41123456",
            "latitude": 12.9752,
            "longitude": 77.5956,
            "rating": 4.5,
            "distance": 0.45,
            "medicine_available": true,
            "available_medicines": [
                {
                    "name": "Paracetamol",
                    "quantity": 50,
                    "price": 45.00
                }
            ]
        },
        {
            "id": 2,
            "name": "MediPlus",
            "address": "456 Church Street",
            "city": "Bangalore",
            "phone": "080-41987654",
            "latitude": 12.9815,
            "longitude": 77.5945,
            "rating": 4.2,
            "distance": 1.23,
            "medicine_available": true,
            "available_medicines": [
                {
                    "name": "Paracetamol",
                    "quantity": 25,
                    "price": 42.50
                }
            ]
        }
    ]
}
```

### Error Response

```json
{
    "success": false,
    "error": "Could not find location for address: Invalid Address. Please check the address and try again.",
    "pharmacies": []
}
```

---

## 🐛 Troubleshooting

### GPS Not Working

**Problem:** "Geolocation is not supported by your browser"

**Solution:**
- Use modern browser (Chrome, Firefox, Safari, Edge)
- Ensure HTTPS is used (GPS requires secure context)
- Check if GPS is enabled on device
- Try Manual Search instead

### GPS Permission Denied

**Problem:** "Location permission denied"

**Solution:**
- Check browser GPS permissions settings
- Clear browser cache and cookies
- Try in incognito/private window
- Enable GPS for the website
- Restart browser and try again

### Address Not Found

**Problem:** "Could not find location for address..."

**Solution:**
- Use complete address with city
- Include PIN code for better accuracy
- Use common landmark names
- Try shorter address variation
- Use street name instead of area name

### No Pharmacies Found

**Problem:** "No pharmacies found with medicine"

**Solutions:**
1. Check medicine spelling
2. Use generic name if available
3. Increase search radius
4. Try different location
5. Verify pharmacies are in database

### Slow Search Results

**Problem:** Search takes too long

**Solutions:**
- Reduce search radius
- Check internet connection
- Clear browser cache
- Try different time of day
- Report issue if persistent

---

## 📝 Configuration

### Required Settings

Add to `project/settings.py`:

```python
# Geolocation settings
GEOLOCATION_ENABLED = True
NOMINATIM_USER_AGENT = "medilocator_app"
NOMINATIM_TIMEOUT = 10

# Pharmacy search settings
DEFAULT_SEARCH_RADIUS = 10  # km
MAX_SEARCH_RADIUS = 25  # km
MIN_SEARCH_RADIUS = 5  # km
```

### Optional Enhancements

For Google Places API ratings:

```python
# Add Google Places API key
GOOGLE_PLACES_API_KEY = "YOUR_API_KEY_HERE"
GOOGLE_PLACES_ENABLED = True
```

---

## 🚀 Performance Optimization

### Database Indexes

Current indexes for fast queries:

```python
# Pharmacy model
- latitude, longitude (for spatial queries)
- verified, latitude, longitude (for verified pharmacies)

# Medicine model
- name (for search)
- generic_name (for search)

# Inventory model
- pharmacy, medicine (unique constraint)
- medicine, quantity (for availability check)
```

### Caching Recommendations

```python
# Cache medicine list
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache popular searches
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
def get_trending_medicines(request):
    ...
```

### Query Optimization

Use `select_related()` and `prefetch_related()`:

```python
inventory = Inventory.objects.filter(
    medicine_id__in=medicines,
    quantity__gt=0
).select_related('pharmacy', 'medicine')
```

---

## 📞 Support & Contact

**For Issues:**
- Check browser console for JavaScript errors (F12)
- Verify internet connection
- Check server logs for backend errors
- Try clearing browser cache

**Contact:**
- Phone: 9240250346
- Hours: 8:00 AM to 10:00 PM IST

---

## 📄 License

MediLocator © 2024. All rights reserved.

---

## Version History

- **v1.0.0** (2024-11-13)
  - Implemented Manual Search feature
  - Implemented GPS Search feature
  - Added Haversine distance calculation
  - Added Nominatim geocoding integration
  - Added comprehensive error handling
  - Updated home page with new search options

---
