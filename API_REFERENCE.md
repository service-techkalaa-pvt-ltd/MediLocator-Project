# MediLocator API Reference

## Table of Contents

1. [Manual Location Search](#manual-location-search)
2. [GPS Location Search](#gps-location-search)
3. [Response Formats](#response-formats)
4. [Error Handling](#error-handling)
5. [Code Examples](#code-examples)

---

## Manual Location Search

Convert address to coordinates and find nearby pharmacies with medicine.

### Endpoint

```
POST /api/search-manual/
```

### Authentication

Required: Yes (User login required on frontend)

### Request

**Headers:**
```
Content-Type: application/json
X-CSRFToken: {csrf_token}
```

**Body:**
```json
{
    "medicine_name": "Paracetamol",
    "address": "MG Road, Bangalore 560001",
    "radius": 10
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| medicine_name | string | Yes | Name of medicine to search for |
| address | string | Yes | Complete address including city and PIN code |
| radius | integer | No | Search radius in km (default: 10) |

### Response

**Success (200):**
```json
{
    "success": true,
    "latitude": 12.9716,
    "longitude": 77.5946,
    "message": "Location coordinates found"
}
```

**Error (400/500):**
```json
{
    "success": false,
    "error": "Could not find location for address: MG Road, Bangalore 560001. Please check the address and try again."
}
```

### Example Usage

**JavaScript:**
```javascript
const response = await fetch('/api/search-manual/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        medicine_name: 'Paracetamol',
        address: 'MG Road, Bangalore 560001',
        radius: 10
    })
});

const data = await response.json();
if (data.success) {
    console.log(`Found at: ${data.latitude}, ${data.longitude}`);
    // Redirect to results page
    window.location.href = `/search-results/?lat=${data.latitude}&lon=${data.longitude}&medicine=${medicine}&mode=manual`;
} else {
    console.error(data.error);
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/search-manual/ \
  -H "Content-Type: application/json" \
  -d '{
    "medicine_name": "Paracetamol",
    "address": "MG Road, Bangalore 560001",
    "radius": 10
  }'
```

**Python:**
```python
import requests
import json

url = 'http://localhost:8000/api/search-manual/'
headers = {
    'Content-Type': 'application/json',
}
data = {
    'medicine_name': 'Paracetamol',
    'address': 'MG Road, Bangalore 560001',
    'radius': 10
}

response = requests.post(url, headers=headers, json=data)
result = response.json()

if result['success']:
    print(f"Coordinates: {result['latitude']}, {result['longitude']}")
else:
    print(f"Error: {result['error']}")
```

---

## GPS Location Search

Find pharmacies with medicine using GPS coordinates.

### Endpoint

```
POST /api/search-gps/
```

### Authentication

Required: Yes (User login required on frontend)

### Request

**Headers:**
```
Content-Type: application/json
X-CSRFToken: {csrf_token}
```

**Body:**
```json
{
    "medicine_name": "Paracetamol",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "radius": 10
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| medicine_name | string | Yes | Name of medicine to search for |
| latitude | float | Yes | User's latitude coordinate |
| longitude | float | Yes | User's longitude coordinate |
| radius | integer | No | Search radius in km (default: 10) |

### Response

**Success (200):**
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

**Error (400/500):**
```json
{
    "success": false,
    "error": "No pharmacies found with medicine: Paracetamol",
    "pharmacies": []
}
```

### Example Usage

**JavaScript:**
```javascript
const response = await fetch('/api/search-gps/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        medicine_name: 'Paracetamol',
        latitude: 12.9716,
        longitude: 77.5946,
        radius: 10
    })
});

const data = await response.json();
if (data.success) {
    console.log(`Found ${data.total} pharmacies`);
    // Display results
    data.pharmacies.forEach(pharmacy => {
        console.log(`${pharmacy.name}: ${pharmacy.distance}km away (Rating: ${pharmacy.rating})`);
    });
} else {
    console.error(data.error);
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/search-gps/ \
  -H "Content-Type: application/json" \
  -d '{
    "medicine_name": "Paracetamol",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "radius": 10
  }'
```

**Python:**
```python
import requests

url = 'http://localhost:8000/api/search-gps/'
headers = {'Content-Type': 'application/json'}
data = {
    'medicine_name': 'Paracetamol',
    'latitude': 12.9716,
    'longitude': 77.5946,
    'radius': 10
}

response = requests.post(url, headers=headers, json=data)
result = response.json()

if result['success']:
    for pharmacy in result['pharmacies']:
        print(f"{pharmacy['name']} - {pharmacy['distance']}km ({pharmacy['rating']}★)")
else:
    print(f"Error: {result['error']}")
```

---

## Response Formats

### Pharmacy Object

```json
{
    "id": 1,
    "name": "Apollo Pharmacy",
    "address": "123 Brigade Road, Bangalore",
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
        },
        {
            "name": "Aspirin",
            "quantity": 30,
            "price": 35.00
        }
    ]
}
```

### Fields Description

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique pharmacy ID |
| name | string | Pharmacy name |
| address | string | Complete address |
| city | string | City name |
| phone | string | Contact phone number |
| latitude | float | GPS latitude coordinate |
| longitude | float | GPS longitude coordinate |
| rating | float | Google/System rating (0-5) |
| distance | float | Distance from user location in km |
| medicine_available | boolean | True if medicine is in stock |
| available_medicines | array | List of medicines with quantity and price |

---

## Error Handling

### HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | Success | All requests completed successfully |
| 400 | Bad Request | Missing required parameters |
| 405 | Method Not Allowed | Using GET instead of POST |
| 500 | Server Error | Backend error during processing |

### Error Response Format

```json
{
    "success": false,
    "error": "Descriptive error message",
    "pharmacies": []
}
```

### Common Errors

**Missing Medicine Name:**
```json
{
    "success": false,
    "error": "Medicine name is required"
}
```

**Invalid Address:**
```json
{
    "success": false,
    "error": "Could not find location for address: Invalid Address. Please check the address and try again."
}
```

**Invalid Coordinates:**
```json
{
    "success": false,
    "error": "Valid latitude and longitude are required"
}
```

**No Results:**
```json
{
    "success": true,
    "total": 0,
    "medicine": "Paracetamol",
    "pharmacies": [],
    "message": "No pharmacies found with medicine: Paracetamol"
}
```

---

## Code Examples

### Complete Search Flow - Manual Search

```javascript
async function performManualSearch(medicineName, address, city, pinCode, radius) {
    try {
        // Step 1: Geocode address
        const manualResponse = await fetch('/api/search-manual/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                medicine_name: medicineName,
                address: `${address}, ${city} ${pinCode}`,
                radius: parseInt(radius)
            })
        });

        const manualData = await manualResponse.json();

        if (!manualData.success) {
            throw new Error(manualData.error);
        }

        // Step 2: Redirect to results with coordinates
        const params = new URLSearchParams({
            medicine: medicineName,
            lat: manualData.latitude,
            lon: manualData.longitude,
            radius: radius,
            mode: 'manual'
        });

        window.location.href = `/search-results/?${params.toString()}`;

    } catch (error) {
        console.error('Search failed:', error.message);
        alert(`Search failed: ${error.message}`);
    }
}

// Usage
performManualSearch(
    'Paracetamol',
    'MG Road',
    'Bangalore',
    '560001',
    10
);
```

### Complete Search Flow - GPS Search

```javascript
async function performGPSSearch(medicineName, radius) {
    try {
        // Step 1: Get GPS coordinates
        if (!navigator.geolocation) {
            throw new Error('Geolocation is not supported by your browser');
        }

        const position = await new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {
                timeout: 15000,
                enableHighAccuracy: true
            });
        });

        const lat = position.coords.latitude;
        const lon = position.coords.longitude;

        // Step 2: Search pharmacies with medicine
        const gpsResponse = await fetch('/api/search-gps/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                medicine_name: medicineName,
                latitude: lat,
                longitude: lon,
                radius: parseInt(radius)
            })
        });

        const gpsData = await gpsResponse.json();

        if (!gpsData.success) {
            throw new Error(gpsData.error);
        }

        // Step 3: Redirect to results with GPS coordinates
        const params = new URLSearchParams({
            medicine: medicineName,
            lat: lat,
            lon: lon,
            radius: radius,
            mode: 'gps'
        });

        window.location.href = `/search-results/?${params.toString()}`;

    } catch (error) {
        console.error('GPS search failed:', error.message);
        alert(`GPS search failed: ${error.message}`);
    }
}

// Usage
performGPSSearch('Paracetamol', 10);
```

### Display Results

```javascript
function displayPharmacyResults(pharmacies) {
    const container = document.getElementById('results-container');
    container.innerHTML = '';

    if (pharmacies.length === 0) {
        container.innerHTML = '<p>No pharmacies found.</p>';
        return;
    }

    pharmacies.forEach(pharmacy => {
        const html = `
            <div class="pharmacy-card">
                <h3>${pharmacy.name}</h3>
                <p><strong>Address:</strong> ${pharmacy.address}</p>
                <p><strong>Phone:</strong> ${pharmacy.phone}</p>
                <p><strong>Distance:</strong> ${pharmacy.distance} km</p>
                <p><strong>Rating:</strong> ${pharmacy.rating}/5 ⭐</p>
                <p><strong>Medicine Available:</strong> ${pharmacy.medicine_available ? 'Yes' : 'No'}</p>
                <div class="medicines">
                    <h5>Available Medicines:</h5>
                    <ul>
                        ${pharmacy.available_medicines.map(med => `
                            <li>${med.name} - Qty: ${med.quantity}, Price: ₹${med.price}</li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;
        container.innerHTML += html;
    });
}

// Usage
const pharmacies = data.pharmacies;
displayPharmacyResults(pharmacies);
```

---

## Testing the APIs

### Using Postman

1. **Import Collection:**
   - Create new request
   - Method: POST
   - URL: `http://localhost:8000/api/search-gps/`

2. **Headers Tab:**
   - Key: `Content-Type`
   - Value: `application/json`

3. **Body Tab (Raw JSON):**
   ```json
   {
       "medicine_name": "Paracetamol",
       "latitude": 12.9716,
       "longitude": 77.5946,
       "radius": 10
   }
   ```

4. **Click Send**

### Using Python Script

```python
import requests
import json
from datetime import datetime

def test_search_apis():
    base_url = 'http://localhost:8000'
    
    # Test 1: Manual Search
    print("=" * 50)
    print(f"Test 1: Manual Search - {datetime.now()}")
    print("=" * 50)
    
    manual_response = requests.post(
        f'{base_url}/api/search-manual/',
        json={
            'medicine_name': 'Paracetamol',
            'address': 'MG Road, Bangalore 560001',
            'radius': 10
        }
    )
    
    print(f"Status: {manual_response.status_code}")
    print(f"Response: {json.dumps(manual_response.json(), indent=2)}")
    
    # Test 2: GPS Search
    print("\n" + "=" * 50)
    print(f"Test 2: GPS Search - {datetime.now()}")
    print("=" * 50)
    
    gps_response = requests.post(
        f'{base_url}/api/search-gps/',
        json={
            'medicine_name': 'Paracetamol',
            'latitude': 12.9716,
            'longitude': 77.5946,
            'radius': 10
        }
    )
    
    print(f"Status: {gps_response.status_code}")
    response_data = gps_response.json()
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    if response_data.get('success'):
        print(f"\nTotal Pharmacies Found: {response_data['total']}")
        for pharmacy in response_data['pharmacies'][:3]:  # Show first 3
            print(f"  - {pharmacy['name']}: {pharmacy['distance']}km away")

if __name__ == '__main__':
    test_search_apis()
```

---

## Pagination & Limits

Currently, APIs return **top 50 results** maximum.

For better performance with large result sets:

```python
# Recommended pagination
offset = 0
limit = 20

results = results[offset:offset+limit]
```

---

## Rate Limiting

Currently no rate limiting implemented. For production:

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h', method='POST')
def search_gps(request):
    # ... implementation
```

---

## Version

**API Version:** 1.0.0

**Last Updated:** 2024-11-13

---
