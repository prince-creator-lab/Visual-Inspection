# Vegetable Classification Flask App

A modern Flask web application that classifies vegetable images using TensorFlow Lite models. The app provides both a web interface and REST API endpoints for image classification.

## Features

- 🌱 **AI-Powered Classification**: Uses TensorFlow Lite for efficient inference
- 🖼️ **Image Upload**: Supports multiple image formats (PNG, JPG, JPEG, GIF, BMP, WebP)
- 🎨 **Modern UI**: Beautiful, responsive web interface with Bootstrap
- 🔧 **REST API**: RESTful endpoints for programmatic access
- 📊 **Confidence Scores**: Returns prediction confidence and top 5 predictions
- 🛡️ **Error Handling**: Comprehensive error handling and validation
- 📱 **Mobile Friendly**: Responsive design works on all devices

## Supported Vegetable Classes

The model supports classification of 15 vegetable types:
- Bean
- Bitter Gourd
- Bottle Gourd
- Brinjal (Eggplant)
- Broccoli
- Cabbage
- Capsicum (Bell Pepper)
- Carrot
- Cauliflower
- Cucumber
- Papaya
- Potato
- Pumpkin
- Radish
- Tomato

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your TensorFlow Lite model**:
   - Place your trained TFLite model file in the project root
   - Name it `model.tflite` or update the `MODEL_PATH` in `app.py`
   - Ensure your model expects input size 150x150x3 and outputs 15 classes

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the app**:
   - Open your browser and navigate to `http://localhost:5000`
   - The web interface will be available immediately

## Usage

### Web Interface

1. **Upload Image**: Click "Select Vegetable Image" and choose an image file
2. **Classify**: Click "Upload & Classify" to process the image
3. **View Results**: See the predicted class, confidence score, and top 5 predictions

### REST API

#### Upload and Classify Image

**Endpoint**: `POST /predict`

**Request**:
```bash
curl -X POST -F "file=@vegetable_image.jpg" http://localhost:5000/predict
```

**Response**:
```json
{
  "success": true,
  "predicted_class": "Tomato",
  "confidence": 0.9234,
  "all_predictions": [
    {"class": "Tomato", "confidence": 0.9234},
    {"class": "Capsicum", "confidence": 0.0456},
    {"class": "Brinjal", "confidence": 0.0234},
    {"class": "Potato", "confidence": 0.0123},
    {"class": "Carrot", "confidence": 0.0089}
  ],
  "filename": "vegetable_image.jpg"
}
```

#### Get Supported Classes

**Endpoint**: `GET /classes`

**Response**:
```json
{
  "classes": ["Bean", "Bitter_Gourd", "Bottle_Gourd", ...]
}
```

#### Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "supported_formats": ["png", "jpg", "jpeg", "gif", "bmp", "webp"],
  "max_file_size_mb": 16.0,
  "num_classes": 15
}
```

## API Error Responses

All errors return JSON with an error message:

```json
{
  "error": "Error description"
}
```

Common error codes:
- `400`: Bad request (invalid file, missing file, etc.)
- `413`: File too large (>16MB)
- `500`: Internal server error

## Configuration

You can modify these settings in `app.py`:

```python
# File upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Model settings
app.config['MODEL_PATH'] = 'model.tflite'

# Supported file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Update these with your actual class names
VEGETABLE_CLASSES = [
    'Bean', 'Bitter_Gourd', 'Bottle_Gourd', 'Brinjal', 'Broccoli',
    'Cabbage', 'Capsicum', 'Carrot', 'Cauliflower', 'Cucumber',
    'Papaya', 'Potato', 'Pumpkin', 'Radish', 'Tomato'
]
```

## Model Requirements

Your TensorFlow Lite model should:
- Accept input shape: `(1, 150, 150, 3)` (batch_size, height, width, channels)
- Expect normalized input values in range [0, 1]
- Output 15 class probabilities
- Be saved as a `.tflite` file

## Production Deployment

For production deployment, consider:

1. **Use a production WSGI server**:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Set environment variables**:
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-secret-key-here
   ```

3. **Enable HTTPS** and configure proper security headers
4. **Set up monitoring** and logging
5. **Configure file storage** for uploaded images if needed

## File Structure

```
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── model.tflite          # Your TensorFlow Lite model (add this)
├── templates/
│   └── index.html        # Web interface template
├── static/
│   └── css/
│       └── style.css     # Custom CSS styles
├── uploads/              # Upload directory (created automatically)
└── README.md            # This file
```

## Troubleshooting

### Common Issues

1. **Model not found**: Ensure `model.tflite` exists in the project root
2. **Import errors**: Install all dependencies with `pip install -r requirements.txt`
3. **File upload fails**: Check file size (<16MB) and format (supported extensions)
4. **Prediction errors**: Verify your model input/output format matches the expected shape

### Logs

The application logs important information to the console. Check for:
- Model loading status
- Image preprocessing errors
- Prediction failures

## License

This project is provided as-is for educational and development purposes.

## Contributing

Feel free to fork this project and submit pull requests for improvements!