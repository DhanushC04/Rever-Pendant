"""
Test Email Setup
Run this to verify your email configuration works
"""

import os
from flask import Flask
from flask_mail import Mail, Message

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USERNAME')

print("\n" + "="*50)
print("📧 EMAIL CONFIGURATION TEST")
print("="*50)
print(f"Email: {app.config['MAIL_USERNAME']}")
print(f"Password: {'*' * len(app.config['MAIL_PASSWORD']) if app.config['MAIL_PASSWORD'] else 'NOT SET'}")
print("="*50 + "\n")

# Check if credentials are set
if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
    print("❌ ERROR: Email credentials not set!")
    print("\nTo fix:")
    print("1. Create .env file in backend folder")
    print("2. Add these lines:")
    print("   EMAIL_USERNAME=your-email@gmail.com")
    print("   EMAIL_PASSWORD=your-16-char-app-password")
    print("\n3. Get app password from: https://myaccount.google.com/security")
    exit(1)

mail = Mail(app)

# Test sending email
def test_email():
    try:
        with app.app_context():
            msg = Message(
                subject='✅ AI Pendant Test Email',
                recipients=[app.config['MAIL_USERNAME']]  # Send to yourself
            )
            
            msg.html = """
            <html>
            <body style="font-family: Arial; padding: 20px;">
                <h1 style="color: #8b5cf6;">✅ Email Test Successful!</h1>
                <p>Your AI Pendant email system is working correctly.</p>
                <p>You can now receive:</p>
                <ul>
                    <li>📝 Keynote summaries after conversations</li>
                    <li>⏰ Scheduled reminders</li>
                </ul>
                <p style="color: #6b7280; font-size: 12px; margin-top: 30px;">
                    Sent from AI Pendant System
                </p>
            </body>
            </html>
            """
            
            print("📤 Sending test email...")
            mail.send(msg)
            print("✅ SUCCESS! Email sent successfully!")
            print(f"📬 Check your inbox: {app.config['MAIL_USERNAME']}")
            return True
            
    except Exception as e:
        print(f"❌ ERROR sending email: {e}")
        print("\nCommon fixes:")
        print("1. Enable 2-Step Verification in Gmail")
        print("2. Generate App Password (not your regular password)")
        print("3. Use 16-character password without spaces")
        print("4. Check .env file has correct credentials")
        return False

if __name__ == '__main__':
    print("Starting email test...\n")
    success = test_email()
    
    if success:
        print("\n" + "="*50)
        print("🎉 EMAIL SYSTEM READY!")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("❌ EMAIL SYSTEM NOT WORKING")
        print("="*50)