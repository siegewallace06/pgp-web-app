#!/bin/bash

# PGP Web Application - Quick Start Script
# This script helps you get the application running quickly

set -e

echo "🔐 PGP Web Application - Quick Start"
echo "===================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    
    # Generate a random secret key
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "change-this-secret-key-in-production")
    sed -i.bak "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
    rm .env.bak 2>/dev/null || true
    echo "✅ Created .env file with generated secret key"
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads gnupg_home logs ssl
echo "✅ Directories created"

# Build and start the application
echo "🚀 Building and starting the application..."
docker compose up -d --build

# Wait for the application to be ready
echo "⏳ Waiting for the application to start..."
sleep 10

# Check if the application is running
if curl -f http://localhost:8080/api/health > /dev/null 2>&1; then
    echo "✅ Application is running successfully!"
    echo ""
    echo "🌐 Access the application at: http://localhost:8080"
    echo ""
    echo "📚 Quick Guide:"
    echo "  1. Generate a PGP key pair: http://localhost:8080/generate-key"
    echo "  2. Encrypt files: http://localhost:8080/encrypt"
    echo "  3. Decrypt files: http://localhost:8080/decrypt"
    echo "  4. Manage keys: http://localhost:8080/keys"
    echo ""
    echo "🔧 Management Commands:"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Stop app: docker-compose down"
    echo "  • Restart: docker-compose restart"
    echo ""
    echo "📖 For more information, see README.md"
else
    echo "❌ Application failed to start. Check the logs:"
    echo "   docker-compose logs"
    exit 1
fi