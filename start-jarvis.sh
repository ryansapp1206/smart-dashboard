#!/bin/bash

# Initialize Node.js backend as a background process to manage local JSON state and API routes
cd /home/ryan/jarvis-dashboard/smart-dashboard/backend
node server.js &

# Initialize Vite frontend as a background process to serve the React UI
cd /home/ryan/jarvis-dashboard/smart-dashboard/frontend
npm run dev &

# Boot the Python Voice Bridge using the isolated virtual environment binary.
cd /home/ryan/jarvis-dashboard/guitar-voice-bridge
/home/ryan/jarvis-dashboard/guitar-voice-bridge/venv/bin/python listener.py &

# Buffer period to prevent UI race conditions
# TO-DO: REFACTOR TO PROHBIT RACE CONDITIONS ALL TOGETHER
sleep 5

# Launch dashboard in full-screen kiosk mode. 
# Autoplay policy is overridden to allow immediate audio playback
chromium-browser --kiosk --window-position=0,0 --window-size=4096,2160 --autoplay-policy=no-user-gesture-required http://localhost:5173