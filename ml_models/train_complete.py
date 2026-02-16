"""
Complete Training Script for Prescription Detection Model
Supports both fresh training and resuming from checkpoints
"""

import os
import sys
from pathlib import Path
import torch
from ultralytics import YOLO
from datetime import datetime
import yaml

# Configuration
class TrainingConfig:
    """Training configuration"""
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    ML_MODELS_DIR = Path(__file__).parent
    DATASET_DIR = ML_MODELS_DIR / "dataset" / "Doctor-Prescription-3-2"
    DATA_YAML = DATASET_DIR / "data.yaml"
    
    # Model paths
    MODEL_DIR = ML_MODELS_DIR / "prescription_detector"
    CHECKPOINT_DIR = MODEL_DIR / "prescription_v1" / "weights"
    FINAL_MODEL = MODEL_DIR / "prescription_detector.pt"
    
    # YOLOv8 base model
    BASE_MODEL = "yolov8n.pt"  # Nano model (fastest, smallest)
    # Options: yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
    
    # Training parameters
    EPOCHS = 150
    BATCH_SIZE = 16
    IMAGE_SIZE = 640
    PATIENCE = 50  # Early stopping patience
    
    # Hardware
    DEVICE = 0 if torch.cuda.is_available() else 'cpu'
    WORKERS = 4
    
    # Augmentation
    AUGMENT = True
    
    @classmethod
    def display(cls):
        """Display current configuration"""
        print("\n" + "="*60)
        print("TRAINING CONFIGURATION")
        print("="*60)
        print(f"Dataset:        {cls.DATASET_DIR}")
        print(f"Base Model:     {cls.BASE_MODEL}")
        print(f"Output Dir:     {cls.MODEL_DIR}")
        print(f"Epochs:         {cls.EPOCHS}")
        print(f"Batch Size:     {cls.BATCH_SIZE}")
        print(f"Image Size:     {cls.IMAGE_SIZE}")
        print(f"Device:         {'GPU (CUDA)' if cls.DEVICE == 0 else 'CPU'}")
        print(f"Early Stopping: {cls.PATIENCE} epochs")
        print("="*60 + "\n")


def check_dataset():
    """Check if dataset exists and is valid"""
    print("\n" + "="*60)
    print("CHECKING DATASET")
    print("="*60)
    
    config = TrainingConfig
    
    # Check if dataset directory exists
    if not config.DATASET_DIR.exists():
        print(f"❌ Dataset not found: {config.DATASET_DIR}")
        print("\n📥 DOWNLOAD INSTRUCTIONS:")
        print("1. Run: cd ml_models")
        print("2. Run: python download_dataset.py")
        print("   OR download manually from:")
        print("   https://app.roboflow.com/ds/k4U6JPdoCK?key=wZOHBUtAEb")
        print("\n3. Extract to: ml_models/dataset/Doctor-Prescription-3-2/")
        return False
    
    # Check data.yaml
    if not config.DATA_YAML.exists():
        print(f"❌ data.yaml not found: {config.DATA_YAML}")
        return False
    
    # Check train/valid/test folders
    splits = ['train', 'valid', 'test']
    for split in splits:
        images_dir = config.DATASET_DIR / split / 'images'
        labels_dir = config.DATASET_DIR / split / 'labels'
        
        if not images_dir.exists():
            print(f"❌ Missing {split}/images folder")
            return False
        
        if not labels_dir.exists():
            print(f"❌ Missing {split}/labels folder")
            return False
        
        # Count images
        num_images = len(list(images_dir.glob('*.jpg'))) + len(list(images_dir.glob('*.png')))
        num_labels = len(list(labels_dir.glob('*.txt')))
        
        print(f"✅ {split:8s}: {num_images:4d} images, {num_labels:4d} labels")
    
    print("\n✅ Dataset validation passed!")
    print("="*60 + "\n")
    return True


