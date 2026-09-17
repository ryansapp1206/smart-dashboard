#!/bin/bash

# 1. Boot the Node.js Backend
cd /home/ryan/jarvis-dashboard/smart-dashboard/backend
node server.js &

# 2. Boot the Vite Frontend
cd /home/ryan/jarvis-dashboard/smart-dashboard/frontend
npm run dev &

# 3. Boot the Python Voice Bridge
cd /home/ryan/jarvis-dashboard/guitar-voice-bridge
/home/ryan/jarvis-dashboard/guitar-voice-bridge/venv/bin/python listener.py &

# 4. Wait for servers to spin up
sleep 5

# 5. Launch the Dashboard UI
chromium-browser --kiosk --window-position=0,0 --window-size=4096,2160 --autoplay-policy=no-user-gesture-required http://localhost:5173
