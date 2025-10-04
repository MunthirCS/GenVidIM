# Fix Serverless Dockerfile - Step by Step
Write-Host ""
Write-Host "================================================================="
Write-Host "SERVERLESS DOCKERFILE FIX - AUTOMATED"
Write-Host "================================================================="
Write-Host ""

# Step 1
Write-Host "[Step 1/5] Checking if fixed Dockerfile exists..."
$fixedFile = "GenVidIM\serverless\Dockerfile.fixed"
if (Test-Path $fixedFile) {
    Write-Host "  OK Found: $fixedFile"
} else {
    Write-Host "  ERROR: $fixedFile not found!"
    exit 1
}

# Step 2
Write-Host ""
Write-Host "[Step 2/5] Checking original Dockerfile..."
$originalFile = "GenVidIM\serverless\Dockerfile"
if (Test-Path $originalFile) {
    Write-Host "  OK Found: $originalFile"
} else {
    Write-Host "  WARNING: Original Dockerfile not found!"
}

# Step 3
Write-Host ""
Write-Host "[Step 3/5] Creating backup..."
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "GenVidIM\serverless\Dockerfile.backup_$timestamp"

if (Test-Path $originalFile) {
    Copy-Item $originalFile $backupFile
    Write-Host "  OK Backup created: $backupFile"
} else {
    Write-Host "  Skipped (original not found)"
}

# Step 4
Write-Host ""
Write-Host "[Step 4/5] Replacing Dockerfile..."
Copy-Item $fixedFile $originalFile -Force
Write-Host "  OK Dockerfile updated!"

# Step 5
Write-Host ""
Write-Host "[Step 5/5] Verifying..."
$content = Get-Content $originalFile -Raw
if ($content -match "peft" -and $content -match "decord") {
    Write-Host "  OK Verified: peft and decord present"
} else {
    Write-Host "  WARNING: Could not verify"
}

Write-Host ""
Write-Host "================================================================="
Write-Host "DOCKERFILE UPDATE COMPLETE!"
Write-Host "================================================================="
Write-Host ""
Write-Host "NEXT STEPS:"
Write-Host "  1. Go to: https://runpod.io/console/serverless"
Write-Host "  2. Find endpoint: yn6sjkwfuqqk05"
Write-Host "  3. Click Edit or Settings"
Write-Host "  4. Trigger rebuild"
Write-Host "  5. Wait 10-15 minutes"
Write-Host "  6. Test with: python test_endpoint.py"
Write-Host ""

