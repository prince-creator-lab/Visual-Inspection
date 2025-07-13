import os
import io
import numpy as np
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import tensorflow as tf
import logging
from typing import Optional, Tuple, List
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MODEL_PATH'] = 'model.tflite'  # Path to your TFLite model

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Vegetable classes - update these with your actual class names
VEGETABLE_CLASSES = [
    'Bean', 'Bitter_Gourd', 'Bottle_Gourd', 'Brinjal', 'Broccoli',
    'Cabbage', 'Capsicum', 'Carrot', 'Cauliflower', 'Cucumber',
    'Papaya', 'Potato', 'Pumpkin', 'Radish', 'Tomato'
]

# Global variable to store the TFLite interpreter
interpreter = None

def load_model() -> bool:
    """Load the TFLite model and initialize the interpreter."""
    global interpreter
    try:
        if not os.path.exists(app.config['MODEL_PATH']):
            logger.error(f"Model file not found at {app.config['MODEL_PATH']}")
            return False
        
        interpreter = tf.lite.Interpreter(model_path=app.config['MODEL_PATH'])
        interpreter.allocate_tensors()
        logger.info("TFLite model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False

def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_data: bytes) -> Optional[np.ndarray]:
    """
    Preprocess the uploaded image for model inference.
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        Preprocessed image array or None if preprocessing fails
    """
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to model input size (150x150)
        image = image.resize((150, 150), Image.Resampling.LANCZOS)
        
        # Convert to numpy array and normalize
        image_array = np.array(image, dtype=np.float32)
        image_array = image_array / 255.0  # Normalize to [0, 1]
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
    
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        return None

def predict_vegetable(image_array: np.ndarray) -> Tuple[Optional[str], Optional[float], Optional[List[dict]]]:
    """
    Predict vegetable class using the TFLite model.
    
    Args:
        image_array: Preprocessed image array
        
    Returns:
        Tuple of (predicted_class, confidence, all_predictions)
    """
    global interpreter
    
    if interpreter is None:
        logger.error("Model not loaded")
        return None, None, None
    
    try:
        # Get input and output tensors
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        # Set input tensor
        interpreter.set_tensor(input_details[0]['index'], image_array)
        
        # Run inference
        interpreter.invoke()
        
        # Get output
        output_data = interpreter.get_tensor(output_details[0]['index'])
        predictions = output_data[0]  # Remove batch dimension
        
        # Get predicted class and confidence
        predicted_class_idx = np.argmax(predictions)
        confidence = float(predictions[predicted_class_idx])
        predicted_class = VEGETABLE_CLASSES[predicted_class_idx]
        
        # Get all predictions sorted by confidence
        all_predictions = []
        for i, prob in enumerate(predictions):
            all_predictions.append({
                'class': VEGETABLE_CLASSES[i],
                'confidence': float(prob)
            })
        
        # Sort by confidence (descending)
        all_predictions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return predicted_class, confidence, all_predictions
    
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        return None, None, None

@app.route('/')
def index():
    """Render the main page with upload form."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle image upload and prediction."""
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed types: ' + ', '.join(ALLOWED_EXTENSIONS)}), 400
        
        # Read file data
        file_data = file.read()
        
        # Check file size (additional check beyond Flask config)
        if len(file_data) > app.config['MAX_CONTENT_LENGTH']:
            return jsonify({'error': 'File too large'}), 400
        
        # Preprocess image
        image_array = preprocess_image(file_data)
        if image_array is None:
            return jsonify({'error': 'Failed to process image'}), 400
        
        # Make prediction
        predicted_class, confidence, all_predictions = predict_vegetable(image_array)
        
        if predicted_class is None:
            return jsonify({'error': 'Failed to make prediction'}), 500
        
        # Return results
        result = {
            'success': True,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'all_predictions': all_predictions[:5],  # Top 5 predictions
            'filename': secure_filename(file.filename)
        }
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in predict endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    model_loaded = interpreter is not None
    return jsonify({
        'status': 'healthy' if model_loaded else 'unhealthy',
        'model_loaded': model_loaded,
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024),
        'num_classes': len(VEGETABLE_CLASSES)
    })

@app.route('/classes')
def get_classes():
    """Get list of supported vegetable classes."""
    return jsonify({'classes': VEGETABLE_CLASSES})

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Load the model
    if not load_model():
        logger.warning("Model not loaded. Please ensure model.tflite is in the project root.")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)