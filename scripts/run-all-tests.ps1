# ============================================================================
# Complete Local Testing Script for CA3
# Student: X00203402 - Roko Skugor
# Runs all tests: Unit, Security, Performance, UAT
# ============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   CA3 - Complete Test Suite Runner    " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$script:ErrorCount = 0
$script:WarningCount = 0

function Add-Error([string]$Message) {
    Write-Host $Message -ForegroundColor Red
    $script:ErrorCount++
}

function Add-Warning([string]$Message) {
    Write-Host $Message -ForegroundColor Yellow
    $script:WarningCount++
}

# ============================================================================
# Step 1: Verify Virtual Environment
# ============================================================================
Write-Host "[1/7] Checking virtual environment..." -ForegroundColor Yellow

if (-Not (Test-Path "venv\Scripts\activate.ps1")) {
    Add-Error "ERROR: Virtual environment not found! Please create it first: python -m venv venv"
    exit 1
}

Write-Host "OK: Activating virtual environment..." -ForegroundColor Green
& "venv\Scripts\Activate.ps1"
Write-Host ""

# ============================================================================
# Step 2: Run Unit Tests (WITH coverage gate)
# ============================================================================
Write-Host "[2/7] Running Unit Tests (pytest)..." -ForegroundColor Yellow
Write-Host "      Target: 42 tests, >=80% coverage" -ForegroundColor Gray

$unitCmd = "pytest tests/test_calculator.py --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml --cov-fail-under=80 -v --tb=short"
$unitTestOutput = Invoke-Expression "$unitCmd 2>&1" | Out-String
Write-Host $unitTestOutput

if ($unitTestOutput -match "(\d+)\s+passed") {
    $passedTests = [int]$matches[1]
    if ($passedTests -eq 42) {
        Write-Host "OK: Unit tests passed ($passedTests/42)" -ForegroundColor Green
    } else {
        Add-Error "ERROR: Unit tests did not run expected count (got $passedTests/42)."
    }
} else {
    Add-Error "ERROR: Unit tests failed!"
}
Write-Host ""

# ============================================================================
# Step 3: Run Static Analysis (Pylint)
# ============================================================================
Write-Host "[3/7] Running Static Analysis (Pylint)..." -ForegroundColor Yellow
Write-Host "      Target: Score >=8.0/10" -ForegroundColor Gray

$pylintOutput = pylint src/ --output-format=text --score=yes 2>&1 | Out-String
Write-Host $pylintOutput

if ($pylintOutput -match "rated at ([\d\.]+)/10") {
    $score = [decimal]$matches[1]
    if ($score -ge 8.0) {
        Write-Host "OK: Pylint passed (Score: $score/10)" -ForegroundColor Green
    } else {
        Add-Warning "WARNING: Pylint score below 8.0 (Score: $score/10)"
    }
} else {
    Add-Warning "WARNING: Could not parse Pylint score"
}
Write-Host ""

# ============================================================================
# Step 4: Run Security Tests
# ============================================================================
Write-Host "[4/7] Running Security Tests..." -ForegroundColor Yellow

# pip-audit
Write-Host "      Running pip-audit (dependency scanner)..." -ForegroundColor Gray
$pipAuditOutput = pip-audit --desc 2>&1 | Out-String
$pipAuditExit = $LASTEXITCODE
Write-Host $pipAuditOutput

if ($pipAuditExit -eq 0 -and $pipAuditOutput -match "No known vulnerabilities found") {
    Write-Host "OK: pip-audit - No vulnerabilities found" -ForegroundColor Green
} else {
    Add-Warning "WARNING: pip-audit reported vulnerabilities or non-zero exit (see above)"
}
Write-Host ""

# Bandit
Write-Host "      Running bandit (SAST)..." -ForegroundColor Gray
$banditOutput = bandit -r src/ app.py -f txt 2>&1 | Out-String
$banditExit = $LASTEXITCODE
Write-Host $banditOutput

