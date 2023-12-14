#!/bin/bash

# Start the Flask application
python3 /home/olec/smart_switch/src/app.py &

# Wait for the server to start (adjust the sleep duration if needed)
sleep 5

# Open the default browser (if a display is available)
if [ -n "$DISPLAY" ]; then
    firefox-esr -fullscreen http://0.0.0.0:5000/ &
    sleep 5 # Adjust the sleep duration as needed
    xdotool search --onlyvisible --class "Firefox" windowactivate --sync key F11
fi
