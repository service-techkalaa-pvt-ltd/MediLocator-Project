"""
Medicine information knowledge base for chatbot
Maps medicine names/generics to usage, dosage, side effects, precautions
"""

MEDICINE_KNOWLEDGE_BASE = {
    # Painkillers & Fever
    "paracetamol": {
        "names": ["paracetamol", "acetaminophen", "tylenol"],
        "generic": "Paracetamol",
        "uses": "Relief of mild to moderate pain and fever. Used for headaches, muscle aches, fever, and common cold symptoms.",
        "dosage": "Adults: 500-1000 mg every 4-6 hours (max 4000 mg/day). Children: Follow pediatrician's advice based on age/weight.",
        "side_effects": "Generally well-tolerated. Rare: nausea, rash, liver damage (with overdose).",
        "precautions": "Avoid overdose. Don't combine with other paracetamol-containing products. Inform doctor if you have liver disease.",
        "type": "Analgesic & Antipyretic"
    },
    "crocin": {
        "names": ["crocin", "crocin 650"],
        "generic": "Paracetamol",
        "uses": "Relief of mild to moderate pain and fever. Used for headaches, fever, muscle aches.",
        "dosage": "1-2 tablets (500-650 mg) every 4-6 hours as needed. Max 4 grams per day.",
        "side_effects": "Generally safe. Rare: allergic reactions, rash.",
        "precautions": "Avoid if allergic to paracetamol. Not recommended during pregnancy without doctor's advice.",
        "type": "Pain & Fever Relief",
        "brand_for": "Paracetamol"
    },
    "dolo": {
        "names": ["dolo", "dolo 650"],
        "generic": "Paracetamol",
        "uses": "Treatment of mild to moderate pain and fever.",
        "dosage": "1 tablet (650 mg) every 4-6 hours. Max 4 tablets daily.",
        "side_effects": "Rare: nausea, dizziness, liver toxicity.",
        "precautions": "Avoid with liver disease. Don't exceed recommended dose.",
        "type": "Analgesic",
        "brand_for": "Paracetamol"
    },
    
    # Antibiotics
    "amoxicillin": {
        "names": ["amoxicillin", "amoxil", "mox", "novamox"],
        "generic": "Amoxicillin",
        "uses": "Treatment of bacterial infections including ear infections, respiratory infections, urinary tract infections, and skin infections.",
        "dosage": "Adults: 250-500 mg three times daily or 500-875 mg twice daily. Infection-specific and duration typically 7-14 days.",
        "side_effects": "Nausea, diarrhea, allergic reactions, rash. Serious: severe allergic reactions in penicillin-sensitive patients.",
        "precautions": "AVOID if allergic to penicillin or cephalosporins. Inform doctor about allergies. May reduce birth control effectiveness.",
        "type": "Antibiotic (Penicillin class)"
    },
    "azithromycin": {
        "names": ["azithromycin", "azee", "zithromax", "azithral"],
        "generic": "Azithromycin",
        "uses": "Treatment of bacterial infections (respiratory, skin, ear) and certain sexually transmitted infections.",
        "dosage": "Adults: 500 mg day 1, then 250 mg daily for 4 days OR 500 mg every 7 days for 3 weeks.",
        "side_effects": "Nausea, diarrhea, abdominal pain, headache.",
        "precautions": "Consult doctor about liver/kidney disease. Not suitable in certain heart conditions.",
        "type": "Antibiotic (Macrolide class)"
    },
    
    # Antifungals
    "fluconazole": {
        "names": ["fluconazole", "forcan", "diflucan"],
        "generic": "Fluconazole",
        "uses": "Treatment of fungal infections including yeast infections, candidiasis, and other fungal infections.",
        "dosage": "Infection-dependent: 150-400 mg daily or as a single dose. Duration 2-4 weeks typically.",
        "side_effects": "Nausea, abdominal pain, headache, rash.",
        "precautions": "Inform doctor about liver disease or other medications. May interact with certain drugs.",
        "type": "Antifungal"
    },
    "ketoconazole": {
        "names": ["ketoconazole", "zimig", "ketocip", "nizral"],
        "generic": "Ketoconazole",
        "uses": "Treatment of various fungal infections including skin infections, candidiasis, and dandruff.",
        "dosage": "Topical (cream): Apply to affected area 1-2 times daily OR Oral: 200-400 mg daily (doctor-prescribed).",
        "side_effects": "Topical: minimal. Oral: nausea, headache, liver issues.",
        "precautions": "Avoid if allergic. Oral form requires liver function monitoring. Pregnancy: consult doctor.",
        "type": "Antifungal"
    },
    
    # Antihistamines
    "cetirizine": {
        "names": ["cetirizine", "zyrtec", "cetzine"],
        "generic": "Cetirizine",
        "uses": "Relief of allergy symptoms: sneezing, runny nose, itchy eyes, hives.",
        "dosage": "Adults & children ≥6 years: 10 mg once daily. May take 20 minutes to 1 hour.",
        "side_effects": "Drowsiness (less than older antihistamines), dry mouth, headache.",
        "precautions": "Don't drive if drowsy. Inform doctor about kidney disease.",
        "type": "Antihistamine"
    },
    "levocetirizine": {
        "names": ["levocetirizine", "levosiz", "levocet"],
        "generic": "Levocetirizine",
        "uses": "Relief of allergy symptoms: allergic rhinitis, urticaria (hives), itching.",
        "dosage": "Adults: 5 mg once daily in evening. May also take as 2.5 mg twice daily.",
        "side_effects": "Minimal drowsiness, dry mouth, headache.",
        "precautions": "Don't drive if drowsy. Dose adjustment needed for kidney disease.",
        "type": "Antihistamine (second-generation)"
    },
    
    # Blood Pressure
    "amlodipine": {
        "names": ["amlodipine", "amlong", "amlodac", "norvasc"],
        "generic": "Amlodipine",
        "uses": "Treatment of high blood pressure and angina (chest pain) by relaxing blood vessels.",
        "dosage": "Adults: 5-10 mg once daily. Effects typically seen within 1-2 weeks.",
        "side_effects": "Swelling in feet/legs, headache, flushing, fatigue.",
        "precautions": "Don't stop abruptly. Inform doctor about liver disease or heart problems. May cause dizziness.",
        "type": "Calcium Channel Blocker (Blood Pressure)"
    },
    
    # Cholesterol
    "atorvastatin": {
        "names": ["atorvastatin", "lipitor", "atorva"],
        "generic": "Atorvastatin",
        "uses": "Lowering high cholesterol and triglycerides. Reduces risk of heart disease and stroke.",
        "dosage": "Adults: 10-80 mg once daily, usually in evening.",
        "side_effects": "Muscle pain, liver enzyme changes, headache, nausea.",
        "precautions": "Regular liver function tests needed. Avoid in pregnancy. May interact with other drugs.",
        "type": "Statin (Cholesterol Management)"
    },
}

