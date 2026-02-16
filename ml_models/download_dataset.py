"""
Download Doctor Prescription Dataset from Roboflow
"""
import os
from roboflow import Roboflow

def download_dataset():
    """Download the prescription detection dataset from Roboflow"""
    
    print("=" * 60)
    print("DOWNLOADING DOCTOR PRESCRIPTION DATASET FROM ROBOFLOW")
    print("=" * 60)
    
    # Set up paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(current_dir, "dataset")
    
    print(f"\n📁 Dataset will be downloaded to: {dataset_dir}")
    
    # Create dataset directory if it doesn't exist
    os.makedirs(dataset_dir, exist_ok=True)
    
    try:
        print("\n🔄 Connecting to Roboflow...")
        
        # Initialize Roboflow with API key
        rf = Roboflow(api_key="wZOHBUtAEb")
        
        print("✅ Connected to Roboflow successfully!")
        print("\n🔄 Downloading dataset...")
        
        # Access the workspace and project
        project = rf.workspace("ds").project("doctor-prescription-3-2")
        
        # Download the dataset in YOLOv8 format
        dataset = project.version(2).download(
            model_format="yolov8",
            location=dataset_dir,
            overwrite=False
        )
        
        print("\n✅ Dataset downloaded successfully!")
        print(f"\n📂 Dataset location: {dataset.location}")
        print(f"📄 Data config: {os.path.join(dataset.location, 'data.yaml')}")
        
        # Print dataset structure
        print("\n📊 Dataset Structure:")
        for split in ['train', 'valid', 'test']:
            split_path = os.path.join(dataset.location, split)
            if os.path.exists(split_path):
                images_path = os.path.join(split_path, 'images')
                labels_path = os.path.join(split_path, 'labels')
                
                if os.path.exists(images_path):
                    num_images = len([f for f in os.listdir(images_path) if f.endswith(('.jpg', '.jpeg', '.png'))])
                    print(f"  - {split}: {num_images} images")
        
        print("\n" + "=" * 60)
        print("✅ DATASET DOWNLOAD COMPLETE!")
        print("=" * 60)
        print("\n💡 Next Steps:")
        print("   1. Check the dataset in: ml_models/dataset/Doctor-Prescription-3-2/")
        print("   2. Review data.yaml file")
        print("   3. Train model: python train_prescription_model.py")
        print("\n")
        
        return dataset
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\n" + "=" * 60)
        print("MANUAL DOWNLOAD INSTRUCTIONS:")
        print("=" * 60)
        print("\n1. Visit: https://app.roboflow.com/ds/k4U6JPdoCK?key=wZOHBUtAEb")
        print("2. Click 'Download Dataset'")
        print("3. Select format: YOLOv8")
        print("4. Download and extract to: ml_models/dataset/")
        print("5. Ensure folder structure:")
        print("   ml_models/")
        print("   └── dataset/")
        print("       └── Doctor-Prescription-3-2/")
        print("           ├── data.yaml")
        print("           ├── train/")
        print("           ├── valid/")
        print("           └── test/")
        print("\n")
        raise

if __name__ == "__main__":
    try:
        # Check if roboflow is installed
        try:
            import roboflow
            print("✅ Roboflow library found")
        except ImportError:
            print("❌ Roboflow library not found!")
            print("\n📦 Installing roboflow...")
            import subprocess
            subprocess.check_call(['pip', 'install', 'roboflow'])
            print("✅ Roboflow installed successfully!")
            print("🔄 Please run this script again.\n")
            exit(0)
        
        # Download dataset
        download_dataset()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Download cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        exit(1)
