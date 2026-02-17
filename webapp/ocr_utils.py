"""
Simple OCR Utilities for Prescription Processing
Extracts text from prescription images and matches with database medicines
No ML models - pure OCR + text matching approach
"""

import os
import re
import cv2
import numpy as np
from PIL import Image
import pytesseract
from decouple import config

# Configure Tesseract path for different environments
if os.name == 'nt':  # Windows
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Tesseract-OCR\tesseract.exe',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"✅ Tesseract found at: {path}")
            break
else:  # Linux/Unix (Replit, production servers)
    # Common Linux paths
    linux_paths = [
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract',
        config('TESSERACT_CMD', default='/usr/bin/tesseract'),
    ]
    
    for path in linux_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"✅ Tesseract found at: {path}")
            break


def preprocess_image_for_ocr(image_path):
    """
    Preprocess image for better OCR accuracy
    - Converts to grayscale
    - Applies denoising
    - Enhances contrast
    - Applies thresholding
    """
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise Exception("Could not read image file")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(denoised)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            contrast, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Convert back to PIL Image
        pil_image = Image.fromarray(thresh)
        return pil_image
        
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        # Return original image as fallback
        return Image.open(image_path)


def extract_text_from_prescription(image_path):
    """
    Extract text from prescription image using pytesseract OCR
    Uses multiple OCR passes for better accuracy
    """
    try:
        # Check if Tesseract is installed
        try:
            pytesseract.get_tesseract_version()
        except pytesseract.TesseractNotFoundError:
            return {
                'success': False,
                'text': '',
                'error': 'Tesseract OCR is not installed. Please install Tesseract-OCR from https://github.com/UB-Mannheim/tesseract/wiki'
            }
        
        print(f"📄 Extracting text from: {image_path}")
        
        # Try multiple OCR configurations for better results
        extracted_texts = []
        
        # Method 1: Preprocessed image with PSM 6 (uniform text block)
        try:
            processed_image = preprocess_image_for_ocr(image_path)
            config1 = r'--oem 3 --psm 6'
            text1 = pytesseract.image_to_string(processed_image, config=config1, lang='eng')
            extracted_texts.append(text1)
        except:
            pass
        
        # Method 2: Original image with PSM 3 (auto page segmentation)
        try:
            original_image = Image.open(image_path)
            config2 = r'--oem 3 --psm 3'
            text2 = pytesseract.image_to_string(original_image, config=config2, lang='eng')
            extracted_texts.append(text2)
        except:
            pass
        
        # Method 3: Preprocessed with PSM 11 (sparse text)
        try:
            processed_image = preprocess_image_for_ocr(image_path)
            config3 = r'--oem 3 --psm 11'
            text3 = pytesseract.image_to_string(processed_image, config=config3, lang='eng')
            extracted_texts.append(text3)
        except:
            pass
        
        # Combine all extracted texts (longest one is usually best)
        extracted_text = max(extracted_texts, key=len) if extracted_texts else ""
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            return {
                'success': False,
                'text': extracted_text.strip() if extracted_text else '',
                'error': 'Could not extract meaningful text from image. Please ensure the image is clear and readable.'
            }
        
        print(f"✅ Extracted {len(extracted_text)} characters")
        print(f"📝 Sample text: {extracted_text[:300]}...")
        
        return {
            'success': True,
            'text': extracted_text.strip(),
            'error': None
        }
        
    except Exception as e:
        print(f"❌ OCR Error: {str(e)}")
        return {
            'success': False,
            'text': '',
            'error': f'OCR processing failed: {str(e)}'
        }


# Brand name to Generic name mapping (common Indian brands)
BRAND_TO_GENERIC_MAP = {
    # Antihistamines
    'levosiz': 'levocetirizine',
    'levocet': 'levocetirizine',
    'levocetrizine': 'levocetirizine',
    'cetrizine': 'cetirizine',
    'zyrtec': 'cetirizine',
    'cetzine': 'cetirizine',
    
    # Antifungals
    'forcan': 'fluconazole',
    'diflucan': 'fluconazole',
    'flucon': 'fluconazole',
    'zimig': 'ketoconazole',
    'ketocip': 'ketoconazole',
    'nizral': 'ketoconazole',
    
    # Antibiotics
    'mox': 'amoxicillin',
    'novamox': 'amoxicillin',
    'amoxil': 'amoxicillin',
    'zithromax': 'azithromycin',
    'azee': 'azithromycin',
    'azithral': 'azithromycin',
    'augmentin': 'amoxicillin + clavulanic acid',
    'cipcal': 'ciprofloxacin',
    'ciplox': 'ciprofloxacin',
    
    # Pain/Fever
    'crocin': 'paracetamol',
    'dolo': 'paracetamol',
    'calpol': 'paracetamol',
    'metacin': 'paracetamol',
    'brufen': 'ibuprofen',
    'combiflam': 'ibuprofen + paracetamol',
    
    # Blood pressure
    'amlodac': 'amlodipine',
    'amlong': 'amlodipine',
    'norvasc': 'amlodipine',
    'telma': 'telmisartan',
    
    # Cholesterol
    'atorva': 'atorvastatin',
    'lipitor': 'atorvastatin',
    'deplatt': 'clopidogrel',
    
    # Diabetes
    'glycomet': 'metformin',
    'glucophage': 'metformin',
    'januvia': 'sitagliptin',
    
    # Proton pump inhibitors
    'pan': 'pantoprazole',
    'pantocid': 'pantoprazole',
    'esoz': 'esomeprazole',
    'omez': 'omeprazole',
    'rablet': 'rabeprazole',
    
    # Antacids
    'digene': 'aluminium hydroxide + magnesium hydroxide',
    'gelusil': 'aluminium hydroxide + magnesium hydroxide',
}


