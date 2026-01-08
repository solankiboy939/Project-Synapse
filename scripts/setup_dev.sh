#!/bin/bash

# Development setup script for Project Synapse

set -e

echo "🚀 Setting up Project Synapse development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "🛠️  Installing development dependencies..."
pip install -e ".[dev]"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs monitoring/grafana/dashboards monitoring/grafana/datasources

# Initialize configuration
echo "⚙️  Initializing configuration..."
python -m synapse.cli init --config-path config/dev.yaml

# Run tests to verify setup
echo "🧪 Running tests..."
python -m pytest tests/ -v

# Setup pre-commit hooks (if available)
if command -v pre-commit &> /dev/null; then
    echo "🪝 Setting up pre-commit hooks..."
    pre-commit install
fi

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "   1. Activate the virtual environment: source venv/bin/activate"
echo "   2. Start the indexer: synapse indexer start"
echo "   3. Start the API server: synapse server start"
echo "   4. Run demos: python scripts/run_demo.py"
echo "   5. View API docs: http://localhost:8080/docs"
echo ""
echo "📖 For more information, see the README.md file"