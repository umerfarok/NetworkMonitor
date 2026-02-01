#!/bin/bash
# NetworkMonitor Download & Install Script
# Usage: curl -sSL https://raw.githubusercontent.com/umerfarok/networkmonitor/main/scripts/install.sh | bash

set -e

echo "======================================"
echo "    NetworkMonitor Installation"
echo "======================================"
echo ""

# Detect OS
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case "$OS" in
    linux*)
        PLATFORM="Linux"
        EXTENSION="tar.gz"
        ;;
    darwin*)
        PLATFORM="macOS"
        EXTENSION="zip"
        ;;
    *)
        echo "❌ Unsupported operating system: $OS"
        echo "   Please download manually from:"
        echo "   https://github.com/umerfarok/networkmonitor/releases"
        exit 1
        ;;
esac

echo "📋 Detected: $PLATFORM ($ARCH)"
echo ""

# Check for required tools
if ! command -v curl &> /dev/null; then
    echo "❌ 'curl' is required. Please install it first."
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "⚠️  'jq' not found. Installing..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y jq
    elif command -v brew &> /dev/null; then
        brew install jq
    else
        echo "❌ Please install 'jq' manually and retry."
        exit 1
    fi
fi

# Get latest release info
echo "🔍 Finding latest release..."
RELEASE_INFO=$(curl -s "https://api.github.com/repos/umerfarok/networkmonitor/releases/latest")
VERSION=$(echo "$RELEASE_INFO" | jq -r '.tag_name')

if [ "$VERSION" = "null" ]; then
    echo "❌ Could not find latest release."
    echo "   Please download manually from:"
    echo "   https://github.com/umerfarok/networkmonitor/releases"
    exit 1
fi

echo "📦 Latest version: $VERSION"
echo ""

# Find the download URL for our platform
DOWNLOAD_URL=$(echo "$RELEASE_INFO" | jq -r ".assets[] | select(.name | contains(\"$PLATFORM\")) | .browser_download_url" | head -1)

if [ -z "$DOWNLOAD_URL" ] || [ "$DOWNLOAD_URL" = "null" ]; then
    echo "❌ No release found for $PLATFORM"
    echo "   Please download manually from:"
    echo "   https://github.com/umerfarok/networkmonitor/releases"
    exit 1
fi

FILENAME=$(basename "$DOWNLOAD_URL")
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

echo "⬇️  Downloading $FILENAME..."
curl -L "$DOWNLOAD_URL" -o "/tmp/$FILENAME"

echo "📂 Extracting..."
cd /tmp

if [[ "$FILENAME" == *.tar.gz ]]; then
    tar -xzf "$FILENAME"
elif [[ "$FILENAME" == *.zip ]]; then
    unzip -o "$FILENAME"
fi

# Find the executable
EXECUTABLE=$(find . -maxdepth 2 -name "NetworkMonitor" -type f 2>/dev/null | head -1)

if [ -z "$EXECUTABLE" ]; then
    echo "⚠️  Executable not found in archive. Checking for app bundle..."
    if [ -d "NetworkMonitor.app" ]; then
        echo "📦 Found macOS app bundle"
        mv NetworkMonitor.app "$HOME/Applications/" 2>/dev/null || mv NetworkMonitor.app /Applications/
        echo "✅ Installed to Applications folder"
        echo ""
        echo "🚀 To run: Open 'NetworkMonitor' from Applications"
        exit 0
    fi
    echo "❌ Could not find NetworkMonitor executable"
    exit 1
fi

echo "📥 Installing to $INSTALL_DIR..."
chmod +x "$EXECUTABLE"
mv "$EXECUTABLE" "$INSTALL_DIR/networkmonitor"

# Add to PATH if needed
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "💡 Add this to your ~/.bashrc or ~/.zshrc:"
    echo "   export PATH=\"\$PATH:$INSTALL_DIR\""
fi

echo ""
echo "======================================"
echo "    ✅ Installation Complete!"
echo "======================================"
echo ""
echo "🚀 To start NetworkMonitor:"
echo "   sudo $INSTALL_DIR/networkmonitor"
echo ""
echo "📊 Then open: http://localhost:5000"
echo ""
echo "⚠️  Note: Run with sudo for network scanning"
echo ""

# Cleanup
rm -f "/tmp/$FILENAME"