def extract_potential_medicine_names(text):
    """
    Extract potential medicine names from OCR text using patterns
    Returns list of candidate medicine names
    """
    candidates = set()
    
    # Pattern 1: Words followed by dosage (most reliable)
    dosage_pattern = r'([A-Za-z][A-Za-z\-]{2,})\s*\d+\s*(?:mg|g|ml|mcg|%)'
    matches = re.findall(dosage_pattern, text, re.IGNORECASE)
    candidates.update([m.strip() for m in matches])
    
    # Pattern 2: Medicine keywords (Tablet, Capsule, Syrup, etc.)
    medicine_keywords = r'(?:Tablet|Tab|Capsule|Cap|Syrup|Syr|Injection|Inj|Cream|Drops)[:\s]+([A-Za-z][A-Za-z\-]{2,})'
    matches = re.findall(medicine_keywords, text, re.IGNORECASE)
    candidates.update([m.strip() for m in matches])
    
    # Pattern 3: Common medicine suffixes
    suffix_pattern = r'\b([A-Za-z]{4,}(?:cillin|mycin|zole|pril|olol|pine|mab|tide|oxin|tadine|cin))\b'
    matches = re.findall(suffix_pattern, text, re.IGNORECASE)
    candidates.update([m.strip() for m in matches])
    
    # Pattern 4: Capitalized words (3+ chars) that look like medicine names
    cap_pattern = r'\b([A-Z][a-z]{2,}(?:[A-Z][a-z]+)?)\b'
    matches = re.findall(cap_pattern, text)
    candidates.update([m.strip() for m in matches if len(m) >= 4])
    
    # Pattern 5: Words in medicine list context
    list_pattern = r'(?:Medication|Medicine|Drug|Prescribed).*?Name[:\s]+([A-Za-z][A-Za-z\-\s]{2,}?)(?:\n|\s{2,}|$)'
    matches = re.findall(list_pattern, text, re.IGNORECASE | re.DOTALL)
    candidates.update([m.strip() for m in matches])
    
    # Filter out common non-medicine words
    stop_words = {
        'patient', 'name', 'date', 'prescription', 'doctor', 'physician', 'address',
        'phone', 'email', 'signature', 'purpose', 'dosage', 'route', 'frequency',
        'oral', 'tablet', 'capsule', 'morning', 'evening', 'night', 'before', 'after',
        'food', 'daily', 'twice', 'thrice', 'removes', 'immune', 'system', 'none',
        'seafood', 'female', 'male', 'allergies', 'condition', 'health', 'notable',
        'information', 'list', 'prescribed', 'medications'
    }
    
    # Filter candidates
    filtered = []
    for candidate in candidates:
        candidate_clean = candidate.strip().lower()
        if (len(candidate_clean) >= 3 and 
            candidate_clean not in stop_words and
            not candidate_clean.isdigit()):
            filtered.append(candidate)
    
    # Also check for brand names and add their generic equivalents
    brand_matches = []
    for candidate in filtered:
        candidate_lower = candidate.lower().strip()
        # Check if it matches a brand name
        if candidate_lower in BRAND_TO_GENERIC_MAP:
            brand_matches.append(BRAND_TO_GENERIC_MAP[candidate_lower])
        # Check partial matches (brand name contains or is contained)
        for brand, generic in BRAND_TO_GENERIC_MAP.items():
            if len(candidate_lower) >= 4:
                if brand in candidate_lower or candidate_lower in brand:
                    if len(candidate_lower) >= len(brand) * 0.7:  # At least 70% of brand name
                        brand_matches.append(generic)
    
    # Combine original candidates with brand matches
    filtered.extend(brand_matches)
    
    return list(set(filtered))


