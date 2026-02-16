"""
Real-Time Prescription Inference
Uses trained YOLOv8 model to detect and extract medicine names from prescriptions
Integrates with Django for real-time prescription analysis
"""

import os
import cv2
import numpy as np
from pathlib import Path
import pytesseract
from PIL import Image
import re

class PrescriptionDetector:
    """
    Real-time prescription detector using trained YOLO model
    Detects prescription regions and extracts medicine names using OCR
    """
    
    def __init__(self, model_path=None):
        """Initialize detector with trained model"""
        
        if model_path is None:
            # Default model path
            current_dir = Path(__file__).parent
            model_path = current_dir / 'prescription_detector' / 'prescription_detector.pt'
        
        self.model_path = Path(model_path)
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load trained YOLO model"""
        try:
            from ultralytics import YOLO
            
            if not self.model_path.exists():
                raise FileNotFoundError(
                    f"Model not found: {self.model_path}\n"
                    f"Please train the model first: python train_prescription_model.py"
                )
            
            print(f"📦 Loading prescription detection model from: {self.model_path}")
            self.model = YOLO(str(self.model_path))
            print("✅ Model loaded successfully!")
            
        except ImportError:
            print("❌ Ultralytics not installed. Install with: pip install ultralytics")
            raise
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def preprocess_image(self, image):
        """Preprocess image for better OCR results"""
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(denoised)
        
        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(
            contrast, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to remove noise
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)
        
        return processed
    
    def extract_text_from_region(self, image, bbox):
        """Extract text from detected bounding box using OCR"""
        
        x1, y1, x2, y2 = bbox
        
        # Crop region
        region = image[int(y1):int(y2), int(x1):int(x2)]
        
        if region.size == 0:
            return ""
        
        # Preprocess region
        processed = self.preprocess_image(region)
        
        # OCR with Tesseract
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(processed, config=custom_config)
        
        return text.strip()
    
    def extract_medicine_names(self, text):
        """Extract medicine names from OCR text using patterns"""
        
        # Common medicine name patterns
        # Medicines often start with capital letter, may have numbers
        medicine_pattern = r'\b[A-Z][a-z]{2,}(?:[A-Z][a-z]+)?\b'
        
        # Extract potential medicine names
        potential_medicines = re.findall(medicine_pattern, text)
        
        # Filter out common words
        common_words = {
            'Tab', 'Cap', 'Syrup', 'Tablet', 'Capsule', 'Injection',
            'Morning', 'Evening', 'Night', 'After', 'Before', 'Food',
            'Daily', 'Times', 'Days', 'Weeks', 'Month', 'Take', 'Dose',
            'Patient', 'Doctor', 'Date', 'Name', 'Age', 'Address'
        }
        
        medicines = [
            med for med in potential_medicines
            if med not in common_words and len(med) > 3
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_medicines = []
        for med in medicines:
            med_lower = med.lower()
            if med_lower not in seen:
                seen.add(med_lower)
                unique_medicines.append(med)
        
        return unique_medicines
    
    def detect_and_extract(self, image_path, confidence=0.01, top_n=10):
        """
        Detect prescription elements and extract medicine names using AI model
        ALWAYS returns top N detections, even with low confidence
        
        Args:
            image_path: Path to prescription image
            confidence: Detection confidence threshold (0-1) - very low to catch all detections
            top_n: Number of top detections to return (default 10)
        
        Returns:
            dict: Detection results with medicines and metadata
        """
        
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Read image
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Cannot read image: {image_path}")
        
        print(f"🔍 Running AI detection (will return top {top_n} medicines)")
        
        # Run detection with very low confidence to catch everything
        results = self.model.predict(
            source=image,
            conf=confidence,
            verbose=False,
            max_det=300  # Allow more detections per image
        )
        
        # Extract ALL detections and sort by confidence
        all_detections = []
        
        for result in results:
            boxes = result.boxes
            
            if len(boxes) > 0:
                print(f"📦 Found {len(boxes)} raw detections")
            
            for i, box in enumerate(boxes):
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = result.names[cls]  # This IS the medicine name!
                
                all_detections.append({
                    'name': class_name,
                    'confidence': conf,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                })
        
        # Sort by confidence (highest first) and take top N
        all_detections.sort(key=lambda x: x['confidence'], reverse=True)
        top_detections = all_detections[:top_n]
        
        # Extract medicine names from top detections
        detections = []
        all_medicines = []
        detected_medicines_with_conf = []
        
        if top_detections:
            print(f"✅ Returning top {len(top_detections)} medicine suggestions:")
            for det in top_detections:
                name = det['name']
                conf = det['confidence']
                
                # Add to results
                all_medicines.append(name)
                detected_medicines_with_conf.append({
                    'name': name,
                    'confidence': conf
                })
                
                # Mark confidence level
                if conf >= 0.10:
                    marker = "✅"
                elif conf >= 0.05:
                    marker = "⚠️"
                else:
                    marker = "💡"
                    
                print(f"   {marker} {name} (confidence: {conf:.3f})")
                
                detections.append({
                    'class': name,
                    'confidence': conf,
                    'bbox': det['bbox'],
                    'medicine_name': name
                })
        else:
            print("❌ No detections at all - image may not contain prescriptions")
        
        # Remove duplicate medicines while preserving order
        unique_medicines = list(dict.fromkeys(all_medicines))
        
        if unique_medicines:
            print(f"✅ Suggesting {len(unique_medicines)} medicine(s) from prescription")
            if top_detections and top_detections[0]['confidence'] < 0.10:
                print("⚠️  Note: Low confidence - these are AI suggestions, verify manually")
        else:
            print("❌ No detections found - prescription may be blank or unreadable")
        
        return {
            'success': True if unique_medicines else False,
            'medicines': unique_medicines,
            'detections': detections,
            'detected_medicines': detected_medicines_with_conf,
            'full_text': f"Suggested medicines: {', '.join(unique_medicines)}" if unique_medicines else "No suggestions available",
            'num_detections': len(detections),
            'model_used': 'YOLOv8 AI Detection (Top Suggestions)',
            'low_confidence_warning': top_detections[0]['confidence'] < 0.10 if top_detections else False
        }
    
    def process_for_django(self, image_path, db_medicines=None):
        """
        Process prescription for Django integration with fuzzy matching
        
        Args:
            image_path: Path to prescription image
            db_medicines: List of medicine names from database for fuzzy matching
        
        Returns:
            dict: Results compatible with Django views
        """
        
        try:
            # Detect and extract
            result = self.detect_and_extract(image_path)
            
            if not result['success']:
                print("⚠️  AI model did not detect medicines with confidence")
                print("🔄 Attempting full OCR extraction as fallback...")
                
                # Try full image OCR extraction as fallback
                try:
                    image = cv2.imread(str(image_path))
                    processed = self.preprocess_image(image)
                    custom_config = r'--oem 3 --psm 6'
                    full_text = pytesseract.image_to_string(processed, config=custom_config)
                    
                    if full_text.strip():
                        medicines = self.extract_medicine_names(full_text)
                        if medicines:
                            print(f"✅ OCR fallback found {len(medicines)} potential medicines")
                            result = {
                                'success': True,
                                'medicines': medicines,
                                'full_text': full_text,
                                'detections': [],
                                'num_detections': 0,
                                'model_used': 'OCR Fallback',
                                'low_confidence_warning': True
                            }
                        else:
                            print("⚠️  OCR extracted text but no medicine names found")
                            return {
                                'success': False,
                                'error': 'No medicine names detected. Please ensure prescription is clear and readable.',
                                'medicines': [],
                                'text': full_text
                            }
                    else:
                        return {
                            'success': False,
                            'error': 'Could not extract text from image. Please ensure image is clear.',
                            'medicines': [],
                            'text': ''
                        }
                except Exception as ocr_error:
                    print(f"❌ OCR fallback failed: {ocr_error}")
                    return {
                        'success': False,
                        'error': f'OCR processing failed: {str(ocr_error)}',
                        'medicines': [],
                        'text': ''
                    }
                
            if not result['success']:
                return result
            
            # Fuzzy match with database if provided
            matched_medicines = []
            fuzzy_matches = {}
            
            if db_medicines and result['medicines']:
                from rapidfuzz import process, fuzz
                
                for medicine in result['medicines']:
                    # Find best match in database
                    matches = process.extract(
                        medicine,
                        db_medicines,
                        scorer=fuzz.ratio,
                        limit=3
                    )
                    
                    # Accept matches with score > 70
                    best_matches = [m for m in matches if m[1] > 70]
                    
                    if best_matches:
                        best_match = best_matches[0][0]
                        matched_medicines.append(best_match)
                        fuzzy_matches[medicine] = {
                            'best_match': best_match,
                            'score': best_matches[0][1],
                            'alternatives': [
                                {'name': m[0], 'score': m[1]}
                                for m in best_matches[1:]
                            ]
                        }
            
            return {
                'success': True,
                'medicines': result['medicines'],
                'matched_meds': matched_medicines if matched_medicines else result['medicines'],
                'fuzzy_matches': fuzzy_matches,
                'text': result['full_text'],
                'detections': result['detections'],
                'num_detections': result['num_detections'],
                'model_used': result['model_used']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'medicines': [],
                'text': ''
            }


# Singleton instance
_detector_instance = None

def get_detector():
    """Get or create detector singleton"""
    global _detector_instance
    
    if _detector_instance is None:
        _detector_instance = PrescriptionDetector()
    
    return _detector_instance


def process_prescription_realtime(image_path, db_medicines=None):
    """
    Process prescription using trained AI model (Django-compatible function)
    Uses YOLOv8 model to detect medicine names directly from the image
    
    Args:
        image_path: Path to prescription image
        db_medicines: List of medicine names from database (optional for fuzzy matching)
    
    Returns:
        dict: Processing results with extracted medicines
    """
    
    try:
        print("🤖 Processing prescription with AI model...")
        detector = get_detector()
        result = detector.process_for_django(image_path, db_medicines)
        
        if result['success'] and result['medicines']:
            print(f"✅ Successfully detected {len(result['medicines'])} medicines")
        else:
            print("⚠️  No medicines detected in this prescription")
            
        return result
        
    except Exception as e:
        print(f"❌ Error processing prescription: {e}")
        return {
            'success': False,
            'error': str(e),
            'medicines': [],
            'text': 'Error processing prescription with AI model'
        }


