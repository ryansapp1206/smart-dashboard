require('dotenv').config();

// Core dependencies
const express = require('express');
const { google } = require('googleapis');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const app = express();

// Middleware setup
app.use(cors());
app.use(express.json());

// Google API Authentication securely loaded from .env
// A bad or missing key only disables the calendar route; local state routes keep working
let auth = null;
try {
  const credentials = JSON.parse(process.env.GOOGLE_CREDENTIALS);
  auth = new google.auth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/calendar.readonly']
  });
} catch (err) {
  console.error('Google credentials unavailable, calendar route disabled:', err.message);
}

// CALENDAR API ROUTE
app.get('/api/calendar', async (req, res) => {
  if (!auth) return res.status(503).json({ error: 'Calendar credentials not configured' });
  const calendar = google.calendar({ version: 'v3', auth });
  try {
    const now = new Date();

    // Establish the time window for fetched events
    // Start of the current month
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1, 0, 0, 0);

    // End of the current month
    const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59);

    // Exactly 7 days from now (end of day)
    const sevenDaysOut = new Date(now);
    sevenDaysOut.setDate(now.getDate() + 7);
    sevenDaysOut.setHours(23, 59, 59, 999);

    // Use whichever date reaches further into the future to ensure a rolling 7-day minimum buffer
    const maxDate = sevenDaysOut > endOfMonth ? sevenDaysOut : endOfMonth;

    // Fetch events from Google
    const response = await calendar.events.list({
      calendarId: process.env.CALENDAR_ID,
      timeMin: startOfMonth.toISOString(),
      timeMax: maxDate.toISOString(),
      singleEvents: true,
      orderBy: 'startTime',
    });

    res.json(response.data.items);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// LOCAL STATE MANAGEMENT ROUTES
// DATA_PATH lets tests point the server at a throwaway state file; production uses the default
const dataPath = process.env.DATA_PATH ? path.resolve(process.env.DATA_PATH) : path.join(__dirname, 'guitar_data.json');
const backupPath = dataPath + '.bak';
const tmpPath = dataPath + '.tmp';

// Keys the voice bridge / UI are allowed to change
const UPDATABLE_KEYS = ['current_view', 'is_listening', 'switches', 'pending_update', 'metronome_bpm', 'timer_active'];

// Read state from disk, falling back to the last good backup if the main file is corrupt
function loadState() {
  for (const file of [dataPath, backupPath]) {
    try {
      const parsed = JSON.parse(fs.readFileSync(file, 'utf8'));
      if (parsed && typeof parsed === 'object') return parsed;
    } catch (err) {
      console.error(`Could not read ${path.basename(file)}: ${err.message}`);
    }
  }
  throw new Error('No readable state file');
}

// Atomic write: temp file + fsync + rename, so a crash or power cut never leaves a half-written file
function saveState(state) {
  const json = JSON.stringify(state, null, 2);
  const fd = fs.openSync(tmpPath, 'w');
  try {
    fs.writeSync(fd, json);
    fs.fsyncSync(fd);
  } finally {
    fs.closeSync(fd);
  }
  try { fs.copyFileSync(dataPath, backupPath); } catch (err) { /* no previous file yet */ }
  fs.renameSync(tmpPath, dataPath);
}

// Fetch the current dashboard state
app.get('/api/guitar', (req, res) => {
  try {
    res.json(loadState());
  } catch (err) {
    res.status(500).send("Error reading guitar data");
  }
});

// Update the dashboard state based on Python Voice Bridge payloads
// Synchronous read-merge-write keeps every update atomic with respect to other requests
app.post('/api/guitar/update', (req, res) => {
  try {
    const guitarData = loadState();
    const body = req.body || {};

    for (const key of UPDATABLE_KEYS) {
      if (body[key] !== undefined) guitarData[key] = body[key];
    }

    saveState(guitarData);
    res.send({ status: "success" });
  } catch (err) {
    console.error('State update failed:', err.message);
    res.status(500).send("Error updating data layer");
  }
});

// Last-resort guards: log and keep the kiosk backend alive
process.on('uncaughtException', (err) => console.error('Uncaught exception:', err));
process.on('unhandledRejection', (err) => console.error('Unhandled rejection:', err));

// Start the server
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});