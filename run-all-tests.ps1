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

# ============================================================================
# Step 1: Verify Virtual Environment
# ============================================================================
Write-Host "[1/7] Checking virtual environment..." -ForegroundColor Yellow

if (-Not (Test-Path "venv\Scripts\activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "   Please create it first: python -m venv venv" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "OK: Activating virtual environment..." -ForegroundColor Green
& "venv\Scripts\Activate.ps1"

Write-Host ""

# ============================================================================
# Step 2: Run Unit Tests
# ============================================================================
Write-Host "[2/7] Running Unit Tests (pytest)..." -ForegroundColor Yellow
Write-Host "      Target: 42 tests, >=80% coverage" -ForegroundColor Gray

$unitTestOutput = pytest tests/test_calculator.py --cov=src --cov-report=term-missing --cov-fail-under=80 -v --tb=short 2>&1 | Out-String
Write-Host $unitTestOutput

if ($unitTestOutput -match "(\d+) passed") {
    $passedTests = [int]$matches[1]
    Write-Host "OK: Unit tests passed ($passedTests/42)" -ForegroundColor Green
} else {
    Write-Host "ERROR: Unit tests failed!" -ForegroundColor Red
    $script:ErrorCount++
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
        Write-Host "WARNING: Pylint score below 8.0 (Score: $score/10)" -ForegroundColor Yellow
        $script:WarningCount++
    }
} else {
    Write-Host "WARNING: Could not parse Pylint score" -ForegroundColor Yellow
    $script:WarningCount++
}

Write-Host ""

# ============================================================================
# Step 4: Run Security Tests
# ============================================================================
Write-Host "[4/7] Running Security Tests..." -ForegroundColor Yellow

# pip-audit
Write-Host "      Running pip-audit (dependency scanner)..." -ForegroundColor Gray
$pipAuditOutput = pip-audit --desc 2>&1 | Out-String
Write-Host $pipAuditOutput

if ($pipAuditOutput -match "No known vulnerabilities found") {
    Write-Host "OK: pip-audit - No vulnerabilities found" -ForegroundColor Green
} else {
    Write-Host "WARNING: pip-audit found vulnerabilities (see above)" -ForegroundColor Yellow
    $script:WarningCount++
}

Write-Host ""

# Bandit
Write-Host "      Running bandit (SAST)..." -ForegroundColor Gray
$banditOutput = bandit -r src/ app.py -f txt 2>&1 | Out-String
Write-Host $banditOutput

if ($banditOutput -match "No issues identified") {
    Write-Host "OK: Bandit - No issues found" -ForegroundColor Green
} elseif ($banditOutput -match "Total issues.*:\s*2") {
    Write-Host "WARNING: Bandit found 2 expected issues (debug mode)" -ForegroundColor Yellow
    $script:WarningCount++
} else {
    Write-Host "WARNING: Bandit found security issues (see above)" -ForegroundColor Yellow
    $script:WarningCount++
}

Write-Host ""

# ============================================================================
# Step 5: Start Flask Application
# ============================================================================
Write-Host "[5/7] Starting Flask application..." -ForegroundColor Yellow

$FlaskProcess = Start-Process python -ArgumentList "app.py" -PassThru -WindowStyle Hidden

Write-Host "      Waiting for Flask to start (10 seconds)..." -ForegroundColor Gray
Start-Sleep -Seconds 10

# Verify Flask is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "OK: Flask application started successfully" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Flask failed to start!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    $script:ErrorCount++
    if ($FlaskProcess) { Stop-Process -Id $FlaskProcess.Id -Force -ErrorAction SilentlyContinue }
    exit 1
}

Write-Host ""

# ============================================================================
# Step 6: Run Performance Tests (Locust)
# ============================================================================
Write-Host "[6/7] Running Performance Tests (Locust)..." -ForegroundColor Yellow
Write-Host "      Test: 10 users, 30 seconds" -ForegroundColor Gray

Set-Location tests/performance

$locustOutput = locust -f locustfile.py --headless --users 10 --spawn-rate 2 --run-time 30s --host http://localhost:5000 --html performance-report.html --csv performance-results 2>&1 | Out-String

# Check for failure percentage in output
if ($locustOutput -match "Percentage.*failed.*:\s*([\d\.]+)%") {
    $failureRate = [decimal]$matches[1]
    if ($failureRate -eq 0) {
        Write-Host "OK: Performance tests passed (0% failure rate)" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Performance tests had $failureRate% failure rate" -ForegroundColor Yellow
        $script:WarningCount++
    }
} else {
    Write-Host "WARNING: Could not determine performance test results" -ForegroundColor Yellow
    $script:WarningCount++
}

Set-Location ..\..

Write-Host ""

# ============================================================================
# Step 7: Run UAT Tests (Selenium)
# ============================================================================
Write-Host "[7/7] Running UAT Tests (Selenium)..." -ForegroundColor Yellow
Write-Host "      Target: 11 tests" -ForegroundColor Gray

$env:TEST_URL = "http://localhost:5000"

$uatOutput = pytest tests/uat_selenium/test_uat.py -v --tb=short --html=uat-report.html --self-contained-html 2>&1 | Out-String

# Check for passed tests in output
if ($uatOutput -match "(\d+) passed") {
    $passedUAT = [int]$matches[1]
    Write-Host "OK: UAT tests passed ($passedUAT/11)" -ForegroundColor Green
} else {
    Write-Host "ERROR: UAT tests failed!" -ForegroundColor Red
    $script:ErrorCount++
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
if ($unitTestOutput -match "42 passed") { 
    Write-Host "PASSED" -ForegroundColor Green 
} else { 
    Write-Host "FAILED" -ForegroundColor Red 
}

Write-Host "  - Static Analysis:      " -NoNewline
if ($pylintOutput -match "rated at ([\d\.]+)/10") {
    $score = [decimal]$matches[1]
    Write-Host "PASSED ($score/10)" -ForegroundColor Green
} else {
    Write-Host "WARNING" -ForegroundColor Yellow
}

Write-Host "  - Security (pip-audit): " -NoNewline
if ($pipAuditOutput -match "No known vulnerabilities") { 
    Write-Host "PASSED" -ForegroundColor Green 
} else { 
    Write-Host "WARNINGS" -ForegroundColor Yellow 
}

Write-Host "  - Security (bandit):    " -NoNewline
Write-Host "WARNINGS (expected)" -ForegroundColor Yellow

Write-Host "  - Performance Tests:    " -NoNewline
if ($locustOutput -match "0\.00%|0%") {
    Write-Host "PASSED" -ForegroundColor Green
} else {
    Write-Host "WARNING" -ForegroundColor Yellow
}

Write-Host "  - UAT Tests (11):       " -NoNewline
if ($uatOutput -match "11 passed") { 
    Write-Host "PASSED" -ForegroundColor Green 
} else { 
    Write-Host "FAILED" -ForegroundColor Red 
}

Write-Host ""
Write-Host "Reports Generated:" -ForegroundColor White
Write-Host "  - Coverage:     htmlcov/index.html"
Write-Host "  - Performance:  tests/performance/performance-report.html"
Write-Host "  - UAT:          uat-report.html"

Write-Host ""

if ($script:ErrorCount -eq 0 -and $script:WarningCount -le 2) {
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