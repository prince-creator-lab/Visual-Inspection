#!/usr/bin/env python3
"""
Example usage script for the Vegetable Classification Flask API.
This script demonstrates how to interact with the API programmatically.
"""

import requests
import json
import os
from pathlib import Path

# API configuration
API_BASE_URL = "http://localhost:5000"
ENDPOINTS = {
    'predict': f"{API_BASE_URL}/predict",
    'classes': f"{API_BASE_URL}/classes",
    'health': f"{API_BASE_URL}/health"
}

def check_health():
    """Check if the API is healthy and ready to use."""
    try:
        response = requests.get(ENDPOINTS['health'])
        if response.status_code == 200:
            data = response.json()
            print("✅ API Health Check:")
            print(f"   Status: {data['status']}")
            print(f"   Model loaded: {data['model_loaded']}")
            print(f"   Supported formats: {', '.join(data['supported_formats'])}")
            print(f"   Max file size: {data['max_file_size_mb']} MB")
            print(f"   Number of classes: {data['num_classes']}")
            return data['model_loaded']
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the Flask app is running.")
        return False
    except Exception as e:
        print(f"❌ Error checking health: {e}")
        return False

def get_supported_classes():
    """Get the list of supported vegetable classes."""
    try:
        response = requests.get(ENDPOINTS['classes'])
        if response.status_code == 200:
            data = response.json()
            print("\n📋 Supported Vegetable Classes:")
            for i, class_name in enumerate(data['classes'], 1):
                print(f"   {i:2d}. {class_name}")
            return data['classes']
        else:
            print(f"❌ Failed to get classes: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting classes: {e}")
        return []

def classify_image(image_path):
    """
    Classify a vegetable image using the API.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Classification results or None if failed
    """
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return None
    
    try:
        # Open and send the image file
        with open(image_path, 'rb') as image_file:
            files = {'file': image_file}
            response = requests.post(ENDPOINTS['predict'], files=files)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"\n🎯 Classification Results for '{image_path}':")
                print(f"   Predicted Class: {data['predicted_class']}")
                print(f"   Confidence: {data['confidence']:.2%}")
                print(f"   Filename: {data['filename']}")
                
                print("\n📊 Top 5 Predictions:")
                for i, pred in enumerate(data['all_predictions'], 1):
                    print(f"   {i}. {pred['class']:<15} ({pred['confidence']:.2%})")
                
                return data
            else:
                print(f"❌ Classification failed: {data.get('error', 'Unknown error')}")
                return None
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
            print(f"❌ API request failed ({response.status_code}): {error_data.get('error', 'Unknown error')}")
            return None
    
    except Exception as e:
        print(f"❌ Error classifying image: {e}")
        return None

def batch_classify(image_directory):
    """
    Classify multiple images in a directory.
    
    Args:
        image_directory (str): Path to directory containing images
    """
    if not os.path.exists(image_directory):
        print(f"❌ Directory not found: {image_directory}")
        return
    
    # Supported image extensions
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    
    # Find all image files
    image_files = []
    for file_path in Path(image_directory).iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(file_path)
    
    if not image_files:
        print(f"❌ No image files found in {image_directory}")
        return
    
    print(f"\n🔄 Batch processing {len(image_files)} images...")
    
    results = []
    for image_file in image_files:
        result = classify_image(str(image_file))
        if result:
            results.append({
                'filename': image_file.name,
                'predicted_class': result['predicted_class'],
                'confidence': result['confidence']
            })
        print("-" * 50)
    
    # Summary
    if results:
        print(f"\n📈 Batch Processing Summary:")
        print(f"   Total images processed: {len(results)}")
        print(f"   Success rate: {len(results)}/{len(image_files)} ({len(results)/len(image_files):.1%})")
        
        # Group by predicted class
        class_counts = {}
        for result in results:
            class_name = result['predicted_class']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        print(f"\n🏷️  Classification Summary:")
        for class_name, count in sorted(class_counts.items()):
            print(f"   {class_name}: {count} image(s)")

def main():
    """Main function to demonstrate API usage."""
    print("🥕 Vegetable Classification API Example")
    print("=" * 40)
    
    # Check API health
    if not check_health():
        print("\n❌ API is not ready. Please start the Flask app first.")
        print("   Run: python app.py")
        return
    
    # Get supported classes
    classes = get_supported_classes()
    if not classes:
        return
    
    # Example: Classify a single image
    print("\n" + "=" * 50)
    print("Example 1: Single Image Classification")
    print("=" * 50)
    
    # You can replace this with an actual image path
    example_image = "example_vegetable.jpg"
    
    if os.path.exists(example_image):
        classify_image(example_image)
    else:
        print(f"ℹ️  To test single image classification, place an image at: {example_image}")
    
    # Example: Batch classification
    print("\n" + "=" * 50)
    print("Example 2: Batch Image Classification")
    print("=" * 50)
    
    example_directory = "test_images"
    
    if os.path.exists(example_directory):
        batch_classify(example_directory)
    else:
        print(f"ℹ️  To test batch classification, create a directory: {example_directory}")
        print("   and place some vegetable images inside.")
    
    print("\n✅ Example completed!")
    print("\nAPI Endpoints:")
    for name, url in ENDPOINTS.items():
        print(f"   {name}: {url}")

if __name__ == "__main__":
    main()