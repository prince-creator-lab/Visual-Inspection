# Vegetable Quality Inspector

A comprehensive Flask web application for AI-powered vegetable quality assessment using TensorFlow Lite. The system provides both camera capture and file upload capabilities with real-time quality analysis.

## ✨ Features

### Core Functionality
- **🎥 Camera Integration**: Real-time camera capture with auto-focus and orientation handling
- **📁 File Upload**: Support for multiple image formats with corruption detection
- **🤖 AI-Powered Analysis**: TensorFlow Lite model for efficient quality assessment
- **📊 Quality Scoring**: Comprehensive quality assessment with 4-tier classification
- **� Vegetable Recognition**: Identifies 15 different vegetable types
- **⚡ Real-time Processing**: Fast inference with optimized preprocessing
- **📱 Mobile-Friendly**: Responsive design with camera API support

### Technical Features
- **🛡️ Robust Error Handling**: Comprehensive error handling for corrupt images
- **🔐 Security**: File type validation, size limits, and secure processing
- **📱 Progressive Web App**: Modern web technologies with offline capability
- **🎨 Modern UI**: Beautiful, accessible interface with Bootstrap 5
- **🔄 Real-time Updates**: Live camera feed with instant capture
- **📈 Performance Optimized**: Efficient image processing and model inference

## 🥬 Supported Vegetables

The system can identify and assess quality for these vegetable types:

| Category | Vegetables |
|----------|------------|
| **Leafy Greens** | Lettuce, Spinach, Cabbage |
| **Roots & Tubers** | Carrot, Potato, Radish, Onion |
| **Cruciferous** | Broccoli, Cauliflower |
| **Fruiting** | Tomato, Bell Pepper, Cucumber, Eggplant |
| **Squash** | Zucchini |
| **Legumes** | Bean |

## 🏷️ Quality Categories

| Quality | Score Range | Description | Recommendation |
|---------|-------------|-------------|----------------|
| **Fresh** | 80-100 | Excellent quality | Ready for consumption |
| **Good** | 60-79 | Good quality | Consume soon |
| **Fair** | 40-59 | Fair quality | Check before consumption |
| **Poor** | 0-39 | Poor quality | Not recommended |

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Modern web browser with camera support
- TensorFlow Lite model file

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vegetable-quality-inspector
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your TensorFlow Lite model**
   - Place your trained model file as `vegetable_quality_model.tflite` in the project root
   - Ensure the model expects 150x150 RGB input and outputs 15 classes

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`
   - Allow camera permissions when prompted
   - Start inspecting vegetables!

## 🖥️ Usage

### Web Interface

1. **Camera Capture**
   - Click "Start Camera" to begin camera feed
   - Position vegetable in frame
   - Click "Capture" to take photo
   - Click "Inspect Quality" to analyze

2. **File Upload**
   - Click "Or Upload Image File"
   - Select image from your device
   - Preview will appear automatically
   - Click "Inspect Quality" to analyze

3. **Results**
   - View vegetable type identification
   - See quality assessment with score
   - Check detailed predictions
   - Review timestamp and confidence

### API Endpoints

#### Quality Inspection
```bash
POST /inspect
Content-Type: multipart/form-data (for file upload)
Content-Type: application/json (for camera capture)

# File upload example
curl -X POST -F "file=@vegetable.jpg" http://localhost:5000/inspect

# Camera capture example
curl -X POST -H "Content-Type: application/json" \
  -d '{"image": "data:image/jpeg;base64,/9j/4AAQ..."}' \
  http://localhost:5000/inspect
```

**Response:**
```json
{
  "success": true,
  "vegetable_type": "Tomato",
  "quality_category": "fresh",
  "quality_info": {
    "label": "Fresh",
    "color": "#28a745",
    "description": "Excellent quality, ready for consumption"
  },
  "quality_score": 85,
  "confidence": 0.8456,
  "vegetable_predictions": [
    {"vegetable": "Tomato", "confidence": 0.8456},
    {"vegetable": "Bell_Pepper", "confidence": 0.0892},
    {"vegetable": "Eggplant", "confidence": 0.0234}
  ],
  "timestamp": "2024-01-15T10:30:45.123456",
  "filename": "captured_image.jpg"
}
```

#### System Information
```bash
# Get supported vegetables
GET /vegetables

