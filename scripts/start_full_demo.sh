#!/bin/bash

# Complete Project Synapse Demo Startup Script

set -e

echo "🚀 Starting Project Synapse - Complete Demo Environment"
echo "=" * 60

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is required but not installed"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs monitoring/grafana/dashboards monitoring/grafana/datasources

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.full.yml down --remove-orphans

# Pull latest images
echo "📦 Pulling Docker images..."
docker-compose -f docker-compose.full.yml pull

# Start the complete stack
echo "🚀 Starting Project Synapse stack..."
docker-compose -f docker-compose.full.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

services=("redis:6379" "elasticsearch:9200" "postgres:5432")
for service in "${services[@]}"; do
    host=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    if nc -z localhost $port 2>/dev/null; then
        echo "✅ $host is healthy"
    else
        echo "⚠️  $host is not responding"
    fi
done

# Wait for API to be ready
echo "⏳ Waiting for Synapse API..."
timeout=60
counter=0

while [ $counter -lt $timeout ]; do
    if curl -f http://localhost:8080/health &>/dev/null; then
        echo "✅ Synapse API is healthy"
        break
    fi
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -ge $timeout ]; then
    echo "❌ Synapse API failed to start within $timeout seconds"
    echo "📋 Checking API logs..."
    docker-compose -f docker-compose.full.yml logs synapse-api
    exit 1
fi

# Wait for frontend to be ready
echo "⏳ Waiting for frontend..."
timeout=60
counter=0

while [ $counter -lt $timeout ]; do
    if curl -f http://localhost:3000 &>/dev/null; then
        echo "✅ Frontend is healthy"
        break
    fi
    sleep 2
    counter=$((counter + 2))
done

# Initialize demo data
echo "📊 Initializing demo data..."
if command -v python3 &> /dev/null; then
    python3 examples/basic_usage.py
    echo "✅ Demo data initialized"
else
    echo "⚠️  Python not found, skipping demo data initialization"
fi

# Display access information
echo ""
echo "🎉 Project Synapse is now running!"
echo "=" * 50
echo ""
echo "🌐 Access Points:"
echo "   Frontend (React UI):     http://localhost:3000"
echo "   Backend API:             http://localhost:8080"
echo "   API Documentation:       http://localhost:8080/docs"
echo "   Grafana Dashboards:      http://localhost:3001 (admin/admin)"
echo "   Prometheus Metrics:      http://localhost:9090"
echo ""
echo "🔧 Services:"
echo "   Redis Cache:             localhost:6379"
echo "   Elasticsearch:           localhost:9200"
echo "   PostgreSQL:              localhost:5432"
echo ""
echo "📖 Quick Start:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Navigate to 'Demo' to see interactive demonstrations"
echo "   3. Try the 'Query' interface for federated search"
echo "   4. Check 'Privacy Center' for privacy budget monitoring"
echo "   5. View 'Analytics' for system insights"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose -f docker-compose.full.yml down"
echo ""
echo "📋 To view logs:"
echo "   docker-compose -f docker-compose.full.yml logs -f [service-name]"
echo ""
echo "✨ Enjoy exploring Project Synapse!"