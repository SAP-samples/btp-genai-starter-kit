#!/bin/bash

# Script to install poppler-utils and tesseract to the DevContainer

# Check if the script is run with sudo privileges
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or with sudo"
  exit 1
fi

# Update package lists
echo "Updating package lists..."
apt-get update

# Check if the update was successful
if [ $? -ne 0 ]; then
    echo "Failed to update package lists. Please check your internet connection and try again."
    exit 1
fi

# Install poppler-utils
echo "Installing poppler-utils..."
apt-get install -y poppler-utils

# Check if the installation was successful
if [ $? -eq 0 ]; then
    echo "poppler-utils installed successfully!"
else
    echo "Failed to install poppler-utils. Please check the error messages above."
    exit 1
fi

# Install tesseract
echo "Installing tesseract..."
apt-get install -y tesseract-ocr

# Check if the installation was successful
if [ $? -eq 0 ]; then
    echo "tesseract installed successfully!"
else
    echo "Failed to install tesseract. Please check the error messages above."
    exit 1
fi

# Verify installations
if command -v pdfinfo >/dev/null 2>&1; then
    echo "Verification: pdfinfo command is available."
else
    echo "Verification failed: pdfinfo command not found. Installation of poppler-utils may have been incomplete."
    exit 1
fi

if command -v tesseract >/dev/null 2>&1; then
    echo "Verification: tesseract command is available."
    echo "Installation completed successfully."
else
    echo "Verification failed: tesseract command not found. Installation may have been incomplete."
    exit 1
fi