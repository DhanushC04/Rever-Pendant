# Email Reminder API Reference

## Endpoints

### 1. Test Email Configuration
**Endpoint:** `POST /api/debug/test-email`

Sends a test email to verify credentials are working.

**Request:**
```json
{
  "email": "recipient@example.com"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Test email sent to recipient@example.com",
  "mail_server": "smtp.gmail.com",
  "mail_port": 587,
  "mail_username": "your_email@gmail.com"
}
```

**Response (Failure):**
```json
{
  "error": "Email credentials not configured",
  "message": "Please set EMAIL_USERNAME and EMAIL_PASSWORD in .env file",
  "mail_username_set": false,
  "mail_password_set": false
}
```

---

### 2. Create Reminder
**Endpoint:** `POST /api/reminders`

Creates a scheduled email reminder for a keynote.

**Request:**
```json
{
  "user_id": 1,
  "keynote_id": 1,
  "reminder_time": "2024-12-25T10:00:00"
}
```

**Response:**
```json
{
  "status": "scheduled",
  "reminder_id": 42,
  "reminder_time": "2024-12-25T10:00:00"
}
```

**Parameters:**
- `user_id` (int): ID of the user receiving the reminder
- `keynote_id` (int): ID of the keynote to remind about
- `reminder_time` (ISO datetime): When to send the email (format: YYYY-MM-DDTHH:MM:SS)

---

### 3. Get User Reminders
**Endpoint:** `GET /api/reminders/user/<user_id>`

Retrieves all reminders for a specific user.

**Response:**
```json
[
  {
    "id": 1,
    "keynote_id": 5,
    "reminder_time": "2024-12-20T14:00:00",
    "is_sent": false,
    "sent_at": null
  },
  {
    "id": 2,
    "keynote_id": 6,
    "reminder_time": "2024-12-21T09:00:00",
    "is_sent": true,
    "sent_at": "2024-12-21T09:00:15"
  }
]
```

---

### 4. Cancel Reminder
**Endpoint:** `DELETE /api/reminders/<reminder_id>`

Cancels a scheduled reminder and removes it from the scheduler.

**Response:**
```json
{
  "status": "cancelled"
}
```

---

### 5. Debug Reminders
**Endpoint:** `GET /api/debug/reminders`

Shows all scheduled reminder jobs and database records for debugging.

**Response:**
```json
{
  "status": "ok",
  "scheduled_jobs": [
    {
      "job_id": "reminder_1",
      "next_run_time": "2024-12-20 10:00:00",
      "trigger": "date",
      "func": "app.send_reminder_email"
    }
  ],
  "database_records": [
    {
      "id": 1,
      "user_id": 1,
      "keynote_id": 5,
      "reminder_time": "2024-12-20T10:00:00",
      "is_sent": false,
      "sent_at": null,
      "created_at": "2024-12-15T12:30:45"
    }
  ],
  "mail_configured": true,
  "scheduler_running": true,
  "timestamp": "2024-12-15T12:35:20.123456"
}
```

---

## Example Workflows

### Workflow 1: Test Email Setup
```powershell
# 1. Test that email is configured correctly
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/debug/test-email" `
  -Method POST `
  -Headers @{"Content-Type" = "application/json"} `
  -Body (@{"email" = "test@gmail.com"} | ConvertTo-Json)

$response.Content | ConvertFrom-Json | Format-Table

# Expected output should show "success" status
```

### Workflow 2: Create and Verify Reminder
```powershell
# 1. Create a reminder for 1 hour from now
$futureTime = (Get-Date).AddHours(1).ToString("yyyy-MM-ddTHH:mm:ss")

$reminder = Invoke-WebRequest -Uri "http://localhost:5000/api/reminders" `
  -Method POST `
  -Headers @{"Content-Type" = "application/json"} `
  -Body (@{
    "user_id" = 1
    "keynote_id" = 1
    "reminder_time" = $futureTime
  } | ConvertTo-Json)

$reminderData = $reminder.Content | ConvertFrom-Json
Write-Host "Created reminder ID: $($reminderData.reminder_id)"

# 2. Check if it was scheduled
$debug = Invoke-WebRequest -Uri "http://localhost:5000/api/debug/reminders" -Method GET
($debug.Content | ConvertFrom-Json).scheduled_jobs | Format-Table

# 3. Verify it's in the database
$userReminders = Invoke-WebRequest -Uri "http://localhost:5000/api/reminders/user/1" -Method GET
($userReminders.Content | ConvertFrom-Json) | Format-Table
```

### Workflow 3: Cancel a Reminder
```powershell
# Delete reminder with ID 42
Invoke-WebRequest -Uri "http://localhost:5000/api/reminders/42" -Method DELETE
```

---

## Status Codes

| Code | Meaning | Typical Cause |
|------|---------|---------------|
| 200 | Success | Operation completed |
| 400 | Bad Request | Missing or invalid parameters |
| 404 | Not Found | Reminder/resource doesn't exist |
| 500 | Server Error | Email credentials missing or SMTP error |

---

## Common Errors

### "Missing data" (400)
```
Error: Missing data
```
**Solution:** Ensure POST request includes `keynote_id` and `reminder_time`

### "Email credentials not configured" (500)
```
Error: Email credentials not configured
Message: Please set EMAIL_USERNAME and EMAIL_PASSWORD in .env file
```
**Solution:** Update `new_version/backend/.env` with Gmail credentials

### "SMTP authentication failed" (500)
```
Error: Email sending failed
Message: [Errno 535] b'5.7.8 Username and password not accepted'
```
**Solution:** 
- Verify you're using Gmail App Password (not regular password)
- Ensure 2FA is enabled on Gmail account
- Check password doesn't have extra spaces

---

## Testing Checklist

- [ ] .env file exists with EMAIL_USERNAME and EMAIL_PASSWORD
- [ ] `/api/debug/test-email` returns "success"
- [ ] Email arrives in test inbox
- [ ] `/api/reminders` (POST) creates reminder without errors
- [ ] `/api/debug/reminders` shows scheduled job
- [ ] Reminder is marked as sent after scheduled time passes
- [ ] Email was received in user's inbox

---

For detailed setup instructions, see `EMAIL_SETUP.md`
