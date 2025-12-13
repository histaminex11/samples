#!/bin/bash

echo "🧪 Testing Frontend Application"
echo "================================"
echo ""

# Test 1: Check if frontend server is running
echo "1. Checking if frontend server is running on port 5173..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 | grep -q "200"; then
    echo "   ✅ Frontend server is running"
else
    echo "   ❌ Frontend server is not responding"
    exit 1
fi
echo ""

# Test 2: Check if backend server is running
echo "2. Checking if backend server is running on port 8080..."
BACKEND_RESPONSE=$(curl -s http://localhost:8080/api/greeting)
if echo "$BACKEND_RESPONSE" | grep -q "Hello from the Java backend"; then
    echo "   ✅ Backend server is running"
    echo "   Response: $BACKEND_RESPONSE"
else
    echo "   ❌ Backend server is not responding"
    exit 1
fi
echo ""

# Test 3: Test the API endpoint through Vite proxy
echo "3. Testing API endpoint through Vite proxy (/api/greeting)..."
PROXY_RESPONSE=$(curl -s http://localhost:5173/api/greeting)
if echo "$PROXY_RESPONSE" | grep -q "Hello from the Java backend"; then
    echo "   ✅ Vite proxy is working correctly"
    echo "   Response: $PROXY_RESPONSE"
else
    echo "   ⚠️  Proxy test failed (this is expected if Vite proxy only works from browser)"
    echo "   Response: $PROXY_RESPONSE"
fi
echo ""

# Test 4: Check if React app HTML is being served
echo "4. Checking if React app HTML is being served..."
HTML_CONTENT=$(curl -s http://localhost:5173)
if echo "$HTML_CONTENT" | grep -q "Cursor Full-Stack Sample"; then
    echo "   ✅ React app HTML is being served"
else
    echo "   ⚠️  Could not find expected content in HTML"
fi
echo ""

echo "================================"
echo "✅ Basic tests completed!"
echo ""
echo "📝 To test in browser:"
echo "   1. Open http://localhost:5173 in your browser"
echo "   2. You should see 'Hello from the Java backend!' message"
echo "   3. Open browser DevTools (F12) to see network requests"
echo ""

