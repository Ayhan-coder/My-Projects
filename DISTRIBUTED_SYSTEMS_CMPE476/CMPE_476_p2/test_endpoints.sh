#!/bin/bash
# Test script for CMPE476 Project 2
# Run all endpoints and verify responses

BASE_URL="http://localhost:8080"

echo "================================"
echo "Testing CMPE476 Project 2 Endpoints"
echo "================================"
echo ""

# Test 1: Health endpoint
echo "1. Testing /health endpoint:"
curl -i "$BASE_URL/health" 2>/dev/null | head -20
echo ""
echo ""

# Test 2: Root endpoint (GET /)
echo "2. Testing GET / endpoint:"
curl -i "$BASE_URL/" 2>/dev/null | head -20
echo ""
echo ""

# Test 3: Store endpoint
echo "3. Testing /store endpoint (store key-value):"
curl -i "$BASE_URL/store?key=course&value=distributed-systems" 2>/dev/null | head -20
echo ""
echo ""

# Test 4: Get endpoint
echo "4. Testing /get endpoint (retrieve value):"
curl -i "$BASE_URL/get?key=course" 2>/dev/null | head -20
echo ""
echo ""

# Test 5: Slow endpoint
echo "5. Testing /slow endpoint (3 second sleep):"
curl -i "$BASE_URL/slow?seconds=3" 2>/dev/null | head -20
echo ""
echo ""

# Test 6: Load distribution (30 requests)
echo "6. Testing load distribution across replicas (30 requests):"
echo "   Sending 30 requests and counting responses per server_id:"
for i in $(seq 30); do
    curl -s "$BASE_URL/" | grep -o '"server_id":"[^"]*"'
done | sort | uniq -c
echo ""
echo ""

# Test 7: Header verification
echo "7. Verifying X-Server-Id header is present:"
curl -i "$BASE_URL/" 2>/dev/null | grep -i "x-server-id"
echo ""
echo ""

echo "================================"
echo "Tests complete!"
echo "================================"
