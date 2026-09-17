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
const credentials = JSON.parse(process.env.GOOGLE_CREDENTIALS);
const auth = new google.auth.GoogleAuth({
  credentials,
  scopes: ['https://www.googleapis.com/auth/calendar.events']
});

// CALENDAR API ROUTE
app.get('/api/calendar', async (req, res) => {
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
const dataPath = path.join(__dirname, 'guitar_data.json');

// Fetch the current dashboard state
app.get('/api/guitar', (req, res) => {
  fs.readFile(dataPath, 'utf8', (err, data) => {
    if (err) return res.status(500).send("Error reading guitar data");
    try {
        res.json(JSON.parse(data));
    } catch (parseError) {
        // Race condition safeguard: If file is read mid-write, return 204 (No Content) to prevent JSON parse crash
        // TO-DO COMPLETELY REMOVE POSSIBILITY OF RACE CONDITION
        res.status(204).send(); 
    }
  });
});

// Update the dashboard state based on Python Voice Bridge payloads
app.post('/api/guitar/update', (req, res) => {
  fs.readFile(dataPath, 'utf8', (err, data) => {
    if (err) return res.status(500).send("Error reading data layer");

    let guitarData = JSON.parse(data);

    // Selectively update state properties only if they exist in the incoming request
    // TO-DO REFACTOR AT A LATER DATE
    if (req.body.current_view) {
      guitarData.current_view = req.body.current_view;
    }
    if (req.body.is_listening !== undefined) {
      guitarData.is_listening = req.body.is_listening;
    }
    // Save the updated chord switch tracking array
    if (req.body.switches !== undefined) {
      guitarData.switches = req.body.switches;
    }
    // Handle the temporary confirmation modal state for UI popups
    if (req.body.pending_update !== undefined) {
      guitarData.pending_update = req.body.pending_update;
    }
    if (req.body.metronome_bpm !== undefined) {
      guitarData.metronome_bpm = req.body.metronome_bpm;
    }
    // Handle practice timer boolean state
    if (req.body.timer_active !== undefined) {
      guitarData.timer_active = req.body.timer_active;
    }

    // Write the merged state back to the local JSON file
    fs.writeFile(dataPath, JSON.stringify(guitarData, null, 2), (err) => {
      if (err) return res.status(500).send("Error writing to data layer");
      res.send({ status: "success" });
    });
  });
});

// Start the server
app.listen(3001, () => {
  console.log('Server listening on port 3001');
});