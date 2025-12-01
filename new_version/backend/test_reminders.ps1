# Email & Reminder System Testing - PowerShell Script
# Run: .\test_reminders.ps1

param(
    [string]$Action = "status",
    [int]$MinutesFromNow = 2,
    [int]$UserId = 1,
    [int]$KeynoteId = 1
)

$BaseUrl = "http://localhost:5000/api"

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "=" * 70
    Write-Host $Message
    Write-Host "=" * 70
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

# Check if backend is running
function Test-Backend {
    Write-Info "Testing backend connectivity..."
    try {
        $health = Invoke-RestMethod -Uri "$BaseUrl/health" -ErrorAction Stop
        Write-Success "Backend is running"
        return $true
    } catch {
        Write-Error-Custom "Backend is not responding!"
        Write-Error-Custom "Start it with: python app.py"
        return $false
    }
}

# Show debug status
function Show-Status {
    Write-Header "📊 REMINDER DEBUG STATUS"
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/debug/reminders" -ErrorAction Stop
        
        Write-Info "Scheduler Status: $(if($response.scheduler_running) {'🟢 RUNNING'} else {'🔴 STOPPED'})"
        Write-Info "Mail Configured: $(if($response.mail_configured) {'✅ YES'} else {'❌ NO'})"
        Write-Info "Timestamp: $($response.timestamp)"
        
        Write-Host ""
        Write-Host "📋 Database Reminders:" -ForegroundColor Cyan
        if ($response.database_records.Count -eq 0) {
            Write-Info "No reminders in database"
        } else {
            $response.database_records | Format-Table -Property id, user_id, keynote_id, reminder_time, is_sent, sent_at
        }
        
        Write-Host ""
        Write-Host "⏱️  Scheduled Jobs:" -ForegroundColor Cyan
        if ($response.scheduled_jobs.Count -eq 0) {
            Write-Info "No jobs scheduled"
        } else {
            $response.scheduled_jobs | Format-Table -Property job_id, next_run_time, trigger, func
        }
    } catch {
        Write-Error-Custom "Failed to get status: $_"
    }
}

# Create test reminder
function Create-Reminder {
    Write-Header "⏰ CREATING TEST REMINDER"
    
    $reminderTime = (Get-Date).AddMinutes($MinutesFromNow).ToString("yyyy-MM-ddTHH:mm:ss")
    Write-Info "Will fire at: $reminderTime (in $MinutesFromNow minutes)"
    
    $body = @{
        user_id = $UserId
        keynote_id = $KeynoteId
        reminder_time = $reminderTime
    } | ConvertTo-Json
    
    Write-Info "Sending request..."
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/reminders" -Method Post -Body $body -ContentType "application/json" -ErrorAction Stop
        Write-Success "Reminder created!"
        Write-Host $response | ConvertTo-Json -Indent 2
        Write-Success "Check console for logs starting with ⏰ when reminder time arrives"
    } catch {
        Write-Error-Custom "Failed to create reminder: $_"
    }
}

# Get all conversations
function List-Conversations {
    Write-Header "📚 CONVERSATIONS"
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/conversations" -ErrorAction Stop
        if ($response.Count -eq 0) {
            Write-Info "No conversations found. Create one via /api/start"
        } else {
            $response | Format-Table -Property id, title, duration, location, timestamp
        }
    } catch {
        Write-Error-Custom "Failed to get conversations: $_"
    }
}

# Get user reminders
function List-Reminders {
    Write-Header "🔔 USER REMINDERS"
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/reminders/user/$UserId" -ErrorAction Stop
        if ($response.Count -eq 0) {
            Write-Info "No reminders for user $UserId"
        } else {
            $response | Format-Table -Property id, keynote_id, reminder_time, is_sent, sent_at
        }
    } catch {
        Write-Error-Custom "Failed to get reminders: $_"
    }
}

# Show usage
function Show-Usage {
    Write-Header "📖 EMAIL & REMINDER SYSTEM TEST SCRIPT"
    Write-Host ""
    Write-Host "Usage: .\test_reminders.ps1 -Action <action> [options]"
    Write-Host ""
    Write-Host "Actions:"
    Write-Host "  status          Show reminder debug status (default)"
    Write-Host "  create          Create test reminder"
    Write-Host "  conversations   List all conversations"
    Write-Host "  reminders       List user reminders"
    Write-Host "  all             Run all tests"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -MinutesFromNow <int>    Minutes until reminder fires (default: 2)"
    Write-Host "  -UserId <int>            User ID (default: 1)"
    Write-Host "  -KeynoteId <int>         Keynote ID (default: 1)"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\test_reminders.ps1                           # Show status"
    Write-Host "  .\test_reminders.ps1 -Action create            # Create 2-min reminder"
    Write-Host "  .\test_reminders.ps1 -Action create -MinutesFromNow 5  # Create 5-min reminder"
    Write-Host "  .\test_reminders.ps1 -Action all               # Run all diagnostics"
    Write-Host ""
}

# Main execution
if ($Action -eq "help" -or $Action -eq "-h") {
    Show-Usage
    exit
}

# Check backend first
if (-not (Test-Backend)) {
    exit 1
}

Write-Host ""

switch ($Action.ToLower()) {
    "status" {
        Show-Status
    }
    "create" {
        Show-Status
        Write-Host ""
        Create-Reminder
        Write-Host ""
        Write-Info "Check /api/debug/reminders to verify job was scheduled"
    }
    "conversations" {
        List-Conversations
    }
    "reminders" {
        List-Reminders
    }
    "all" {
        Show-Status
        Write-Host ""
        List-Conversations
        Write-Host ""
        List-Reminders
    }
    default {
        Show-Usage
    }
}

Write-Host ""
Write-Host "💡 TIP: Keep console open to see logs when reminder fires!" -ForegroundColor Yellow
Write-Host ""