if ($banditExit -eq 0 -and $banditOutput -match "No issues identified") {
    Write-Host "OK: Bandit - No issues found" -ForegroundColor Green
} else {
    Add-Warning "WARNING: Bandit found security issues (see above)"
}
Write-Host ""

# ============================================================================
# Step 5: Start Flask Application
# ============================================================================
Write-Host "[5/7] Starting Flask application..." -ForegroundColor Yellow

# Ensure test-safe bind (app.py defaults to 127.0.0.1, but we enforce)
$env:FLASK_HOST = "127.0.0.1"
$env:FLASK_DEBUG = "0"
$env:PORT = "5000"

$FlaskProcess = Start-Process python -ArgumentList "app.py" -PassThru -WindowStyle Hidden

Write-Host "      Waiting for Flask to start (10 seconds)..." -ForegroundColor Gray
Start-Sleep -Seconds 2

# Poll health endpoint (faster + more reliable than fixed 10 sec wait)
$started = $false
for ($i = 0; $i -lt 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 3 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $started = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if ($started) {
    Write-Host "OK: Flask application started successfully" -ForegroundColor Green
} else {
    Add-Error "ERROR: Flask failed to start!"
    if ($FlaskProcess) { Stop-Process -Id $FlaskProcess.Id -Force -ErrorAction SilentlyContinue }
    exit 1
}
Write-Host ""

# ============================================================================
# Step 6: Run Performance Tests (Locust)
# ============================================================================
Write-Host "[6/7] Running Performance Tests (Locust)..." -ForegroundColor Yellow
Write-Host "      Test: 10 users, 30 seconds" -ForegroundColor Gray

$perfDir = "tests/performance"
$csvPrefix = "performance-results"
$htmlReport = "performance-report.html"

Push-Location $perfDir

# Clean old artifacts
Get-ChildItem -ErrorAction SilentlyContinue "$csvPrefix*" | Remove-Item -Force -ErrorAction SilentlyContinue
if (Test-Path $htmlReport) { Remove-Item $htmlReport -Force -ErrorAction SilentlyContinue }

$locustOutput = locust -f locustfile.py --headless --users 10 --spawn-rate 2 --run-time 30s --host http://localhost:5000 --html $htmlReport --csv $csvPrefix 2>&1 | Out-String
$locustExit = $LASTEXITCODE
Write-Host $locustOutput

# Prefer CSV parsing over fragile console regex
$statsFile = "${csvPrefix}_stats.csv"
if (Test-Path $statsFile) {
    try {
        $rows = Import-Csv $statsFile
        # Aggregate all rows except "Aggregated" if present; prefer Aggregated for totals
        $agg = $rows | Where-Object { $_.Name -eq "Aggregated" } | Select-Object -First 1
        if (-not $agg) { $agg = $rows | Select-Object -First 1 }

        $req = [decimal]$agg."Request Count"
        $fail = [decimal]$agg."Failure Count"

        $failureRate = 0
        if ($req -gt 0) { $failureRate = [math]::Round(($fail / $req) * 100, 2) }

        if ($locustExit -eq 0 -and $failureRate -eq 0) {
            Write-Host "OK: Performance tests passed (0% failure rate)" -ForegroundColor Green
        } else {
            Add-Warning "WARNING: Performance tests finished with $failureRate% failure rate (failures=$fail, requests=$req)"
        }
    } catch {
        Add-Warning "WARNING: Could not parse Locust CSV results ($statsFile)."
    }
} else {
    Add-Warning "WARNING: Locust did not produce CSV results ($statsFile)."
}

Pop-Location
Write-Host ""

# ============================================================================
# Step 7: Run UAT Tests (Selenium) - WITHOUT coverage
# ============================================================================
Write-Host "[7/7] Running UAT Tests (Selenium)..." -ForegroundColor Yellow
Write-Host "      Target: 11 tests" -ForegroundColor Gray

$env:TEST_URL = "http://localhost:5000"

# Ensure UAT does not enforce coverage (even if someone adds cov flags again later)
$uatCmd = "pytest -p no:cov tests/uat_selenium/test_uat.py -v --tb=short --html=uat-report.html --self-contained-html"
$uatOutput = Invoke-Expression "$uatCmd 2>&1" | Out-String
Write-Host $uatOutput

if ($uatOutput -match "(\d+)\s+passed") {
    $passedUAT = [int]$matches[1]
    if ($passedUAT -eq 11) {
        Write-Host "OK: UAT tests passed ($passedUAT/11)" -ForegroundColor Green
    } else {
        Add-Error "ERROR: UAT tests did not run expected count (got $passedUAT/11)."
    }
} else {
    Add-Error "ERROR: UAT tests failed!"
}
Write-Host ""

# ============================================================================
# Cleanup: Stop Flask
# ============================================================================
Write-Host "Stopping Flask application..." -ForegroundColor Gray
if ($FlaskProcess) {
    Stop-Process -Id $FlaskProcess.Id -Force -ErrorAction SilentlyContinue
    Write-Host "OK: Flask stopped" -ForegroundColor Green
}
Write-Host ""

# ============================================================================
# Summary Report
# ============================================================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "          TEST SUMMARY REPORT           " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Test Results:" -ForegroundColor White

Write-Host "  - Unit Tests (42):      " -NoNewline
if ($unitTestOutput -match "42\s+passed") {
    Write-Host "PASSED" -ForegroundColor Green
} else {
    Write-Host "FAILED" -ForegroundColor Red
}

Write-Host "  - Static Analysis:      " -NoNewline
if ($pylintOutput -match "rated at ([\d\.]+)/10") {
    $score = [decimal]$matches[1]
    if ($score -ge 8.0) { Write-Host "PASSED ($score/10)" -ForegroundColor Green }
    else { Write-Host "WARNING ($score/10)" -ForegroundColor Yellow }
} else {
    Write-Host "WARNING" -ForegroundColor Yellow
}

Write-Host "  - Security (pip-audit): " -NoNewline
if ($pipAuditExit -eq 0 -and $pipAuditOutput -match "No known vulnerabilities") {
    Write-Host "PASSED" -ForegroundColor Green
} else {
    Write-Host "WARNING" -ForegroundColor Yellow
}

Write-Host "  - Security (bandit):    " -NoNewline
if ($banditExit -eq 0 -and $banditOutput -match "No issues identified") {
    Write-Host "PASSED" -ForegroundColor Green
} else {
    Write-Host "WARNING" -ForegroundColor Yellow
}

Write-Host "  - Performance Tests:    " -NoNewline
if (Test-Path "tests/performance/${csvPrefix}_stats.csv") {
    Write-Host "COMPLETED (see report)" -ForegroundColor Green
} else {
    Write-Host "WARNING" -ForegroundColor Yellow
}

Write-Host "  - UAT Tests (11):       " -NoNewline
if ($uatOutput -match "11\s+passed") {
    Write-Host "PASSED" -ForegroundColor Green
} else {
    Write-Host "FAILED" -ForegroundColor Red
}

Write-Host ""
Write-Host "Reports Generated:" -ForegroundColor White
Write-Host "  - Coverage:     htmlcov/index.html"
Write-Host "  - Performance:  tests/performance/performance-report.html"
Write-Host "  - Performance CSV: tests/performance/${csvPrefix}_stats.csv"
Write-Host "  - UAT:          uat-report.html"
Write-Host ""

if ($script:ErrorCount -eq 0 -and $script:WarningCount -eq 0) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   ALL TESTS PASSED!                   " -ForegroundColor Green
    Write-Host "   Ready for Azure deployment!         " -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    exit 0
} elseif ($script:ErrorCount -eq 0) {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "   TESTS PASSED WITH WARNINGS          " -ForegroundColor Yellow
    Write-Host "   Review warnings above                " -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "   SOME TESTS FAILED                   " -ForegroundColor Red
    Write-Host "   Please review errors above           " -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
# End of Script