#!/bin/bash

# The backend, frontend and voice bridge are supervised by PM2 (started at boot by pm2-ryan.service,
# auto-restarted on crash). This script must NOT launch them again, or each runs twice and the
# duplicate voice bridges fight over the microphone. It only waits for the services, then opens the kiosk.

# Only one kiosk launcher at a time
exec 9>/tmp/jarvis-kiosk.lock
flock -n 9 || exit 0

# Wait (up to 2 minutes) for the API and the UI to actually answer instead of sleeping a fixed time
wait_for() {
  for _ in $(seq 1 60); do
    curl -fs -o /dev/null --max-time 2 "$1" && return 0
    sleep 2
  done
  echo "Timed out waiting for $1" >&2
  return 1
}
wait_for http://127.0.0.1:3001/api/guitar
wait_for http://127.0.0.1:5173

# Launch dashboard in full-screen kiosk mode.
# Autoplay policy is overridden to allow immediate audio playback
exec chromium-browser --kiosk --window-position=0,0 --window-size=4096,2160 --autoplay-policy=no-user-gesture-required http://localhost:5173
