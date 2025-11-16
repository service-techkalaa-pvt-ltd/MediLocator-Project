# Medicine Search Integration Plan

## Goal
Add medicine search functionality to `search_results.html` WITHOUT changing existing location/city search features.

---

## What's Working ✅

### simple_search.html (Reference Page)
- ✅ Medicine input box
- ✅ Search button
- ✅ Calls `/api/search-medicines/?medicine=NAME`
- ✅ Displays 216 pharmacies with:
  - Pharmacy name
  - Rating ⭐
  - Address & City
  - Phone
  - Available medicines with quantity & price

### search_results.html (Original Features)
- ✅ Location search (GPS-based)
- ✅ City search
- ✅ Pharmacy cards with details
- ✅ Sort & filter options
- ✅ Beautiful navbar and styling

---

## What You Need To Do

### Step 1: Add CSS Styles (search_results.html)
Add these CSS classes to the `<style>` section:
```css
.pharmacy-card { background: #f8f9fa; padding: 20px; margin-bottom: 15px; border-radius: 8px; border-left: 4px solid #1E40AF; }
.pharmacy-name { font-size: 1.2rem; font-weight: bold; color: #1E40AF; margin-bottom: 10px; }
.pharmacy-info { color: #666; margin-bottom: 5px; }
.rating { background: #FFA500; color: white; padding: 5px 10px; border-radius: 5px; display: inline-block; margin-bottom: 10px; }
.medicines { margin-top: 10px; padding: 10px; background: white; border-radius: 5px; }
.medicine-item { padding: 8px; border-bottom: 1px solid #eee; }
.medicine-item:last-child { border-bottom: none; }
.status { padding: 15px; background: #e3f2fd; border-radius: 8px; margin-bottom: 20px; }
.error { background: #ffebee; color: #c62828; }
.success { background: #e8f5e9; color: #2e7d32; }
```

### Step 2: Add HTML Elements (search_results.html)
In the `.search-header` section, add:
```html
<!-- Medicine Search Section -->
<div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd;">
    <h3>Search by Medicine</h3>
    <div class="search-box">
        <input type="text" id="medicineInput" placeholder="Enter medicine name (e.g., Paracetamol, Aspirin)" />
        <button onclick="searchMedicine()">Search Medicine</button>
    </div>
</div>

<!-- Status Display -->
<div id="status" class="status" style="display: none; margin-top: 20px;"></div>
```

### Step 3: Add JavaScript Functions (search_results.html)
Add these functions to the `<script>` section at the END (before closing `</script>`):

```javascript
// Medicine Search Function
function searchMedicine() {
    const medicine = document.getElementById('medicineInput').value.trim();
    if (!medicine) {
        showStatus('Please enter a medicine name', 'error');
        return;
    }
    
    showStatus('Searching...', 'status');
    const url = `/api/search-medicines/?medicine=${encodeURIComponent(medicine)}`;
    
    console.log('Medicine Search - URL:', url);
    
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('API error: ' + response.status);
            return response.json();
        })
        .then(data => {
            console.log('Medicine API Response:', data);
            
            if (!data.success) {
                showStatus('API Error', 'error');
                return;
            }
            
            if (!data.pharmacies || data.pharmacies.length === 0) {
                showStatus('No pharmacies found with this medicine', 'error');
                document.getElementById('resultCount').textContent = '0';
                document.getElementById('resultsContainer').innerHTML = '';
                return;
            }
            
            // Success!
            showStatus(`Found ${data.total} pharmacies with ${medicine}`, 'success');
            document.getElementById('resultCount').textContent = data.total;
            
            allResults = data.pharmacies;
            displayResults();
        })
        .catch(error => {
            console.error('Error:', error);
            showStatus('Error: ' + error.message, 'error');
            document.getElementById('resultCount').textContent = '0';
        });
}

// Display Pharmacy Cards
function displayMedicineResults(pharmacies) {
    const container = document.getElementById('resultsContainer');
    container.innerHTML = '';
    
    pharmacies.forEach((pharmacy, index) => {
        const card = document.createElement('div');
        card.className = 'pharmacy-card';
        
        let medicinesHtml = '';
        if (pharmacy.available_medicines && pharmacy.available_medicines.length > 0) {
            medicinesHtml = '<div class="medicines"><strong>Available Medicines:</strong>';
            pharmacy.available_medicines.forEach(med => {
                medicinesHtml += `
                    <div class="medicine-item">
                        <strong>${med.name}</strong> - 
                        Quantity: ${med.quantity} pcs - 
                        Price: ₹${med.price}
                    </div>
                `;
            });
            medicinesHtml += '</div>';
        }
        
        card.innerHTML = `
            <div class="pharmacy-name">${pharmacy.name}</div>
            <div class="rating">⭐ ${pharmacy.rating}</div>
            <div class="pharmacy-info">📍 ${pharmacy.address}, ${pharmacy.city}</div>
            <div class="pharmacy-info">📞 ${pharmacy.phone}</div>
            ${medicinesHtml}
        `;
        
        container.appendChild(card);
    });
}

// Show Status Messages
function showStatus(message, type) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = 'status ' + type;
    statusDiv.style.display = 'block';
}

// Allow Enter key to search
document.getElementById('medicineInput')?.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        searchMedicine();
    }
});
```

---

## Testing Checklist

- [ ] Type "Paracetamol" in medicine search box
- [ ] Click "Search Medicine" button
- [ ] See 216 pharmacies displayed with medicines, quantities, prices
- [ ] Existing location search still works
- [ ] Existing city search still works
- [ ] Status messages appear (success/error)
- [ ] Enter key works in medicine search box

---

## Files To Modify
1. `search_results.html` - Add CSS, HTML elements, and JavaScript functions

## Files NOT To Change
1. `simple_search.html` - Keep as reference
2. `index.html` - No changes needed
3. `views.py` - No changes needed
4. `urls.py` - No changes needed

---

## API Endpoints Used
- `/api/search-medicines/?medicine=NAME` - Returns pharmacies with medicine data

## Expected Result
- One page (`search_results.html`) with TWO search modes:
  - Mode 1: Search by medicine name
  - Mode 2: Search by location/city (existing)
- Both return beautiful pharmacy cards with all details

