#!/usr/bin/env powershell
<#
.SYNOPSIS
    Email Reminder System Test Helper Script
    Quick tests for the AI Pendant email reminder functionality

.DESCRIPTION
    Provides PowerShell functions to test email configuration,
    create reminders, and debug the system without manual API calls

.EXAMPLE
    # Test email setup
    .\test_email_reminders.ps1 -TestEmail

    # Create a test reminder (1 hour from now)
    .\test_email_reminders.ps1 -CreateReminder -UserId 1 -KeynoteId 1 -HoursFromNow 1

    # Check all scheduled reminders
    .\test_email_reminders.ps1 -DebugReminders
#>

param(
    [switch]$TestEmail,
    [switch]$CreateReminder,
    [switch]$GetUserReminders,
    [switch]$DebugReminders,
    [string]$TestEmailAddr = "test@gmail.com",
    [int]$UserId = 1,
    [int]$KeynoteId = 1,
    [int]$HoursFromNow = 1,
    [string]$BaseUrl = "http://localhost:5000"
)

function Test-EmailSetup {
    <#
    .SYNOPSIS
        Test email configuration by sending a test email
    #>
    Write-Host "🔧 Testing email configuration..." -ForegroundColor Cyan
    
    $headers = @{"Content-Type" = "application/json"}
    $body = @{"email" = $TestEmailAddr} | ConvertTo-Json
    
    try {
        $response = Invoke-WebRequest `
            -Uri "$BaseUrl/api/debug/test-email" `
            -Method POST `
            -Headers $headers `
            -Body $body `
            -ErrorAction Stop
        
        $data = $response.Content | ConvertFrom-Json
        
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ SUCCESS: Email test passed!" -ForegroundColor Green
            Write-Host "   Status: $($data.status)"
            Write-Host "   Message: $($data.message)"
            Write-Host "   Server: $($data.mail_server):$($data.mail_port)"
            Write-Host "   From: $($data.mail_username)"
            Write-Host ""
            Write-Host "📧 Check your inbox for test email at: $TestEmailAddr"
        } else {
            Write-Host "❌ FAILED: $($data.error)" -ForegroundColor Red
            Write-Host "   Message: $($data.message)"
        }
    }
    catch {
        Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Message -like "*Connection refused*") {
            Write-Host "   💡 Hint: Is Flask backend running? (python app.py)"
        }
    }
}

function Create-Reminder {
    <#
    .SYNOPSIS
        Create a scheduled email reminder
    #>
    $reminderTime = (Get-Date).AddHours($HoursFromNow).ToString("yyyy-MM-ddTHH:mm:ss")
    
    Write-Host "⏰ Creating reminder..." -ForegroundColor Cyan
    Write-Host "   User ID: $UserId"
    Write-Host "   Keynote ID: $KeynoteId"
    Write-Host "   Reminder Time: $reminderTime (in $HoursFromNow hour(s))"
    Write-Host ""
    
    $headers = @{"Content-Type" = "application/json"}
    $body = @{
        "user_id" = $UserId
        "keynote_id" = $KeynoteId
        "reminder_time" = $reminderTime
    } | ConvertTo-Json
    
    try {
        $response = Invoke-WebRequest `
            -Uri "$BaseUrl/api/reminders" `
            -Method POST `
            -Headers $headers `
            -Body $body `
            -ErrorAction Stop
        
        $data = $response.Content | ConvertFrom-Json
        
        Write-Host "✅ SUCCESS: Reminder created!" -ForegroundColor Green
        Write-Host "   Status: $($data.status)"
        Write-Host "   Reminder ID: $($data.reminder_id)"
        Write-Host "   Scheduled Time: $($data.reminder_time)"
        Write-Host ""
        Write-Host "⏳ Email will be sent at: $reminderTime"
    }
    catch {
        Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
        try {
            $data = $_.ErrorDetails.Message | ConvertFrom-Json
            Write-Host "   Server error: $($data.error)"
        }
        catch {}
    }
}

