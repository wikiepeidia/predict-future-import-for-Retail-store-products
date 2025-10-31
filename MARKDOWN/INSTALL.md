# Installation Guide - Deep Learning Models

## Quick Install Script

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Verify installation
python test_models.py

# 3. Generate dataset
python data/generate_dataset.py

# 4. Train models
python train_models.py

# 5. Run application
python app.py
```

## Manual Installation

### Step 1: Install TensorFlow

```bash
pip install tensorflow==2.13.0
```

### Step 2: Install Image Processing

```bash
pip install Pillow opencv-python
```

### Step 3: Install Flask

```bash
pip install Flask==2.3.3
```

### Step 4: Install Other Dependencies

```bash
pip install numpy pandas python-dateutil
```

## Verification

Run the test script:

```bash
python test_models.py
```

You should see:
```
✅ CNN Model built successfully
✅ LSTM Model built successfully
✅ CNN Prediction successful
✅ LSTM Prediction successful
```

## Next Steps

1. **Generate Dataset**: `python data/generate_dataset.py`
2. **Train Models**: `python train_models.py`  
3. **Start App**: `python app.py`
4. **Access**: http://localhost:5000

## Troubleshooting

### TensorFlow Installation Issues

**Windows:**
```bash
pip install tensorflow-cpu==2.13.0
```

**macOS (M1/M2):**
```bash
pip install tensorflow-macos==2.13.0
pip install tensorflow-metal
```

**Linux:**
```bash
pip install tensorflow==2.13.0
```

### OpenCV Issues

If cv2 import fails:
```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

### Memory Issues

If you encounter memory errors during training:
- Reduce batch size in `train_models.py`
- Reduce dataset size in `data/generate_dataset.py`

```python
# In train_models.py, change:
history = lstm.model.fit(
    X, y,
    epochs=20,
    batch_size=16,  # <-- Reduce from 32 to 16
    ...
)
```

## System Requirements

- **Python**: 3.8 - 3.11
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

## Optional: GPU Support

For faster training with NVIDIA GPU:

```bash
pip install tensorflow-gpu==2.13.0
```

Requirements:
- CUDA 11.8
- cuDNN 8.6