def get_medicine_info(medicine_name: str) -> dict:
    """
    Get medicine information by name (brand or generic)
    Returns dict with usage, dosage, side effects, precautions
    """
    if not medicine_name:
        return None
    
    search_term = medicine_name.lower().strip()
    
    # Direct lookup
    for key, info in MEDICINE_KNOWLEDGE_BASE.items():
        if search_term == key.lower():
            return info
        if search_term in info.get('names', []):
            return info
    
    # Partial match
    for key, info in MEDICINE_KNOWLEDGE_BASE.items():
        if search_term in key.lower() or key.lower() in search_term:
            return info
        for alt_name in info.get('names', []):
            if search_term in alt_name or alt_name in search_term:
                return info
    
    return None


def format_medicine_info(info: dict, medicine_name: str = '') -> str:
    """
    Format medicine info into a user-friendly HTML response
    """
    if not info:
        return None
    
    html = f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
        <h3 style="margin: 0 0 0.5rem 0; font-size: 1.2rem;">💊 {medicine_name or info['generic']}</h3>
        <p style="margin: 0; opacity: 0.95; font-size: 0.9rem;">{info.get('type', 'Medicine')}</p>
    </div>
    
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <div style="margin-bottom: 0.8rem;">
            <h4 style="color: #667eea; margin: 0 0 0.5rem 0; font-size: 0.95rem;">📋 What is it used for?</h4>
            <p style="margin: 0; color: #333; line-height: 1.6; font-size: 0.9rem;">{info.get('uses', 'N/A')}</p>
        </div>
        
        <div style="margin-bottom: 0.8rem;">
            <h4 style="color: #667eea; margin: 0 0 0.5rem 0; font-size: 0.95rem;">💊 Typical Dosage</h4>
            <p style="margin: 0; color: #333; line-height: 1.6; font-size: 0.9rem;">{info.get('dosage', 'N/A')}</p>
        </div>
        
        <div style="margin-bottom: 0.8rem;">
            <h4 style="color: #667eea; margin: 0 0 0.5rem 0; font-size: 0.95rem;">⚠️ Side Effects</h4>
            <p style="margin: 0; color: #333; line-height: 1.6; font-size: 0.9rem;">{info.get('side_effects', 'N/A')}</p>
        </div>
        
        <div>
            <h4 style="color: #667eea; margin: 0 0 0.5rem 0; font-size: 0.95rem;">✓ Precautions</h4>
            <p style="margin: 0; color: #333; line-height: 1.6; font-size: 0.9rem;">{info.get('precautions', 'N/A')}</p>
        </div>
    </div>
    
    <div style="background: #ede9fe; border-left: 4px solid #7c3aed; padding: 0.8rem; border-radius: 6px; margin-bottom: 1rem;">
        <p style="margin: 0; color: #6b21a8; font-size: 0.85rem;"><strong>⚕️ Medical Advice:</strong> Always consult your doctor or pharmacist before taking any medicine. This information is for educational purposes only.</p>
    </div>
    """
    return html
