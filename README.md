# Smart Kiosk Dashboard

This is a voice-activated smart dashboard built to run 24/7 on a dedicated Ubuntu thinclient. It displays real-time schedule data and listens for offline voice commands, with the entire stack running locally on the machine.

## System Architecture

To prevent dependency conflicts and keep the codebase maintainable, the system is split into three isolated services:

* **Frontend (React + Vite):** The user interface. It is hosted locally and renders real-time telemetry and calendar data.
* **Backend (Node.js / Express):** A local API server that handles the heavy lifting. It securely fetches and formats data from the Google Calendar API to feed to the frontend.
* **Voice Bridge (Python):** An entirely offline voice recognition service. It uses Vosk and PyAudio to listen for a wake word ("Jarvis") and trigger dashboard commands locally, completely bypassing cloud-based speech-to-text.

## Hardware & Deployment

* **Hardware:** Lenovo ThinkCentre M700
* **OS:** Ubuntu Linux
* **Display:** Hosted locally on `http://localhost:5173` and rendered via Chromium.
* **Automated Boot:** The system requires zero manual intervention to start. An Ubuntu `.desktop` autostart configuration triggers a master shell script (`start-jarvis.sh`) immediately upon user login.
* **Process Management:** The startup script manages local ports, boots the Node servers in the background, routes Python execution strictly through an isolated virtual environment (`venv`), and forces Chromium into a locked `--kiosk` mode with hardware autoplay enabled.

## Security Posture

* **Credential Management:** All Google Cloud service account keys, API endpoints, and authentication tokens are scrubbed from the codebase and managed entirely via local `.env` files.
* **Version Control:** Strict `.gitignore` rules prevent the accidental staging of virtual environments, `node_modules`, and local system paths.