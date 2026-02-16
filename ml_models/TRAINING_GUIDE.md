# 🎯 Complete Training Guide

## Quick Start

```bash
cd ml_models
python train_complete.py
```

## What It Does

### ✅ Automatic Features:
- **Detects existing models** - Asks if you want to resume or start fresh
- **Finds checkpoints** - Automatically resumes from last checkpoint
- **Validates dataset** - Checks if dataset is downloaded and valid
- **Saves progress** - Saves checkpoint every 10 epochs
- **Early stopping** - Stops if no improvement for 50 epochs
- **GPU support** - Automatically uses GPU if available
- **Error handling** - Can resume even after crashes

## Training Scenarios

### Scenario 1: First Time Training
```bash
python train_complete.py
```
- Downloads YOLOv8n base model
- Starts training from epoch 0
- Saves checkpoints every 10 epochs
- Saves best model as `prescription_detector.pt`

### Scenario 2: Resume After Interruption
```bash
python train_complete.py
```
- Detects existing checkpoint (`last.pt`)
- Asks if you want to resume
- Continues from where it stopped
- Preserves all previous progress

### Scenario 3: Continue Training Completed Model
```bash
python train_complete.py
```
- Detects completed model (`prescription_detector.pt`)
- Asks if you want to continue training
- Can train for more epochs to improve accuracy

## Configuration

Edit `train_complete.py` to customize:

```python
class TrainingConfig:
    EPOCHS = 150          # Total epochs
    BATCH_SIZE = 16       # Batch size
    IMAGE_SIZE = 640      # Image size
    PATIENCE = 50         # Early stopping patience
    BASE_MODEL = "yolov8n.pt"  # Model size
```

### Model Options:
- `yolov8n.pt` - Nano (fastest, smallest, good for CPU)
- `yolov8s.pt` - Small (balanced)
- `yolov8m.pt` - Medium (better accuracy)
- `yolov8l.pt` - Large (high accuracy)
- `yolov8x.pt` - Extra large (best accuracy, slowest)

## Dataset Requirements

The script expects this structure:
```
ml_models/
└── dataset/
    └── Doctor-Prescription-3-2/
        ├── data.yaml
        ├── train/
        │   ├── images/
        │   └── labels/
        ├── valid/
        │   ├── images/
        │   └── labels/
        └── test/
            ├── images/
            └── labels/
```

If dataset is missing, run:
```bash
python download_dataset.py
```

Or download manually from:
https://app.roboflow.com/ds/k4U6JPdoCK?key=wZOHBUtAEb

## Output Files

After training, you'll get:

### Main Model:
```
ml_models/prescription_detector/prescription_detector.pt
```

### Training Files:
```
ml_models/prescription_detector/prescription_v1/
├── weights/
│   ├── best.pt       # Best performing model
│   ├── last.pt       # Most recent checkpoint
│   ├── epoch10.pt    # Checkpoint at epoch 10
│   └── epoch20.pt    # Checkpoint at epoch 20
├── results.csv       # Training metrics
├── results.png       # Training curves
├── confusion_matrix.png
├── PR_curve.png      # Precision-Recall
├── F1_curve.png
└── train_batch0.jpg  # Training examples
```

## Training Time Estimates

### With GPU (NVIDIA RTX 3060 or better):
- 100 epochs: ~2-3 hours
- 150 epochs: ~3-4 hours

### With CPU (Intel i7 or better):
- 100 epochs: ~10-15 hours
- 150 epochs: ~15-20 hours

## Monitoring Progress

During training, you'll see:
```
Epoch    GPU_mem    box_loss    cls_loss    dfl_loss    Instances    Size
1/150      2.5G      1.234      0.567      1.012         45        640
```

- `GPU_mem` - GPU memory usage
- `box_loss` - Bounding box accuracy
- `cls_loss` - Classification accuracy
- `dfl_loss` - Distribution focal loss
- `Instances` - Objects per batch
- `Size` - Image size

## Stopping Training

### Safe Stop:
Press `Ctrl+C` once - Will save checkpoint and exit cleanly

### Force Stop:
Press `Ctrl+C` twice - Immediate exit (progress may be lost)

## Resume Training After Stop

Just run the script again:
```bash
python train_complete.py
```

It will automatically detect the checkpoint and ask if you want to resume.

## Troubleshooting

### Error: "Dataset not found"
**Solution:**
```bash
cd ml_models
python download_dataset.py
```

### Error: "CUDA out of memory"
**Solution:** Reduce batch size in config:
```python
BATCH_SIZE = 8  # or even 4
```

### Error: "No module named 'ultralytics'"
**Solution:**
```bash
pip install ultralytics torch torchvision
```

### Training is too slow
**Solutions:**
1. Reduce image size: `IMAGE_SIZE = 416`
2. Reduce batch size: `BATCH_SIZE = 8`
3. Use smaller model: `BASE_MODEL = "yolov8n.pt"`

## After Training

### Test the model:
```bash
python test_model_direct.py
```

### Use in application:
The trained model is automatically used by the Django app at:
```
http://localhost:8000/prescription-scanner/
```

### Check model performance:
```bash
python -c "from ultralytics import YOLO; model = YOLO('prescription_detector/prescription_detector.pt'); model.val()"
```

## Advanced Usage

### Change training parameters:
```python
# In train_complete.py, modify TrainingConfig class
EPOCHS = 200          # Train longer
BATCH_SIZE = 32       # Larger batches (needs more memory)
IMAGE_SIZE = 1280     # Higher resolution (slower but more accurate)
PATIENCE = 30         # Stop sooner if no improvement
```

### Use different base model:
```python
BASE_MODEL = "yolov8m.pt"  # Medium model (better accuracy)
```

### Train on specific GPU:
```python
DEVICE = 0  # First GPU
DEVICE = 1  # Second GPU
DEVICE = 'cpu'  # Force CPU
```

## Performance Tips

1. **Use GPU** - 5-10x faster than CPU
2. **Larger batch size** - More stable training (if GPU has memory)
3. **More epochs** - Better accuracy (with patience parameter)
4. **Data augmentation** - Already enabled by default
5. **Early stopping** - Prevents overfitting (patience=50)

## Expected Results

After 100-150 epochs, you should see:
- **mAP50**: 0.85-0.95 (85-95% accuracy)
- **Precision**: 0.80-0.90
- **Recall**: 0.80-0.90

If results are lower:
- Train for more epochs
- Use larger model (yolov8m.pt)
- Add more training data
- Check data quality

---

## Need Help?

1. Check `results.csv` for metrics
2. View `results.png` for training curves
3. Check `confusion_matrix.png` for errors
4. Run `python test_model_direct.py` to test

**Ready to train? Run: `python train_complete.py`** 🚀
