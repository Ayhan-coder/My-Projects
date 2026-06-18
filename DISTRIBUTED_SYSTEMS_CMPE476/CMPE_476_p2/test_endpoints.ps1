# PowerShell test script for CMPE476 Project 2
# Run all endpoints and verify responses

$BASE_URL = "http://localhost:8080"

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Testing CMPE476 Project 2 Endpoints" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health endpoint
Write-Host "1. Testing /health endpoint:" -ForegroundColor Yellow
$response = curl -i "$BASE_URL/health" 2>&1 | Select-Object -First 20
$response
Write-Host ""
Write-Host ""

# Test 2: Root endpoint (GET /)
Write-Host "2. Testing GET / endpoint:" -ForegroundColor Yellow
$response = curl -i "$BASE_URL/" 2>&1 | Select-Object -First 20
$response
Write-Host ""
Write-Host ""

# Test 3: Store endpoint
Write-Host "3. Testing /store endpoint (store key-value):" -ForegroundColor Yellow
$response = curl -i "$BASE_URL/store?key=course&value=distributed-systems" 2>&1 | Select-Object -First 20
$response
Write-Host ""
Write-Host ""

# Test 4: Get endpoint
Write-Host "4. Testing /get endpoint (retrieve value):" -ForegroundColor Yellow
$response = curl -i "$BASE_URL/get?key=course" 2>&1 | Select-Object -First 20
$response
Write-Host ""
Write-Host ""

# Test 5: Slow endpoint
Write-Host "5. Testing /slow endpoint (3 second sleep):" -ForegroundColor Yellow
$response = curl -i "$BASE_URL/slow?seconds=3" 2>&1 | Select-Object -First 20
$response
Write-Host ""
Write-Host ""

# Test 6: Load distribution (30 requests)
Write-Host "6. Testing load distribution across replicas (30 requests):" -ForegroundColor Yellow
Write-Host "   Sending 30 requests and counting responses per server_id:" -ForegroundColor Yellow
$servers = @{}
1..30 | ForEach-Object {
    $response = curl -s "$BASE_URL/" | ConvertFrom-Json
    $serverId = $response.server_id
    if ($servers.ContainsKey($serverId)) {
        $servers[$serverId]++
    } else {
        $servers[$serverId] = 1
    }
}
$servers | Format-Table -AutoSize
Write-Host ""
Write-Host ""

# Test 7: Header verification
Write-Host "7. Verifying X-Server-Id header is present:" -ForegroundColor Yellow
$response = curl -i "$BASE_URL/" 2>&1 | Select-String "X-Server-Id" -CaseSensitive
$response
Write-Host ""
Write-Host ""

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Tests complete!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
