"""
Test script to verify email configuration and SMTP connectivity
Run this BEFORE running the main app to debug email issues
"""
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

print("\n" + "="*70)
print("📧 EMAIL CONFIGURATION TEST")
print("="*70 + "\n")

# Check environment variables
email_user = os.getenv('EMAIL_USERNAME', '')
email_pass = os.getenv('EMAIL_PASSWORD', '')

print("✅ Configuration Check:")
print(f"   EMAIL_USERNAME: {email_user if email_user else '❌ NOT SET'}")
print(f"   EMAIL_PASSWORD: {'*' * len(email_pass) if email_pass else '❌ NOT SET'}")

if not email_user or not email_pass:
    print("\n❌ ERROR: Email credentials not configured!")
    print("   Please set EMAIL_USERNAME and EMAIL_PASSWORD in .env file")
    sys.exit(1)

# Test SMTP connection
print("\n🔌 Testing SMTP Connection...")
try:
    import smtplib
    
    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
    print("   ✅ Connected to smtp.gmail.com")
    
    server.starttls()
    print("   ✅ TLS enabled")
    
    server.login(email_user, email_pass)
    print(f"   ✅ Login successful as {email_user}")
    
    server.quit()
    print("\n✅ SMTP Configuration is CORRECT!")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ AUTHENTICATION ERROR: {e}")
    print("   Check your EMAIL_USERNAME and EMAIL_PASSWORD in .env")
    print("   For Gmail, use an App Password: https://support.google.com/accounts/answer/185833")
    sys.exit(1)
    
except smtplib.SMTPException as e:
    print(f"\n❌ SMTP ERROR: {e}")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ CONNECTION ERROR: {e}")
    sys.exit(1)

# Test Flask-Mail
print("\n📧 Testing Flask-Mail...")
try:
    from flask import Flask
    from flask_mail import Mail, Message
    
    app = Flask(__name__)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = email_user
    app.config['MAIL_PASSWORD'] = email_pass
    app.config['MAIL_DEFAULT_SENDER'] = email_user
    
    mail = Mail(app)
    
    with app.app_context():
        msg = Message(
            subject="🧪 AI Pendant Test Email",
            recipients=[email_user],
            body="This is a test email from AI Pendant System.\nIf you received this, email configuration is working!"
        )
        
        print("   ✅ Message object created")
        print("   🔄 Sending test email to", email_user)
        
        mail.send(msg)
        print("   ✅ TEST EMAIL SENT SUCCESSFULLY!")
        
except Exception as e:
    print(f"   ❌ Flask-Mail Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("✅ ALL TESTS PASSED - Email system is configured correctly!")
print("="*70)
print("\nNow you can:")
print("  1. Run the main app: python app.py")
print("  2. Create reminders via API")
print("  3. Check /api/debug/reminders for status")
print("\n")