# Get quality categories
GET /quality-categories

# Health check
GET /health
```

## 🛠️ Configuration

### Environment Variables
```bash
export SECRET_KEY=your-secret-key-here
export FLASK_ENV=production
export MODEL_PATH=path/to/your/model.tflite
```

### Application Settings
```python
# In app.py
app.config.update(
    MAX_CONTENT_LENGTH=32 * 1024 * 1024,  # 32MB max file size
    UPLOAD_FOLDER='uploads',
    MODEL_PATH='vegetable_quality_model.tflite',
    TEMP_FOLDER='temp'
)
```

## 📁 Project Structure

```
vegetable-quality-inspector/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── vegetable_quality_model.tflite  # Your TensorFlow Lite model
├── templates/
│   └── index.html                  # Web interface
├── static/
│   └── css/
│       └── quality-inspector.css   # Custom styling
├── uploads/                        # File upload directory
├── temp/                           # Temporary files
├── logs/                           # Application logs
└── quality_inspector.log          # Log file
```

## 🔧 Model Requirements

Your TensorFlow Lite model should meet these specifications:

### Input Requirements
- **Shape**: `(1, 150, 150, 3)` - batch size, height, width, channels
- **Data Type**: `float32`
- **Range**: Normalized values [0, 1]
- **Format**: RGB color space

### Output Requirements
- **Shape**: `(1, 15)` - batch size, number of classes
- **Data Type**: `float32`
- **Range**: Probability scores [0, 1]
- **Order**: Must match VEGETABLE_TYPES order in app.py

### Model Training Tips
- Use data augmentation for better generalization
- Include various lighting conditions
- Train with different vegetable quality levels
- Implement proper validation splits
- Consider transfer learning from pre-trained models

## 🚀 Deployment

### Development Server
```bash
python app.py
```

### Production Deployment
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Docker
docker build -t vegetable-quality-inspector .
docker run -p 5000:5000 vegetable-quality-inspector
```

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🧪 Testing

### Manual Testing
1. Test camera functionality on different devices
2. Upload various image formats
3. Test with corrupted image files
4. Verify quality assessment accuracy
5. Check responsive design on mobile

### API Testing
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test with sample image
curl -X POST -F "file=@test_images/tomato.jpg" http://localhost:5000/inspect
```

## 🔍 Troubleshooting

### Common Issues

1. **Model Not Loading**
   - Check file path: `vegetable_quality_model.tflite`
   - Verify model format and compatibility
   - Check file permissions

2. **Camera Not Working**
   - Verify browser permissions
   - Check HTTPS for camera access
   - Test on different browsers

3. **Image Upload Failures**
   - Check file size (max 32MB)
   - Verify supported formats
   - Test with different image types

4. **Quality Assessment Issues**
   - Verify model input/output shapes
   - Check image preprocessing
   - Review vegetable type mappings

### Log Files
- Application logs: `quality_inspector.log`
- Error tracking: Check browser console
- Network issues: Verify API endpoints

## 📊 Performance Optimization

### Frontend Optimizations
- Lazy loading for large images
- Image compression before upload
- Efficient DOM manipulation
- Optimized CSS and JavaScript

### Backend Optimizations
- Model caching and reuse
- Efficient image preprocessing
- Asynchronous processing
- Memory management

### Infrastructure
- CDN for static assets
- Load balancing for high traffic
- Database optimization
- Caching strategies

## 🔒 Security Considerations

### File Upload Security
- File type validation
- Size limitations
- Virus scanning (recommended)
- Secure file storage

### API Security
- Rate limiting
- Input validation
- CORS configuration
- HTTPS enforcement

### Data Privacy
- No permanent storage of images
- Temporary file cleanup
- User consent for camera access
- GDPR compliance considerations

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add comprehensive tests
- Update documentation
- Ensure mobile compatibility

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- TensorFlow team for TensorFlow Lite
- Bootstrap team for responsive framework
- Font Awesome for icons
- OpenCV community for image processing insights

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation
- Test with provided examples

---

**Made with ❤️ for better vegetable quality assessment**