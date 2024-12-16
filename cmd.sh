#!/bin/bash

# Configuration
FRAMEBUFFER="/dev/fb1"
BROWSER="/usr/bin/chromium-browser"
URL="http://localhost:5000"
WINDOW_WIDTH=120
WINDOW_HEIGHT=370
SCALE_FACTOR=0.65

# Function to check if running on Raspberry Pi
check_raspberry_pi() {
    if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
        echo "Error: This script must be run on a Raspberry Pi"
        exit 1
    fi
}

# Function to check if PiTFT framebuffer exists
check_framebuffer() {
    if [ ! -e "$FRAMEBUFFER" ]; then
        echo "Error: Framebuffer $FRAMEBUFFER not found"
        echo "Please ensure PiTFT is properly configured"
        exit 1
    fi
}

# Function to check if Chromium browser is installed
check_browser() {
    if [ ! -f "$BROWSER" ]; then
        echo "Error: Chromium browser not found at $BROWSER"
        exit 1
    fi
}

# Main execution
main() {
    # Run checks
    check_raspberry_pi
    check_framebuffer
    check_browser

    # Launch browser with specified configuration
    echo "Launching Chromium browser on PiTFT display..."
    sudo FRAMEBUFFER=$FRAMEBUFFER startx $BROWSER \
        --no-sandbox \
        --kiosk \
        --window-size=$WINDOW_WIDTH,$WINDOW_HEIGHT \
        --window-position=0,0 \
        --force-device-scale-factor=$SCALE_FACTOR \
        "$URL"
}

# Execute main function
main
