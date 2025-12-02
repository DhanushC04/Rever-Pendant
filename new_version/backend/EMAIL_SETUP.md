# Email Reminder System Setup Guide

## Overview
The AI Pendant system includes an email reminder feature that sends keynote summaries and reminders via Gmail SMTP. This guide will help you configure it.

## Prerequisites
- Gmail account with 2-Factor Authentication (2FA) enabled
- Python 3.13.x environment with all dependencies installed
- Flask backend running on `http://localhost:5000`

## Step 1: Enable 2-Factor Authentication on Gmail

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Look for "How you sign in to Google" section
3. Click "2-Step Verification"
4. Follow the setup instructions (you'll need to verify with your phone)

## Step 2: Generate Gmail App Password

**Why?** Gmail no longer allows regular passwords for third-party apps. You must use an "App Password" instead.

1. After enabling 2FA, go to [Google Account Security](https://myaccount.google.com/security)
2. Scroll down to "How you sign in to Google"
3. Click **"App passwords"** (only appears if 2FA is enabled)
4. Select:
   - **App:** Mail
   - **Device:** Windows Computer (or your device)
5. Google will generate a **16-character password** - copy this exactly (no spaces)

**Example App Password:** `abcd efgh ijkl mnop` → Use as `abcdefghijklmnop` in .env

## Step 3: Configure .env File

1. Open `new_version/backend/.env`
2. Replace the placeholders with your actual credentials:

```env
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
```

**Example:**
```env
EMAIL_USERNAME=john.doe@gmail.com
EMAIL_PASSWORD=abcdefghijklmnop
```

**DO NOT:**
- Use your regular Gmail password
- Share this file publicly
- Commit it to Git (it's in .gitignore)

## Step 4: Test Email Configuration

### Option A: Using cURL (Command Line)

```powershell
$headers = @{"Content-Type" = "application/json"}
$body = @{"email" = "your_test_email@gmail.com"} | ConvertTo-Json

Invoke-WebRequest `
  -Uri "http://localhost:5000/api/debug/test-email" `
  -Method POST `
  -Headers $headers `
  -Body $body
```

### Option B: Using Python

```python
import requests
import json

response = requests.post(
    'http://localhost:5000/api/debug/test-email',
    json={'email': 'your_test_email@gmail.com'}
)

print(json.dumps(response.json(), indent=2))
```

### Expected Response (Success):
```json
{
  "status": "success",
  "message": "Test email sent to your_test_email@gmail.com",
  "mail_server": "smtp.gmail.com",
  "mail_port": 587,
  "mail_username": "your_email@gmail.com"
}
```

### Expected Response (Failure - Missing Credentials):
```json
{
  "error": "Email credentials not configured",
  "message": "Please set EMAIL_USERNAME and EMAIL_PASSWORD in .env file",
  "mail_username_set": false,
  "mail_password_set": false
}
```

## Step 5: Create and Test a Reminder

### Create a Reminder (Example)

First, ensure you have a conversation and keynote in the database. Then:

```powershell
$headers = @{"Content-Type" = "application/json"}
$body = @{
    "user_id" = 1
    "keynote_id" = 1
    "reminder_time" = "2024-12-20T10:00:00"
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri "http://localhost:5000/api/reminders" `
  -Method POST `
  -Headers $headers `
  -Body $body
```

### Check Scheduled Reminders

```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/debug/reminders" -Method GET
```

This will show:
- All scheduled reminder jobs in APScheduler
- All reminders in the database
- Whether the scheduler is running
- Mail configuration status

## Troubleshooting

### ❌ "Email credentials not configured"
**Solution:** Check that `.env` file exists at `new_version/backend/.env` with EMAIL_USERNAME and EMAIL_PASSWORD set.

### ❌ "SMTP authentication failed"
**Possible causes:**
1. Using regular Gmail password instead of App Password
2. App Password copied with extra spaces
3. 2FA not enabled on Gmail account
4. Wrong email address format

**Solution:** 
- Verify you're using the 16-character App Password (without spaces)
- Verify 2FA is enabled at https://myaccount.google.com/security
- Double-check the email address matches your Gmail account

### ❌ "Connection refused" or "timeout"
**Possible causes:**
1. Flask backend not running on http://localhost:5000
2. Firewall blocking SMTP port 587

**Solution:**
- Start Flask: `python new_version/backend/app.py`
- Check firewall settings to allow outgoing SMTP (port 587)

### ❌ Reminders scheduled but emails not sent at scheduled time
**Possible causes:**
1. APScheduler background job not running
2. Flask process terminated or Python script exited

**Solution:**
- Keep the Flask server running continuously
- Check logs in `/api/debug/reminders` for scheduled jobs
- Monitor system logs for APScheduler execution

### ❌ "No module named 'flask_mail'" or similar import error
**Solution:** Reinstall requirements:
```powershell
pip install -r new_version/backend/requirements.txt
```

## Email Templates

The system sends emails in HTML format with categories:

### Keynote Email
- Subject: `📋 Keynotes from: [Conversation Title]`
- Shows all keynotes with color-coded categories:
  - 🔴 Action Items (red)
  - 🟢 Decisions (green)
  - 🟠 Questions (orange)
  - 🔴 Deadlines (dark red)

### Reminder Email
- Subject: `⏰ Reminder: [Keynote Category]`
- Shows the specific keynote content
- Includes importance score

## FAQ

**Q: Is my password secure in the .env file?**
A: Yes, if you use an App Password (not your main password). App Passwords can be revoked individually from Google Account settings.

**Q: Can I use other email providers?**
A: Not directly, but you can modify the email config in `app.py` lines 41-47 to use other SMTP servers (Outlook, Gmail business, etc.).

**Q: How many emails can I send per day?**
A: Gmail allows unlimited emails from the same account. Check your Google Account for any security alerts.

**Q: What if I forgot my App Password?**
A: You can regenerate it anytime from [Google Account App passwords](https://myaccount.google.com/apppasswords).

## Next Steps

1. ✅ Enable 2FA on Gmail
2. ✅ Generate App Password
3. ✅ Configure .env file
4. ✅ Test with /api/debug/test-email
5. ✅ Create reminders via API or frontend
6. ✅ Monitor /api/debug/reminders for execution

## Support

If reminders still aren't working:
1. Check Flask server logs for `[REMINDER EMAIL]` or `[TEST EMAIL]` messages
2. Verify .env file syntax (no quotes needed around values)
3. Test email first with `/api/debug/test-email` before creating reminders
4. Check Gmail "Allow less secure apps" hasn't been re-enabled (it shouldn't be - App Password is more secure)

---

**Last Updated:** 2024
**AI Pendant System Email Configuration**