function Get-UserReminders {
    <#
    .SYNOPSIS
        Get all reminders for a user
    #>
    Write-Host "📋 Fetching reminders for User $UserId..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest `
            -Uri "$BaseUrl/api/reminders/user/$UserId" `
            -Method GET `
            -ErrorAction Stop
        
        $reminders = $response.Content | ConvertFrom-Json
        
        if ($reminders.Count -eq 0) {
            Write-Host "ℹ️  No reminders found for user $UserId" -ForegroundColor Yellow
        } else {
            Write-Host "✅ Found $($reminders.Count) reminder(s):" -ForegroundColor Green
            Write-Host ""
            
            $reminders | ForEach-Object {
                Write-Host "  Reminder ID: $($_.id)"
                Write-Host "    Keynote ID: $($_.keynote_id)"
                Write-Host "    Scheduled: $($_.reminder_time)"
                Write-Host "    Sent: $($_.is_sent)"
                if ($_.is_sent) {
                    Write-Host "    Sent At: $($_.sent_at)"
                }
                Write-Host ""
            }
        }
    }
    catch {
        Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Debug-Reminders {
    <#
    .SYNOPSIS
        Show detailed debug information about scheduled reminders
    #>
    Write-Host "🔍 Fetching reminder system debug info..." -ForegroundColor Cyan
    Write-Host ""
    
    try {
        $response = Invoke-WebRequest `
            -Uri "$BaseUrl/api/debug/reminders" `
            -Method GET `
            -ErrorAction Stop
        
        $data = $response.Content | ConvertFrom-Json
        
        # System Status
        Write-Host "🖥️  System Status:" -ForegroundColor Cyan
        Write-Host "   Scheduler Running: $($data.scheduler_running)"
        Write-Host "   Mail Configured: $($data.mail_configured)"
        Write-Host "   Timestamp: $($data.timestamp)"
        Write-Host ""
        
        # Scheduled Jobs
        Write-Host "📅 Scheduled Jobs ($($data.scheduled_jobs.Count)):" -ForegroundColor Cyan
        if ($data.scheduled_jobs.Count -eq 0) {
            Write-Host "   (No scheduled jobs)" -ForegroundColor Yellow
        } else {
            $data.scheduled_jobs | ForEach-Object {
                Write-Host "   Job ID: $($_.job_id)"
                Write-Host "     Trigger: $($_.trigger)"
                Write-Host "     Next Run: $($_.next_run_time)"
                Write-Host "     Function: $($_.func)"
                Write-Host ""
            }
        }
        
        # Database Records
        Write-Host "💾 Database Records ($($data.database_records.Count)):" -ForegroundColor Cyan
        if ($data.database_records.Count -eq 0) {
            Write-Host "   (No reminders in database)" -ForegroundColor Yellow
        } else {
            $data.database_records | ForEach-Object {
                $status = if ($_.is_sent) { "✅ SENT" } else { "⏳ PENDING" }
                Write-Host "   [$status] ID: $($_.id) | Keynote: $($_.keynote_id) | Time: $($_.reminder_time)"
            }
        }
        
        Write-Host ""
        if ($data.scheduled_jobs.Count -ne $data.database_records.Count) {
            Write-Host "⚠️  WARNING: Job count ($($data.scheduled_jobs.Count)) differs from DB count ($($data.database_records.Count))" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Message -like "*Connection refused*") {
            Write-Host "   💡 Hint: Is Flask backend running? (python app.py)"
        }
    }
}

# Main execution
Write-Host ""
Write-Host "═" * 70 -ForegroundColor Cyan
Write-Host "📧 AI PENDANT EMAIL REMINDER SYSTEM - TEST HELPER" -ForegroundColor Cyan
Write-Host "═" * 70 -ForegroundColor Cyan
Write-Host ""

if ($TestEmail) {
    Test-EmailSetup
}
elseif ($CreateReminder) {
    Create-Reminder
}
elseif ($GetUserReminders) {
    Get-UserReminders
}
elseif ($DebugReminders) {
    Debug-Reminders
}
else {
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\test_email_reminders.ps1 -TestEmail                       # Test email setup"
    Write-Host "  .\test_email_reminders.ps1 -CreateReminder                  # Create test reminder"
    Write-Host "  .\test_email_reminders.ps1 -GetUserReminders                # Get user's reminders"
    Write-Host "  .\test_email_reminders.ps1 -DebugReminders                  # Debug system"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -TestEmailAddr <email>      # Email to test with (default: test@gmail.com)"
    Write-Host "  -UserId <id>                # User ID for reminders (default: 1)"
    Write-Host "  -KeynoteId <id>             # Keynote ID for reminders (default: 1)"
    Write-Host "  -HoursFromNow <hours>       # Reminder in X hours (default: 1)"
    Write-Host "  -BaseUrl <url>              # Backend URL (default: http://localhost:5000)"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\test_email_reminders.ps1 -TestEmail -TestEmailAddr myemail@gmail.com"
    Write-Host "  .\test_email_reminders.ps1 -CreateReminder -HoursFromNow 2"
    Write-Host "  .\test_email_reminders.ps1 -DebugReminders"
    Write-Host ""
}

Write-Host ""
