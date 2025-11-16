##Importing library
import re
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pickle

# --- Put your addresses here (or read from file) ---
addresses = [
    "Vijay Nagar,  Mumbai, Maharashtra, India"
]

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
query_point = lat_lon                # latitude & longitude
query_scaled = scaler.transform(query_point)

# --- Step: Get top 3 nearest addresses
distances, indices = model.kneighbors(query_scaled, n_neighbors=3)

# --- Step: Fetch addresses and ratings
nearest_addresses = df.iloc[indices[0]]['Address'].values
nearest_ratings = df.iloc[indices[0]]['Rating'].values
medical_names = df.iloc[indices[0]]['Medical Names'].values

# --- Step: Print results ---
for addr, rating,med in zip(nearest_addresses, nearest_ratings,medical_names):
    print(f"Address: {addr}, Rating: {rating}, Medical Names:{med}")
