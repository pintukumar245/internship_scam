#!/usr/bin/env python3
"""
Test script to verify Email Alerts and ML Model setup
Run: python test_features.py
"""

import os
import json
import sys

def test_imports():
    """Test if all modules can be imported."""
    print("🧪 Testing imports...")
    try:
        import flask
        print("  ✓ Flask")
        import requests
        print("  ✓ Requests")
        import sklearn
        print("  ✓ scikit-learn")
        import pandas
        print("  ✓ pandas")
        print("✅ All imports successful!\n")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("   Run: pip install -r requirements.txt\n")
        return False

def test_directories():
    """Test if required directories exist."""
    print("📁 Testing directories...")
    dirs = ['data', 'models', 'static', 'templates']
    for d in dirs:
        if os.path.exists(d):
            print(f"  ✓ {d}/")
        else:
            print(f"  ⚠️  {d}/ missing (will be created)")
    print()

def test_ml_model():
    """Test ML model creation."""
    print("🤖 Testing ML Scam Detector...")
    try:
        from scam_detector_ml import ml_detector, get_ml_prediction
        
        # Test with sample company data
        test_data = {
            'name': 'Test Company',
            'scam_details': ['fee demand found', 'complaint detected'],
            'snippets': [
                {'title': 'Company Info', 'snippet': 'We charge registration fees'},
                {'title': 'Reviews', 'snippet': 'Fake certificate complaints'},
                {'title': 'Forum', 'snippet': 'This is a scam'}
            ],
            'employee_size': '1-10 employees',
            'local_records': [{'stipend': '1000'}, {'stipend': '1000'}]
        }
        
        result = get_ml_prediction(test_data)
        if result:
            print(f"  ✓ ML Score: {result['ml_score']}%")
            print(f"  ✓ Confidence: {result['confidence']:.2%}")
            print(f"  ✓ Model: {result['model_used']}")
            print("✅ ML Model working!\n")
            return True
        else:
            print("❌ ML prediction failed\n")
            return False
    except Exception as e:
        print(f"❌ ML test error: {e}\n")
        return False

def test_email_system():
    """Test email alert system."""
    print("📧 Testing Email Alerts...")
    try:
        from email_alerts import email_alert_system, subscribe_to_alerts
        
        # Check SMTP configuration
        if email_alert_system.smtp_configured:
            print("  ✓ SMTP Configured")
            print(f"    Server: {email_alert_system.smtp_server}")
            print(f"    Port: {email_alert_system.smtp_port}")
            print(f"    Email: {email_alert_system.sender_email}")
        else:
            print("  ⚠️  SMTP not configured")
            print("    Add email settings to .env file")
        
        # Test subscription
        result = subscribe_to_alerts("test@example.com", ["Test Company"])
        if result.get('success'):
            print("  ✓ Subscription system working")
            print("✅ Email system ready!\n")
            return True
        else:
            print("  ⚠️  Subscription system needs testing\n")
            return False
    except Exception as e:
        print(f"❌ Email test error: {e}\n")
        return False

def test_data_files():
    """Test if data files can be created."""
    print("💾 Testing data storage...")
    try:
        os.makedirs('data', exist_ok=True)
        
        test_file = 'data/test.json'
        with open(test_file, 'w') as f:
            json.dump({'test': 'data'}, f)
        
        with open(test_file, 'r') as f:
            data = json.load(f)
        
        os.remove(test_file)
        print("  ✓ Can read/write JSON files")
        print("✅ Data storage working!\n")
        return True
    except Exception as e:
        print(f"❌ Data storage error: {e}\n")
        return False

def test_env_file():
    """Check if .env file exists."""
    print("⚙️  Checking configuration...")
    if os.path.exists('.env'):
        print("  ✓ .env file found")
        
        # Check for API keys
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            api_keys = ['GEMINI_API_KEY', 'GROQ_API_KEY', 'OPENAI_API_KEY']
            has_ai = any(os.getenv(key) for key in api_keys)
            
            if has_ai:
                print("  ✓ AI API key configured")
            else:
                print("  ⚠️  No AI API key (optional)")
            
            email = os.getenv('MAIL_USERNAME')
            if email:
                print(f"  ✓ Email configured: {email}")
            else:
                print("  ⚠️  Email not configured (optional)")
        except:
            pass
    else:
        print("  ⚠️  .env file not found")
        print("    Run: cp .env.example .env")
        print("    Then edit .env with your settings")
    print()

def test_app_routes():
    """Test if Flask app can start."""
    print("🚀 Testing Flask app...")
    try:
        from app import app
        print("  ✓ App module imported")
        
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("  ✓ Home page loads")
            else:
                print(f"  ⚠️  Home page status: {response.status_code}")
        
        print("✅ Flask app ready!\n")
        return True
    except Exception as e:
        print(f"❌ App test error: {e}\n")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*50)
    print("🧪 Feature Test Suite")
    print("="*50 + "\n")
    
    tests = [
        test_imports,
        test_directories,
        test_env_file,
        test_data_files,
        test_ml_model,
        test_email_system,
        test_app_routes
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("="*50)
    print("📊 Summary")
    print("="*50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n✅ Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to go!")
        print("\nNext steps:")
        print("1. python app.py")
        print("2. Visit http://localhost:5000/")
        print("3. Search for a company")
        print("4. See ML model in action!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) need attention")
        print("See messages above for details")
        return 1

if __name__ == "__main__":
    sys.exit(main())
