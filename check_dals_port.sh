#!/bin/bash
# DALS Port Detection and Test Script

echo "🔍 DALS Port Detection and Testing"
echo "=================================="

# Check what's listening on common ports
echo "📡 Checking active ports..."
for port in 8003 8004 8005; do
    if netstat -tulpn 2>/dev/null | grep -q ":$port "; then
        echo "   ✅ Port $port is active"
        # Try to get response from each port
        if curl -s -m 2 "http://localhost:$port" >/dev/null 2>&1; then
            echo "      📱 HTTP response on port $port"
        elif curl -s -m 2 "http://localhost:$port/health" >/dev/null 2>&1; then
            echo "      📱 Health endpoint responding on port $port"
        elif curl -s -m 2 "http://localhost:$port/docs" >/dev/null 2>&1; then
            echo "      📱 Docs endpoint responding on port $port"
        else
            echo "      ❌ No HTTP response on port $port"
        fi
    else
        echo "   ❌ Port $port is not active"
    fi
done

echo ""
echo "🌐 Testing DALS endpoints..."

# Test DALS on different ports and endpoints
for port in 8003 8004 8005; do
    for endpoint in "" "/health" "/docs" "/api/v1/iss/now"; do
        url="http://localhost:$port$endpoint"
        if curl -s -m 3 "$url" >/dev/null 2>&1; then
            echo "   ✅ $url is responding"
        fi
    done
done

echo ""
echo "🔧 Current configuration check..."
echo "DALS .env port: $(grep '^port=' .env 2>/dev/null || echo 'not found')"

echo ""
echo "💡 Quick fix options:"
echo "1. Start DALS on port 8003: python start_server.py"
echo "2. Start DALS with custom port: ISS_PORT=8004 python start_server.py"
echo "3. Check Docker: docker-compose ps"