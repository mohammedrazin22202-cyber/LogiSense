#!/bin/bash
# Fleet Command - Startup Script

echo "🚛 TRACK FLEET COMMAND"
echo "================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi

# Check Flask
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing Flask..."
    pip install flask openpyxl --break-system-packages
fi

cd "$(dirname "$0")"

# Seed if database doesn't exist or is empty
if [ ! -f "data/fleet.db" ]; then
    echo "📦 Seeding database from orders_master.xlsx..."
    python3 backend/seed.py
fi

echo "🌐 Starting server at http://localhost:1996"
echo "Press Ctrl+C to stop"
echo ""
python3 backend/server.py
