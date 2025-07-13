#!/usr/bin/env python3
"""
Vegetable Quality Inspector - Flask Backend
A comprehensive Flask application for vegetable quality inspection using TensorFlow Lite.
Supports image upload, camera capture, and real-time quality assessment.

Requirements: Python 3.10+
"""

import os
import io
import base64
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import json

import numpy as np
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
import tensorflow as tf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quality_inspector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask app configuration
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'vegetable-quality-inspector-secret-key-2024'),
    MAX_CONTENT_LENGTH=32 * 1024 * 1024,  # 32MB max file size
    UPLOAD_FOLDER='uploads',
    MODEL_PATH='vegetable_quality_model.tflite',
    TEMP_FOLDER='temp'
)

# Quality assessment categories
QUALITY_CATEGORIES = {
    'fresh': {'label': 'Fresh', 'color': '#28a745', 'description': 'Excellent quality, ready for consumption'},
    'good': {'label': 'Good', 'color': '#ffc107', 'description': 'Good quality, consume soon'},
    'fair': {'label': 'Fair', 'color': '#fd7e14', 'description': 'Fair quality, check before consumption'},
    'poor': {'label': 'Poor', 'color': '#dc3545', 'description': 'Poor quality, not recommended for consumption'}
}

# Vegetable types supported
VEGETABLE_TYPES = [
    'Tomato', 'Cucumber', 'Carrot', 'Bell_Pepper', 'Broccoli',
    'Cabbage', 'Lettuce', 'Spinach', 'Potato', 'Onion',
    'Eggplant', 'Zucchini', 'Radish', 'Cauliflower', 'Bean'
]

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'tiff'}

# Global variables
interpreter = None
input_details = None
output_details = None

class ImageProcessingError(Exception):
    """Custom exception for image processing errors."""
    pass

class ModelInferenceError(Exception):
    """Custom exception for model inference errors."""
    pass