def find_latest_checkpoint():
    """Find the latest checkpoint to resume training"""
    config = TrainingConfig
    
    print("\n" + "="*60)
    print("CHECKING FOR EXISTING CHECKPOINTS")
    print("="*60)
    
    # Check if training already completed
    if config.FINAL_MODEL.exists():
        print(f"\n✅ Found completed model: {config.FINAL_MODEL.name}")
        file_size = config.FINAL_MODEL.stat().st_size / (1024 * 1024)
        print(f"   Size: {file_size:.2f} MB")
        
        response = input("\n⚠️  Model already exists. Do you want to:\n"
                        "   [1] Resume/Continue training (recommended)\n"
                        "   [2] Start fresh training (overwrites existing model)\n"
                        "   [3] Cancel\n"
                        "   Enter choice (1/2/3): ")
        
        if response == '3':
            print("\n❌ Training cancelled by user.")
            return None
        elif response == '2':
            print("\n🔄 Starting fresh training...")
            return config.BASE_MODEL
        else:
            print(f"\n🔄 Resuming training from: {config.FINAL_MODEL.name}")
            return str(config.FINAL_MODEL)
    
    # Check for checkpoint directory
    if config.CHECKPOINT_DIR.exists():
        # Look for last.pt (most recent checkpoint)
        last_checkpoint = config.CHECKPOINT_DIR / "last.pt"
        if last_checkpoint.exists():
            print(f"\n✅ Found checkpoint: last.pt")
            print(f"   Location: {last_checkpoint}")
            
            response = input("\n⚠️  Resume from this checkpoint? (y/n): ")
            if response.lower() == 'y':
                print(f"\n🔄 Resuming training from checkpoint...")
                return str(last_checkpoint)
            else:
                print("\n🔄 Starting fresh training...")
                return config.BASE_MODEL
    
    # No checkpoints found
    print("\n📝 No existing checkpoints found.")
    print(f"   Starting fresh training with {config.BASE_MODEL}")
    print("="*60 + "\n")
    return config.BASE_MODEL


def train_model(resume_from=None):
    """Train or resume training of the prescription detection model"""
    
    config = TrainingConfig
    
    print("\n" + "="*60)
    print("INITIALIZING TRAINING")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create output directory
    config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize model
    if resume_from and resume_from != config.BASE_MODEL:
        print(f"\n📦 Loading model from: {Path(resume_from).name}")
        model = YOLO(resume_from)
        print("✅ Model loaded successfully!")
    else:
        print(f"\n📦 Loading base model: {config.BASE_MODEL}")
        model = YOLO(config.BASE_MODEL)
        print("✅ Base model loaded successfully!")
    
    print("\n" + "="*60)
    print("STARTING TRAINING")
    print("="*60)
    print(f"🎯 Target: {config.EPOCHS} epochs")
    print(f"💾 Checkpoints will be saved to: {config.CHECKPOINT_DIR}")
    print(f"⏱️  Training started at: {datetime.now().strftime('%H:%M:%S')}")
    print("="*60 + "\n")
    
    try:
        # Train the model
        results = model.train(
            data=str(config.DATA_YAML),
            epochs=config.EPOCHS,
            imgsz=config.IMAGE_SIZE,
            batch=config.BATCH_SIZE,
            device=config.DEVICE,
            workers=config.WORKERS,
            patience=config.PATIENCE,
            save=True,
            save_period=10,  # Save checkpoint every 10 epochs
            project=str(config.MODEL_DIR),
            name='prescription_v1',
            exist_ok=True,
            pretrained=True,
            optimizer='auto',
            verbose=True,
            seed=42,
            deterministic=False,
            single_cls=True,  # Single class detection (prescription)
            rect=False,
            cos_lr=True,
            close_mosaic=10,
            resume=resume_from != config.BASE_MODEL,  # Resume if checkpoint
            amp=True,  # Automatic Mixed Precision
            fraction=1.0,
            profile=False,
            freeze=None,
            lr0=0.01,
            lrf=0.01,
            momentum=0.937,
            weight_decay=0.0005,
            warmup_epochs=3.0,
            warmup_momentum=0.8,
            warmup_bias_lr=0.1,
            box=7.5,
            cls=0.5,
            dfl=1.5,
            plots=True,
            augment=config.AUGMENT,
        )
        
        print("\n" + "="*60)
        print("✅ TRAINING COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        # Save final model
        best_model_path = config.CHECKPOINT_DIR / "best.pt"
        if best_model_path.exists():
            print(f"\n💾 Saving final model to: {config.FINAL_MODEL}")
            
            # Copy best model to final location
            import shutil
            shutil.copy(best_model_path, config.FINAL_MODEL)
            
            print(f"✅ Final model saved: {config.FINAL_MODEL.name}")
            print(f"   Size: {config.FINAL_MODEL.stat().st_size / (1024*1024):.2f} MB")
        
        # Display results
        print("\n" + "="*60)
        print("TRAINING RESULTS")
        print("="*60)
        
        # Load and display metrics
        results_csv = config.MODEL_DIR / "prescription_v1" / "results.csv"
        if results_csv.exists():
            import pandas as pd
            try:
                df = pd.read_csv(results_csv)
                last_row = df.iloc[-1]
                
                print(f"\nFinal Metrics (Epoch {int(last_row.get('epoch', 0))}):")
                print(f"  Precision: {last_row.get('metrics/precision(B)', 0):.4f}")
                print(f"  Recall:    {last_row.get('metrics/recall(B)', 0):.4f}")
                print(f"  mAP50:     {last_row.get('metrics/mAP50(B)', 0):.4f}")
                print(f"  mAP50-95:  {last_row.get('metrics/mAP50-95(B)', 0):.4f}")
            except Exception as e:
                print(f"  (Could not load metrics: {e})")
        
        print("\n📊 Training artifacts saved to:")
        print(f"   {config.MODEL_DIR / 'prescription_v1'}")
        print("\n📈 View training plots:")
        print(f"   - Results:    {config.MODEL_DIR / 'prescription_v1' / 'results.png'}")
        print(f"   - Confusion:  {config.MODEL_DIR / 'prescription_v1' / 'confusion_matrix.png'}")
        print(f"   - PR Curve:   {config.MODEL_DIR / 'prescription_v1' / 'PR_curve.png'}")
        print("="*60 + "\n")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user!")
        print("💾 Progress has been saved as checkpoint.")
        print("🔄 Run this script again to resume training from the last checkpoint.")
        return False
        
    except Exception as e:
        print(f"\n\n❌ Training failed with error:")
        print(f"   {str(e)}")
        print("\n💾 Any progress has been saved as checkpoint.")
        print("🔄 Run this script again to resume training.")
        raise


def main():
    """Main training pipeline"""
    
    print("\n" + "="*60)
    print("PRESCRIPTION DETECTION MODEL TRAINING")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Display configuration
    TrainingConfig.display()
    
    # Step 1: Check dataset
    if not check_dataset():
        print("\n❌ Dataset check failed. Please fix issues and try again.")
        return 1
    
    # Step 2: Find checkpoint or start fresh
    resume_from = find_latest_checkpoint()
    if resume_from is None:
        return 0  # User cancelled
    
    # Step 3: Train model
    start_time = datetime.now()
    success = train_model(resume_from)
    end_time = datetime.now()
    
    if success:
        duration = end_time - start_time
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        
        print("\n" + "="*60)
        print("🎉 ALL DONE!")
        print("="*60)
        print(f"Training Duration: {hours}h {minutes}m")
        print(f"Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n✅ Model ready at: {TrainingConfig.FINAL_MODEL}")
        print("\n💡 Next Steps:")
        print("   1. Test the model: python test_model_direct.py")
        print("   2. Run inference: python prescription_inference.py")
        print("   3. Use in Django app (already integrated)")
        print("="*60 + "\n")
        return 0
    else:
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
