#!/bin/bash

# Start the Flask application
python3 /home/olec/smart_switch/src/app.py &

# Wait for the server to start (adjust the sleep duration if needed)
sleep 5

# Open the default browser (if a display is available)
if [ -n "$DISPLAY" ]; then
    # Simulate F11 keypress to maximize the window
    xdotool key F11

    # Start Chromium in kiosk mode
    chromium-browser --app=http://0.0.0.0:5000/ --start-fullscreen --kiosk --start-maximized &

    # Wait for Chromium to open (adjust the sleep duration if needed)
    sleep 5

    # Hide the mouse cursor using unclutter
    unclutter -idle 0.1 -root &
fi
