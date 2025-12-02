# 📧 Email Reminder System - Quick Start

## Problem Solved ✅

Your email reminder system was incomplete because **`.env` file was missing**. The system had all the code in place (Flask-Mail configured, APScheduler running, endpoints defined), but credentials to send emails weren't configured.

## What Was Done

### 1. **Created `.env` File**
   - Location: `new_version/backend/.env`
   - Contains placeholders for Gmail credentials

### 2. **Added Test Email Endpoint**
   - Endpoint: `POST /api/debug/test-email`
   - Allows you to verify email configuration works before scheduling reminders

### 3. **Created Documentation**
   - `EMAIL_SETUP.md` - Complete setup guide with Gmail App Password instructions
   - `API_REFERENCE_REMINDERS.md` - API endpoint reference and examples
   - `diagnose_email.py` - Automated diagnostic script

### 4. **Email Scheduler Already Running**
   - APScheduler initialized at startup (app.py line 50)
   - `send_reminder_email()` function ready to send emails at scheduled times
   - Database models ready to store reminders

---

## 3-Step Quick Start

### Step 1: Get Gmail App Password (5 minutes)
1. Go to https://myaccount.google.com/security
2. Click "2-Step Verification" (enable if not already)
3. Click "App passwords" 
4. Select Mail → Windows Computer
5. Copy the 16-character password Google generates

### Step 2: Configure `.env` File
Open `new_version/backend/.env` and update:
```env
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_16_char_app_password_here
```

### Step 3: Test & Use
```powershell
# Start Flask backend
cd new_version\backend
python app.py

# In another terminal, test email:
$body = @{"email" = "test@gmail.com"} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:5000/api/debug/test-email" `
  -Method POST -Headers @{"Content-Type" = "application/json"} -Body $body

# Create a reminder (example - adjust user_id, keynote_id, time):
$body = @{
  "user_id" = 1
  "keynote_id" = 1
  "reminder_time" = (Get-Date).AddHours(1).ToString("yyyy-MM-ddTHH:mm:ss")
} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:5000/api/reminders" `
  -Method POST -Headers @{"Content-Type" = "application/json"} -Body $body
```

---

## System Architecture

```
Email Reminder Flow:
┌─────────────────────────────────────────┐
│ 1. Frontend/API Call: POST /api/reminders │
│    (keynote_id, reminder_time, user_id)  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 2. create_reminder() in app.py (line 536)│
│    - Save reminder to database           │
│    - Schedule background job with APScheduler
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 3. APScheduler Background Job            │
│    - Waits for reminder_time              │
│    - Triggers send_reminder_email()       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 4. send_reminder_email() (line 152)      │
│    - Queries database for reminder, user, keynote
│    - Builds HTML email                   │
│    - Calls mail.send() with Flask-Mail   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 5. Gmail SMTP (smtp.gmail.com:587)       │
│    - Authenticates with EMAIL_USERNAME   │
│    - Uses EMAIL_PASSWORD (App Password)  │
│    - Sends email to user.email            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 6. User receives email! ✅               │
└─────────────────────────────────────────┘
```

---

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/reminders` | POST | Create new reminder |
| `/api/reminders/user/{id}` | GET | Get user's reminders |
| `/api/reminders/{id}` | DELETE | Cancel reminder |
| `/api/debug/test-email` | POST | Test email setup |
| `/api/debug/reminders` | GET | Debug scheduled jobs |

---

## Files Created/Modified

### Created:
- ✅ `new_version/backend/.env` - Email credentials configuration
- ✅ `new_version/backend/EMAIL_SETUP.md` - Setup guide (10 pages)
- ✅ `new_version/backend/API_REFERENCE_REMINDERS.md` - API documentation
- ✅ `new_version/backend/diagnose_email.py` - Diagnostic tool
- ✅ `new_version/backend/EMAIL_REMINDERS_README.md` - This file

### Modified:
- ✅ `new_version/backend/app.py` - Added `/api/debug/test-email` endpoint (53 lines)

---

## Troubleshooting

### "Email credentials not configured"
→ Update `.env` file with EMAIL_USERNAME and EMAIL_PASSWORD

### "SMTP authentication failed"
→ Use Gmail **App Password**, not regular password  
→ Ensure 2FA is enabled on your Gmail account

### "Reminders scheduled but emails not sent"
→ Keep Flask process running (APScheduler needs the process alive)  
→ Check `/api/debug/reminders` to see scheduled jobs  
→ Check Flask console logs for `[REMINDER EMAIL]` messages

### "Connection timeout on port 587"
→ Check firewall allows outgoing SMTP (port 587)  
→ Verify Gmail SMTP isn't blocked by your ISP/network

---

## Testing Checklist

- [ ] .env file created with EMAIL_USERNAME and EMAIL_PASSWORD
- [ ] Flask backend running (`python app.py`)
- [ ] Test email sends successfully (`/api/debug/test-email`)
- [ ] Email arrives in inbox
- [ ] Reminder created successfully (`/api/reminders` POST)
- [ ] `/api/debug/reminders` shows scheduled job
- [ ] Wait for scheduled time - email should arrive
- [ ] Reminder marked as sent in database

---

## Next Steps

1. **Immediate:** Set up `.env` with Gmail credentials (5 min)
2. **Test:** Run test email endpoint (2 min)
3. **Verify:** Create a reminder and check it sends (5 min)
4. **Integrate:** Connect frontend to `/api/reminders` endpoints
5. **Monitor:** Use `/api/debug/reminders` to track jobs

---

## Support & Documentation

For detailed information:
- 📖 **Setup Guide:** `EMAIL_SETUP.md`
- 🔌 **API Reference:** `API_REFERENCE_REMINDERS.md`
- 🔍 **Diagnostics:** Run `python diagnose_email.py`
- 📋 **Code Comments:** See `app.py` lines 41-50 (config) and 84-254 (functions)

---

**Status:** ✅ Email reminder system ready to use  
**Next Action:** Update `.env` with your Gmail credentials
