# scripts/cleanup-reports.ps1
# Cleans local/pipeline-generated artifacts that should not be committed.

$ErrorActionPreference = "SilentlyContinue"

$paths = @(
  "test-results.xml",
  "uat-results.xml",
  "coverage.xml",
  "uat-report.html",
  "deploy.zip",
  "app.log",
  "htmlcov",
  "screenshots",
  ".pytest_cache",
  "tests\performance\performance-report.html",
  "tests\performance\performance-results_stats.csv",
  "tests\performance\performance-results_failures.csv"
)

foreach ($p in $paths) {
  if (Test-Path $p) {
    Remove-Item -Force -Recurse $p
    Write-Host "Removed: $p"
  } else {
    Write-Host "Not found: $p"
  }
}

Write-Host "Cleanup complete."