def initialize_model() -> bool:
    """
    Initialize the TensorFlow Lite model and get input/output details.
    
    Returns:
        bool: True if model loaded successfully, False otherwise
    """
    global interpreter, input_details, output_details
    
    try:
        model_path = app.config['MODEL_PATH']
        if not os.path.exists(model_path):
            logger.warning(f"Model file not found at {model_path}")
            return False
        
        # Load TFLite model
        interpreter = tf.lite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        
        # Get input and output tensors
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        # Log model details
        logger.info("TensorFlow Lite model loaded successfully")
        logger.info(f"Input shape: {input_details[0]['shape']}")
        logger.info(f"Input dtype: {input_details[0]['dtype']}")
        logger.info(f"Output shape: {output_details[0]['shape']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def allowed_file(filename: str) -> bool:
    """
    Check if the uploaded file has an allowed extension.
    
    Args:
        filename (str): Name of the file
        
    Returns:
        bool: True if file extension is allowed
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(image_data: bytes) -> bool:
    """
    Validate if the image data is not corrupted and can be processed.
    
    Args:
        image_data (bytes): Raw image data
        
    Returns:
        bool: True if image is valid
    """
    try:
        # Try to open and verify the image
        with Image.open(io.BytesIO(image_data)) as img:
            img.verify()
        
        # Try to load the image again (verify() can only be called once)
        with Image.open(io.BytesIO(image_data)) as img:
            img.load()
            
        return True
        
    except Exception as e:
        logger.warning(f"Image validation failed: {str(e)}")
        return False

def preprocess_image(image_data: bytes) -> np.ndarray:
    """
    Preprocess image for quality inspection model.
    
    Args:
        image_data (bytes): Raw image data
        
    Returns:
        np.ndarray: Preprocessed image array
        
    Raises:
        ImageProcessingError: If image processing fails
    """
    try:
        # Validate image first
        if not validate_image(image_data):
            raise ImageProcessingError("Invalid or corrupted image file")
        
        # Open image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Auto-orient image based on EXIF data
        image = ImageOps.exif_transpose(image)
        
        # Resize to model input size (150x150)
        image = image.resize((150, 150), Image.Resampling.LANCZOS)
        
        # Convert to numpy array
        image_array = np.array(image, dtype=np.float32)
        
        # Normalize pixel values to [0, 1]
        image_array = image_array / 255.0
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        # Validate array shape
        expected_shape = (1, 150, 150, 3)
        if image_array.shape != expected_shape:
            raise ImageProcessingError(f"Invalid image shape: {image_array.shape}, expected: {expected_shape}")
        
        return image_array
        
    except ImageProcessingError:
        raise
    except Exception as e:
        logger.error(f"Image preprocessing failed: {str(e)}")
        raise ImageProcessingError(f"Failed to process image: {str(e)}")

def predict_quality(image_array: np.ndarray) -> Dict[str, Any]:
    """
    Predict vegetable quality using the TFLite model.
    
    Args:
        image_array (np.ndarray): Preprocessed image array
        
    Returns:
        Dict[str, Any]: Prediction results
        
    Raises:
        ModelInferenceError: If model inference fails
    """
    global interpreter, input_details, output_details
    
    if interpreter is None:
        raise ModelInferenceError("Model not initialized")
    
    try:
        # Set input tensor
        interpreter.set_tensor(input_details[0]['index'], image_array)
        
        # Run inference
        interpreter.invoke()
        
        # Get output tensor
        output_data = interpreter.get_tensor(output_details[0]['index'])
        predictions = output_data[0]  # Remove batch dimension
        
        # For demonstration, we'll simulate quality assessment
        # In a real scenario, your model would output quality scores
        vegetable_type_idx = np.argmax(predictions[:len(VEGETABLE_TYPES)])
        vegetable_type = VEGETABLE_TYPES[vegetable_type_idx]
        
        # Simulate quality assessment based on prediction confidence
        max_confidence = float(predictions[vegetable_type_idx])
        
        # Quality assessment logic (customize based on your model)
        if max_confidence > 0.8:
            quality = 'fresh'
        elif max_confidence > 0.6:
            quality = 'good'
        elif max_confidence > 0.4:
            quality = 'fair'
        else:
            quality = 'poor'
        
        # Calculate quality score (0-100)
        quality_score = min(100, int(max_confidence * 100))
        
        # Get all vegetable type predictions
        vegetable_predictions = []
        for i, prob in enumerate(predictions[:len(VEGETABLE_TYPES)]):
            vegetable_predictions.append({
                'vegetable': VEGETABLE_TYPES[i],
                'confidence': float(prob)
            })
        
        # Sort by confidence
        vegetable_predictions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'vegetable_type': vegetable_type,
            'quality_category': quality,
            'quality_info': QUALITY_CATEGORIES[quality],
            'quality_score': quality_score,
            'confidence': max_confidence,
            'vegetable_predictions': vegetable_predictions[:5],  # Top 5
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Model inference failed: {str(e)}")
        raise ModelInferenceError(f"Prediction failed: {str(e)}")

def decode_base64_image(base64_string: str) -> bytes:
    """
    Decode base64 encoded image data.
    
    Args:
        base64_string (str): Base64 encoded image
        
    Returns:
        bytes: Decoded image data
        
    Raises:
        ImageProcessingError: If decoding fails
    """
    try:
        # Remove data URL prefix if present
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(base64_string)
        return image_data
        
    except Exception as e:
        raise ImageProcessingError(f"Failed to decode base64 image: {str(e)}")

@app.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')

@app.route('/inspect', methods=['POST'])
def inspect_quality():
    """
    Main endpoint for vegetable quality inspection.
    Accepts both file uploads and base64 encoded images.
    """
    try:
        image_data = None
        filename = None
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({
                    'error': f'Invalid file type. Supported formats: {", ".join(ALLOWED_EXTENSIONS)}'
                }), 400
            
            filename = secure_filename(file.filename)
            image_data = file.read()
        
        # Handle base64 image (camera capture)
        elif 'image' in request.json:
            try:
                image_data = decode_base64_image(request.json['image'])
                filename = f'camera_capture_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
            except ImageProcessingError as e:
                return jsonify({'error': str(e)}), 400
        
        else:
            return jsonify({'error': 'No image provided'}), 400
        
        # Check file size
        if len(image_data) > app.config['MAX_CONTENT_LENGTH']:
            return jsonify({'error': 'File too large (max 32MB)'}), 413
        
        # Preprocess image
        try:
            processed_image = preprocess_image(image_data)
        except ImageProcessingError as e:
            return jsonify({'error': str(e)}), 400
        
        # Predict quality
        try:
            results = predict_quality(processed_image)
        except ModelInferenceError as e:
            return jsonify({'error': str(e)}), 500
        
        # Add filename to results
        results['filename'] = filename
        results['success'] = True
        
        # Log successful inspection
        logger.info(f"Quality inspection completed: {filename} -> {results['vegetable_type']} ({results['quality_category']})")
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Unexpected error in quality inspection: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error occurred'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    model_loaded = interpreter is not None
    return jsonify({
        'status': 'healthy' if model_loaded else 'unhealthy',
        'model_loaded': model_loaded,
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024),
        'vegetable_types': VEGETABLE_TYPES,
        'quality_categories': list(QUALITY_CATEGORIES.keys()),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/vegetables')
def get_vegetables():
    """Get supported vegetable types."""
    return jsonify({
        'vegetables': VEGETABLE_TYPES,
        'count': len(VEGETABLE_TYPES)
    })

@app.route('/quality-categories')
def get_quality_categories():
    """Get quality assessment categories."""
    return jsonify({
        'categories': QUALITY_CATEGORIES,
        'count': len(QUALITY_CATEGORIES)
    })

@app.errorhandler(413)
def too_large(e):
    """Handle request entity too large."""
    return jsonify({'error': 'File too large (max 32MB)'}), 413

@app.errorhandler(400)
def bad_request(e):
    """Handle bad request."""
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error."""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

def create_directories():
    """Create necessary directories."""
    directories = [
        app.config['UPLOAD_FOLDER'],
        app.config['TEMP_FOLDER'],
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

if __name__ == '__main__':
    # Create necessary directories
    create_directories()
    
    # Initialize model
    model_loaded = initialize_model()
    if not model_loaded:
        logger.warning("Model not loaded. Place your TensorFlow Lite model at: vegetable_quality_model.tflite")
    
    # Run the application
    logger.info("Starting Vegetable Quality Inspector...")
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )