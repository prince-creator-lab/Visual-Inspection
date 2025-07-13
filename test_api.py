#!/usr/bin/env python3
"""
Vegetable Quality Inspector API Test Script
==================================================

This script demonstrates how to interact with the Vegetable Quality Inspector API
for both file upload and camera capture scenarios. It includes comprehensive
error handling and showcases all API endpoints.

Usage:
    python test_api.py
    python test_api.py --test-file path/to/image.jpg
    python test_api.py --test-directory path/to/images/
    python test_api.py --verbose

Author: Vegetable Quality Inspector Team
Date: 2024
"""

import os
import sys
import json
import base64
import argparse
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests
from datetime import datetime

# API configuration
API_BASE_URL = "http://localhost:5000"
ENDPOINTS = {
    'inspect': f"{API_BASE_URL}/inspect",
    'vegetables': f"{API_BASE_URL}/vegetables",
    'quality_categories': f"{API_BASE_URL}/quality-categories",
    'health': f"{API_BASE_URL}/health"
}

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class QualityInspectorAPITest:
    """Test suite for Vegetable Quality Inspector API"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.session = requests.Session()
        self.session.timeout = 30
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with color coding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if level == "SUCCESS":
            color = Colors.GREEN
        elif level == "ERROR":
            color = Colors.RED
        elif level == "WARNING":
            color = Colors.YELLOW
        elif level == "INFO":
            color = Colors.BLUE
        else:
            color = Colors.WHITE
            
        print(f"{color}[{timestamp}] {level}: {message}{Colors.END}")
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{Colors.BOLD}{Colors.UNDERLINE}{title}{Colors.END}")
        print("=" * len(title))
        
    def print_result(self, result: Dict[str, Any]):
        """Print quality inspection results in a formatted way"""
        print(f"\n{Colors.CYAN}Quality Assessment Results:{Colors.END}")
        print(f"📱 Vegetable Type: {Colors.BOLD}{result['vegetable_type']}{Colors.END}")
        print(f"🏷️  Quality Category: {Colors.BOLD}{result['quality_category']}{Colors.END}")
        print(f"📊 Quality Score: {Colors.BOLD}{result['quality_score']}/100{Colors.END}")
        print(f"🎯 Confidence: {Colors.BOLD}{result['confidence']:.2%}{Colors.END}")
        print(f"📅 Analyzed: {result['timestamp']}")
        
        if result.get('filename'):
            print(f"📂 File: {result['filename']}")
        
        print(f"\n{Colors.MAGENTA}Quality Information:{Colors.END}")
        quality_info = result['quality_info']
        print(f"Label: {quality_info['label']}")
        print(f"Description: {quality_info['description']}")
        
        print(f"\n{Colors.YELLOW}Top Vegetable Predictions:{Colors.END}")
        for i, pred in enumerate(result['vegetable_predictions'][:5], 1):
            print(f"{i}. {pred['vegetable']:<15} {pred['confidence']:.2%}")
            
    def check_api_health(self) -> bool:
        """Check if the API is healthy and ready"""
        try:
            response = self.session.get(ENDPOINTS['health'])
            if response.status_code == 200:
                health_data = response.json()
                
                if health_data.get('model_loaded'):
                    self.log("API is healthy and model is loaded", "SUCCESS")
                    
                    if self.verbose:
                        print(f"  • Max file size: {health_data['max_file_size_mb']} MB")
                        print(f"  • Supported formats: {', '.join(health_data['supported_formats'])}")
                        print(f"  • Vegetable types: {len(health_data['vegetable_types'])}")
                        print(f"  • Quality categories: {len(health_data['quality_categories'])}")
                        
                    return True
                else:
                    self.log("API is running but model is not loaded", "WARNING")
                    return False
            else:
                self.log(f"Health check failed with status {response.status_code}", "ERROR")
                return False
                
        except requests.exceptions.ConnectionError:
            self.log("Cannot connect to API. Make sure the server is running.", "ERROR")
            return False
        except Exception as e:
            self.log(f"Health check error: {str(e)}", "ERROR")
            return False
            
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information from API"""
        try:
            vegetables_response = self.session.get(ENDPOINTS['vegetables'])
            categories_response = self.session.get(ENDPOINTS['quality_categories'])
            
            if vegetables_response.status_code == 200 and categories_response.status_code == 200:
                vegetables_data = vegetables_response.json()
                categories_data = categories_response.json()
                
                return {
                    'vegetables': vegetables_data['vegetables'],
                    'quality_categories': categories_data['categories']
                }
            else:
                self.log("Failed to get system information", "ERROR")
                return {}
                
        except Exception as e:
            self.log(f"Error getting system info: {str(e)}", "ERROR")
            return {}
            
    def test_file_upload(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Test quality inspection with file upload"""
        if not os.path.exists(file_path):
            self.log(f"File not found: {file_path}", "ERROR")
            return None
            
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                
                self.log(f"Uploading file: {file_path}", "INFO")
                start_time = time.time()
                
                response = self.session.post(ENDPOINTS['inspect'], files=files)
                
                processing_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        self.log(f"File processed successfully in {processing_time:.2f}s", "SUCCESS")
                        return result
                    else:
                        self.log(f"Processing failed: {result.get('error', 'Unknown error')}", "ERROR")
                        return None
                else:
                    error_msg = response.json().get('error', 'Unknown error') if response.headers.get('content-type') == 'application/json' else 'Server error'
                    self.log(f"Upload failed ({response.status_code}): {error_msg}", "ERROR")
                    return None
                    
        except Exception as e:
            self.log(f"Error testing file upload: {str(e)}", "ERROR")
            return None
            
    def test_base64_image(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Test quality inspection with base64 encoded image (simulating camera capture)"""
        if not os.path.exists(image_path):
            self.log(f"Image file not found: {image_path}", "ERROR")
            return None
            
        try:
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                
            # Convert to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            data_url = f"data:image/jpeg;base64,{base64_image}"
            
            payload = {'image': data_url}
            
            self.log(f"Testing base64 image: {image_path}", "INFO")
            start_time = time.time()
            
            response = self.session.post(
                ENDPOINTS['inspect'],
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload)
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.log(f"Base64 image processed successfully in {processing_time:.2f}s", "SUCCESS")
                    return result
                else:
                    self.log(f"Processing failed: {result.get('error', 'Unknown error')}", "ERROR")
                    return None
            else:
                error_msg = response.json().get('error', 'Unknown error') if response.headers.get('content-type') == 'application/json' else 'Server error'
                self.log(f"Base64 processing failed ({response.status_code}): {error_msg}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"Error testing base64 image: {str(e)}", "ERROR")
            return None
            
    def test_error_handling(self):
        """Test API error handling with invalid inputs"""
        self.print_header("Testing Error Handling")
        
        # Test 1: No file provided
        self.log("Test 1: No file provided", "INFO")
        response = self.session.post(ENDPOINTS['inspect'])
        if response.status_code == 400:
            self.log("✓ Correctly rejected request with no file", "SUCCESS")
        else:
            self.log("✗ Should have rejected request with no file", "ERROR")
            
        # Test 2: Invalid base64 data
        self.log("Test 2: Invalid base64 data", "INFO")
        invalid_payload = {'image': 'invalid_base64_data'}
        response = self.session.post(
            ENDPOINTS['inspect'],
            headers={'Content-Type': 'application/json'},
            data=json.dumps(invalid_payload)
        )
        if response.status_code == 400:
            self.log("✓ Correctly rejected invalid base64 data", "SUCCESS")
        else:
            self.log("✗ Should have rejected invalid base64 data", "ERROR")
            
        # Test 3: Empty file
        self.log("Test 3: Empty file", "INFO")
        try:
            files = {'file': ('empty.txt', b'', 'text/plain')}
            response = self.session.post(ENDPOINTS['inspect'], files=files)
            if response.status_code == 400:
                self.log("✓ Correctly rejected empty file", "SUCCESS")
            else:
                self.log("✗ Should have rejected empty file", "ERROR")
        except Exception as e:
            self.log(f"Error in empty file test: {str(e)}", "ERROR")
            
    def batch_test_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Test multiple images in a directory"""
        if not os.path.exists(directory_path):
            self.log(f"Directory not found: {directory_path}", "ERROR")
            return []
            
        # Supported image extensions
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff'}
        
        # Find all image files
        image_files = []
        for file_path in Path(directory_path).iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                image_files.append(file_path)
                
        if not image_files:
            self.log(f"No image files found in {directory_path}", "WARNING")
            return []
            
        self.log(f"Found {len(image_files)} image files", "INFO")
        
        results = []
        for i, image_file in enumerate(image_files, 1):
            self.log(f"Processing {i}/{len(image_files)}: {image_file.name}", "INFO")
            
            result = self.test_file_upload(str(image_file))
            if result:
                results.append({
                    'filename': image_file.name,
                    'result': result
                })
                
        return results
        
    def generate_report(self, results: List[Dict[str, Any]]):
        """Generate a summary report of batch processing results"""
        if not results:
            self.log("No results to report", "WARNING")
            return
            
        self.print_header("Batch Processing Report")
        
        # Summary statistics
        total_processed = len(results)
        vegetable_counts = {}
        quality_counts = {}
        
        for item in results:
            result = item['result']
            vegetable = result['vegetable_type']
            quality = result['quality_category']
            
            vegetable_counts[vegetable] = vegetable_counts.get(vegetable, 0) + 1
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
            
        print(f"Total images processed: {total_processed}")
        
        print(f"\n{Colors.CYAN}Vegetable Distribution:{Colors.END}")
        for vegetable, count in sorted(vegetable_counts.items()):
            percentage = (count / total_processed) * 100
            print(f"  {vegetable}: {count} ({percentage:.1f}%)")
            
        print(f"\n{Colors.MAGENTA}Quality Distribution:{Colors.END}")
        for quality, count in sorted(quality_counts.items()):
            percentage = (count / total_processed) * 100
            print(f"  {quality}: {count} ({percentage:.1f}%)")
            
        # Average quality score
        avg_score = sum(item['result']['quality_score'] for item in results) / total_processed
        print(f"\n{Colors.YELLOW}Average Quality Score: {avg_score:.1f}/100{Colors.END}")
        
def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Test Vegetable Quality Inspector API')
    parser.add_argument('--test-file', help='Test with a specific image file')
    parser.add_argument('--test-directory', help='Test with all images in a directory')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--no-error-tests', action='store_true', help='Skip error handling tests')
    
    args = parser.parse_args()
    
    # Initialize test suite
    tester = QualityInspectorAPITest(verbose=args.verbose)
    
    # Print welcome message
    tester.print_header("🥕 Vegetable Quality Inspector API Test Suite")
    print("Testing API functionality and error handling...")
    
    # Check API health
    if not tester.check_api_health():
        print(f"\n{Colors.RED}API health check failed. Please ensure the server is running.{Colors.END}")
        sys.exit(1)
        
    # Get system information
    system_info = tester.get_system_info()
    if system_info and args.verbose:
        print(f"\n{Colors.BLUE}System Information:{Colors.END}")
        print(f"Supported vegetables: {', '.join(system_info['vegetables'])}")
        print(f"Quality categories: {', '.join(system_info['quality_categories'].keys())}")
        
    # Test specific file
    if args.test_file:
        tester.print_header("Single File Test")
        result = tester.test_file_upload(args.test_file)
        if result:
            tester.print_result(result)
            
        # Also test base64 method
        print(f"\n{Colors.CYAN}Testing same image with base64 encoding:{Colors.END}")
        base64_result = tester.test_base64_image(args.test_file)
        if base64_result:
            tester.print_result(base64_result)
            
    # Test directory
    elif args.test_directory:
        tester.print_header("Batch Directory Test")
        results = tester.batch_test_directory(args.test_directory)
        if results:
            tester.generate_report(results)
            
    # Default demo
    else:
        tester.print_header("Demo Mode")
        
        # Look for demo images
        demo_images = ['demo_tomato.jpg', 'demo_carrot.jpg', 'demo_lettuce.jpg']
        found_demo = False
        
        for demo_image in demo_images:
            if os.path.exists(demo_image):
                tester.log(f"Found demo image: {demo_image}", "INFO")
                result = tester.test_file_upload(demo_image)
                if result:
                    tester.print_result(result)
                    found_demo = True
                    break
                    
        if not found_demo:
            print(f"\n{Colors.YELLOW}No demo images found. To test:{Colors.END}")
            print(f"  python test_api.py --test-file path/to/image.jpg")
            print(f"  python test_api.py --test-directory path/to/images/")
            
    # Test error handling
    if not args.no_error_tests:
        tester.test_error_handling()
        
    print(f"\n{Colors.GREEN}Testing completed!{Colors.END}")
    
if __name__ == "__main__":
    main()