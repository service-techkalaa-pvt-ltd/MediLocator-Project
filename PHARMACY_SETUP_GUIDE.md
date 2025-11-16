# MediLocator - Medical Store Search Database Setup Guide

## Overview
This guide explains how to set up and use the new pharmacy database and search functionality in the MediLocator application.

## Database Schema

### Key Models
- **Pharmacy**: Medical store locations with lat/lon coordinates and ratings
- **Medicine**: Medicine master data (names, generic names, categories)
- **Inventory**: Stock status of medicines at each pharmacy
- **SearchLog**: Tracks all searches performed by users

## Setup Instructions

### Step 1: Create Database Records
Run this command to load all pharmacy data (50 real stores + 100+ dummy stores):

```bash
python manage.py load_pharmacies
```

This command:
- Creates an admin pharmacy user
- Loads 50 real pharmacy records from your dataset
- Generates 100+ dummy pharmacies across major Indian cities
- Sets all pharmacies as verified
- Assigns random ratings (3.0-5.0 stars)

### Step 2: Run Migrations (if not done)
```bash
python manage.py migrate
```

### Step 3: Test the API
Access the search API directly:
```
GET /api/search-pharmacies/?lat=18.5204&lon=73.8567&radius=10&medicine=paracetamol
```

**Parameters:**
- `lat` (float): Latitude of search location
- `lon` (float): Longitude of search location  
- `radius` (float): Search radius in kilometers (default: 5)
- `medicine` (string): Medicine name (optional, for logging)

**Response:**
```json
{
    "success": true,
    "total": 12,
    "medicine": "paracetamol",
    "pharmacies": [
        {
            "id": 1,
            "name": "Janwa Medical",
            "address": "Shop No 01...",
            "city": "Pimpri-Chinchwad",
            "phone": "9876543210",
            "latitude": 18.6402,
            "longitude": 73.8000,
            "rating": 4.9,
            "distance": 0.45
        },
        ...
    ]
}
```

## Search Functionality

### Frontend Flow
1. **User selects location** (Auto GPS or Manual address)
2. **User enters medicine name**
3. **Click "Search Stores" button**
4. **Backend searches nearby pharmacies** within 10 km radius
5. **Results displayed in modal** with:
   - Store name and rating
   - Full address
   - Phone number
   - Distance from search location

### Backend Implementation

**Location Modes:**
- **Automatic**: Uses browser Geolocation API + Nominatim reverse geocoding
- **Manual**: User enters address/PIN → Nominatim geocoding to coordinates

**Search Algorithm:**
- Filters pharmacies within radius using lat/lon ranges
- Calculates exact distance using Haversine formula
- Sorts by distance (closest first)
- Returns top 20 results

**Coordinates Used:**
- Pune: 18.5204, 73.8567
- Mumbai: 19.0760, 72.8777
- Bangalore: 12.9716, 77.5946
- Delhi: 28.7041, 77.1025
- And 11+ other major cities

## Database Statistics

### Total Pharmacies
- Real pharmacies from dataset: 50
- Generated dummy pharmacies: 100+
- **Total: 150+** verified pharmacies

### Geographic Coverage
- Pune area: 30+ stores
- Mumbai area: 40+ stores
- Navi Mumbai: 8+ stores
- Nationwide dummy stores: 72+ across 15 major cities

### Rating Distribution
- 5.0 stars: ~20%
- 4.5-4.9 stars: ~30%
- 4.0-4.4 stars: ~25%
- 3.5-3.9 stars: ~15%
- 3.0-3.4 stars: ~10%

## Files Modified/Created

### New Files
- `webapp/management/commands/load_pharmacies.py` - Data loading command
- `webapp/management/commands/__init__.py` - Package marker

### Modified Files
- `webapp/views.py` - Added `search_pharmacies()` API endpoint
- `webapp/urls.py` - Added `/api/search-pharmacies/` route
- `webapp/templates/accounts/index.html` - Enhanced search functions:
  - `performPharmacySearch()` - Calls backend API
  - `displaySearchResults()` - Shows results in modal
  - `geocodeManualAddress()` - Geocodes typed addresses
  - `storeCoordinates()` - Stores GPS coordinates

## Testing Checklist

- [ ] Run `python manage.py load_pharmacies` successfully
- [ ] Check database: `SELECT COUNT(*) FROM webapp_pharmacy;` (should show 150+)
- [ ] Test auto location: Click location button, approve GPS
- [ ] Test manual location: Enter "Pune 411001" or similar
- [ ] Test search: Enter medicine name like "Paracetamol"
- [ ] Verify API: Visit `/api/search-pharmacies/?lat=18.5&lon=73.8&radius=10`
- [ ] Check modal: Results should show in popup
- [ ] Verify sorting: Closest pharmacies should be first
- [ ] Test on mobile: Geolocation permission should work

## Troubleshooting

### "No pharmacies found"
- Check if pharmacies are loaded: `python manage.py load_pharmacies`
- Verify coordinates are reasonable (18-19 for Pune, 19+ for Mumbai)
- Increase radius parameter in search

### "Location not found"
- In auto mode: Check browser geolocation permissions
- In manual mode: Try entering just city name (e.g., "Pune")
- Nominatim API might be slow - wait a moment

### API returns 500 error
- Check Django logs for import/syntax errors
- Ensure `math` module is imported in views.py
- Verify database migrations are complete

### Empty search results
- Search limit might be too small (default 10 km)
- No pharmacies in database - run load_pharmacies
- Check if pharmacies have `verified=True` flag

## Next Steps

1. **Integrate medicine inventory**: Add medicine stock to Inventory model
2. **Real-time availability**: Update Inventory.quantity dynamically
3. **Pharmacy ratings system**: Link to user reviews
4. **Medicine search by name**: Find which pharmacies have specific medicines
5. **Distance-based sorting**: Already implemented!
6. **Favorite pharmacies**: Add user save feature

## API Endpoint Documentation

### Search Pharmacies Endpoint

**URL**: `/api/search-pharmacies/`  
**Method**: GET  
**Auth**: Not required (public search)

**Request Parameters:**
| Parameter | Type | Required | Example | Description |
|-----------|------|----------|---------|-------------|
| lat | float | Yes | 18.5204 | Latitude of search center |
| lon | float | Yes | 73.8567 | Longitude of search center |
| radius | float | No | 10 | Search radius in kilometers (default: 5) |
| medicine | string | No | paracetamol | Medicine name (for logging only) |

**Success Response (200):**
```json
{
    "success": true,
    "total": 5,
    "medicine": "paracetamol",
    "pharmacies": [...]
}
```

**Error Response (400/500):**
```json
{
    "success": false,
    "error": "Error description",
    "pharmacies": []
}
```

## Performance Tips

- Search radius of 10 km recommended for cities
- Results limited to top 20 pharmacies (prevent UI overload)
- Use database indexes on lat/lon for fast queries
- Nominatim API has rate limiting - cache geocoding results

---

**Version**: 1.0  
**Last Updated**: November 2025  
**Status**: Ready for testing