def clean_text_for_matching(text):
    """
    Clean text for flexible medicine matching
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\-]', ' ', text)
    text = ' '.join(text.split())
    return text


def match_medicines_in_text(extracted_text):
    """
    Match medicine names from database with extracted text
    Uses multiple strategies for accurate matching
    """
    try:
        from .models import Medicine
        
        print(f"🔍 Searching for medicines in extracted text...")
        print(f"📄 Raw text preview: {extracted_text[:300]}...")
        
        # Extract potential medicine names from text
        candidates = extract_potential_medicine_names(extracted_text)
        print(f"💊 Found {len(candidates)} potential medicine names: {candidates}")
        
        # Clean text for matching
        cleaned_text = clean_text_for_matching(extracted_text)
        
        # Get all medicines from database
        all_medicines = Medicine.objects.all()
        
        matched_medicines = []
        medicine_ids = set()
        match_scores = {}
        
        # Strategy 1: Match extracted candidates against database
        for candidate in candidates:
            candidate_clean = clean_text_for_matching(candidate)
            
            for medicine in all_medicines:
                if medicine.id in medicine_ids:
                    continue
                
                med_name_clean = clean_text_for_matching(medicine.name)
                gen_name_clean = clean_text_for_matching(medicine.generic_name) if medicine.generic_name else ''
                
                match_score = 0
                match_type = None
                
                # Exact match (case-insensitive)
                if candidate_clean == med_name_clean or candidate_clean == gen_name_clean:
                    match_score = 100
                    match_type = "exact"
                
                # One contains the other
                elif (len(candidate_clean) >= 4 and 
                      (candidate_clean in med_name_clean or med_name_clean in candidate_clean)):
                    if len(candidate_clean) / max(len(med_name_clean), 1) > 0.7 or \
                       len(med_name_clean) / max(len(candidate_clean), 1) > 0.7:
                        match_score = 80
                        match_type = "contains"
                
                # Generic name contains candidate or vice versa
                elif gen_name_clean and len(candidate_clean) >= 4:
                    if candidate_clean in gen_name_clean or gen_name_clean in candidate_clean:
                        if len(candidate_clean) / max(len(gen_name_clean), 1) > 0.7 or \
                           len(gen_name_clean) / max(len(candidate_clean), 1) > 0.7:
                            match_score = 75
                            match_type = "generic"
                
                # Partial match - starts with same letters
                elif (len(candidate_clean) >= 4 and len(med_name_clean) >= 4 and
                      candidate_clean[:4] == med_name_clean[:4]):
                    match_score = 60
                    match_type = "partial"
                
                if match_score > 0:
                    if medicine.id not in match_scores or match_scores[medicine.id] < match_score:
                        match_scores[medicine.id] = match_score
                        if medicine.id in medicine_ids:
                            matched_medicines = [m for m in matched_medicines if m.id != medicine.id]
                            medicine_ids.remove(medicine.id)
                        
                        matched_medicines.append(medicine)
                        medicine_ids.add(medicine.id)
                        print(f"   ✓ Found [{match_type} {match_score}%]: {medicine.name} (matched with '{candidate}')")
        
        # Strategy 2: Direct search in cleaned text for database medicines
        for medicine in all_medicines:
            if medicine.id in medicine_ids:
                continue
            
            med_name_clean = clean_text_for_matching(medicine.name)
            gen_name_clean = clean_text_for_matching(medicine.generic_name) if medicine.generic_name else ''
            
            if len(med_name_clean) >= 3:
                if med_name_clean in cleaned_text:
                    matched_medicines.append(medicine)
                    medicine_ids.add(medicine.id)
                    print(f"   ✓ Found [direct]: {medicine.name}")
                    continue
                
                if gen_name_clean and len(gen_name_clean) >= 3 and gen_name_clean in cleaned_text:
                    matched_medicines.append(medicine)
                    medicine_ids.add(medicine.id)
                    print(f"   ✓ Found [direct-generic]: {medicine.name} ({medicine.generic_name})")
                    continue
        
        print(f"✅ Found {len(matched_medicines)} medicines in database")
        
        return matched_medicines
        
    except Exception as e:
        import traceback
        print(f"❌ Medicine matching error: {str(e)}")
        print(traceback.format_exc())
        return []


def process_prescription(file_path, db_medicines=None):
    """
    Legacy function - redirects to new simplified functions
    Kept for backward compatibility
    """
    result = extract_text_from_prescription(file_path)
    
    if not result['success']:
        return {
            'success': False,
            'error': result['error'],
            'text': result['text'],
            'medicines': []
        }
    
    medicines = match_medicines_in_text(result['text'])
    
    return {
        'success': True,
        'text': result['text'],
        'medicines': [m.name for m in medicines],
        'matched_meds': [m.name for m in medicines]
    }
