#!/usr/bin/env python3
"""
Email Configuration Diagnostic Script
Tests the email reminder system without needing to start the Flask server.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def diagnose_email_setup():
    """Run diagnostic checks on email configuration"""
    
    print("\n" + "="*70)
    print("🔍 AI PENDANT EMAIL SYSTEM DIAGNOSTIC")
    print("="*70 + "\n")
    
    # Check 1: .env file exists
    print("📋 [CHECK 1] Verifying .env file...")
    env_path = Path(__file__).parent / '.env'
    if not env_path.exists():
        print(f"   ❌ FAILED: .env file not found at {env_path}")
        print(f"   💡 Solution: Create {env_path} with EMAIL_USERNAME and EMAIL_PASSWORD")
        return False
    else:
        print(f"   ✅ PASSED: .env file found at {env_path}")
    
    # Check 2: Load .env and verify variables
    print("\n📋 [CHECK 2] Loading environment variables...")
    load_dotenv(env_path)
    
    email_username = os.getenv('EMAIL_USERNAME', '').strip()
    email_password = os.getenv('EMAIL_PASSWORD', '').strip()
    
    if not email_username:
        print("   ❌ FAILED: EMAIL_USERNAME not set in .env")
        print("   💡 Solution: Add EMAIL_USERNAME=your_email@gmail.com to .env")
        return False
    
    if not email_password:
        print("   ❌ FAILED: EMAIL_PASSWORD not set in .env")
        print("   💡 Solution: Add EMAIL_PASSWORD=your_app_password to .env")
        return False
    
    print(f"   ✅ PASSED: EMAIL_USERNAME = {email_username}")
    print(f"   ✅ PASSED: EMAIL_PASSWORD = {'*' * len(email_password)} (masked)")
    
    # Check 3: Validate email format
    print("\n📋 [CHECK 3] Validating email format...")
    if '@gmail.com' not in email_username.lower():
        print(f"   ⚠️  WARNING: Email doesn't appear to be Gmail: {email_username}")
        print("   💡 Note: This setup guide is for Gmail. Other providers may need different config.")
    else:
        print(f"   ✅ PASSED: Gmail email format detected")
    
    # Check 4: Validate app password format
    print("\n📋 [CHECK 4] Validating Gmail App Password format...")
    # App passwords are typically 16 characters (without spaces)
    password_clean = email_password.replace(' ', '').replace('-', '')
    if len(password_clean) < 12:
        print(f"   ⚠️  WARNING: Password seems too short: {len(password_clean)} chars")
        print("   💡 Gmail App Passwords are typically 16 characters")
    else:
        print(f"   ✅ PASSED: Password length looks correct ({len(password_clean)} chars)")
    
    # Check 5: Try importing required packages
    print("\n📋 [CHECK 5] Checking required packages...")
    required_packages = [
        ('flask', 'Flask'),
        ('flask_mail', 'Flask-Mail'),
        ('apscheduler', 'APScheduler'),
        ('sqlalchemy', 'SQLAlchemy'),
    ]
    
    all_installed = True
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print(f"   ✅ PASSED: {package_name} is installed")
        except ImportError:
            print(f"   ❌ FAILED: {package_name} not installed")
            print(f"   💡 Solution: pip install {package_name}")
            all_installed = False
    
    if not all_installed:
        return False
    
    # Check 6: Database models
    print("\n📋 [CHECK 6] Checking database models...")
    try:
        from models import Reminder, User, Keynote
        print("   ✅ PASSED: Database models loaded (Reminder, User, Keynote)")
    except Exception as e:
        print(f"   ❌ FAILED: Could not load database models: {str(e)}")
        return False
    
    # Check 7: Summary
    print("\n" + "="*70)
    print("✅ ALL CHECKS PASSED!")
    print("="*70)
    print("\n📧 Email Configuration Status:")
    print(f"   Email: {email_username}")
    print(f"   Password: Configured (length: {len(password_clean)} chars)")
    print(f"   Server: smtp.gmail.com:587 (TLS)")
    
    print("\n🚀 Next Steps:")
    print("   1. Start Flask backend: python app.py")
    print("   2. Test email: POST to http://localhost:5000/api/debug/test-email")
    print("   3. Create reminders via API")
    print("   4. Check /api/debug/reminders to verify jobs are scheduled")
    
    print("\n📖 For detailed setup guide, see: EMAIL_SETUP.md\n")
    
    return True

if __name__ == '__main__':
    success = diagnose_email_setup()
    sys.exit(0 if success else 1)
