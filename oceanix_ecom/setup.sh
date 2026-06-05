#!/bin/bash

# OCEANIX E-Commerce Platform - Quick Setup Script for macOS/Linux

echo ""
echo "========================================"
echo "  OCEANIX E-Commerce Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python from https://python.org"
    exit 1
fi

# Create virtual environment
echo "[1/6] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "[2/6] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[3/6] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Run migrations
echo "[4/6] Running database migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to run migrations"
    exit 1
fi

# Create superuser
echo "[5/6] Creating superuser account..."
echo ""
echo "Please enter superuser details:"
python manage.py createsuperuser
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create superuser"
    exit 1
fi

# Load sample products
echo "[6/6] Loading sample products..."
python manage.py load_sample_products
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to load sample products"
    exit 1
fi

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "Your OCEANIX website is ready to run!"
echo ""
echo "To start the development server, run:"
echo "  python manage.py runserver"
echo ""
echo "Then open your browser and visit:"
echo "  http://127.0.0.1:8000/"
echo ""
echo "For admin panel, go to:"
echo "  http://127.0.0.1:8000/admin/"
echo ""
