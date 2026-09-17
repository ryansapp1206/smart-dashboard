require('dotenv').config();

const express = require('express');
const { google } = require('googleapis');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const app = express();

app.use(cors());
app.use(express.json());

const credentials = JSON.parse(process.env.GOOGLE_CREDENTIALS);
const auth = new google.auth.GoogleAuth({
  credentials,
  scopes: ['https://www.googleapis.com/auth/calendar.events']
});

app.get('/api/calendar', async (req, res) => {
  const calendar = google.calendar({ version: 'v3', auth });
  try {
    const now = new Date();

    // 1. Start of the current month (captures past events from this month)
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1, 0, 0, 0);

    // 2. End of the current month
    const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59);

    // 3. Exactly 7 days from now (end of day)
    const sevenDaysOut = new Date(now);
    sevenDaysOut.setDate(now.getDate() + 7);
    sevenDaysOut.setHours(23, 59, 59, 999);

    // Use whichever date reaches further into the future
    const maxDate = sevenDaysOut > endOfMonth ? sevenDaysOut : endOfMonth;

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

const dataPath = path.join(__dirname, 'guitar_data.json');

app.get('/api/guitar', (req, res) => {
  fs.readFile(dataPath, 'utf8', (err, data) => {
    if (err) return res.status(500).send("Error reading guitar data");
    res.json(JSON.parse(data));
  });
});

app.post('/api/guitar/update', (req, res) => {
  fs.readFile(dataPath, 'utf8', (err, data) => {
    if (err) return res.status(500).send("Error reading data layer");

    let guitarData = JSON.parse(data);

    if (req.body.current_view) {
      guitarData.current_view = req.body.current_view;
    }
    if (req.body.is_listening !== undefined) {
      guitarData.is_listening = req.body.is_listening;
    }
    // NEW: Save the updated chord switch array
    if (req.body.switches !== undefined) {
      guitarData.switches = req.body.switches;
    }
    // NEW: Handle the temporary confirmation modal state
    if (req.body.pending_update !== undefined) {
      guitarData.pending_update = req.body.pending_update;
    }
    if (req.body.metronome_bpm !== undefined) {
      guitarData.metronome_bpm = req.body.metronome_bpm;
    }
    // NEW: Handle Timer State
    if (req.body.timer_active !== undefined) {
      guitarData.timer_active = req.body.timer_active;
    }
    // ----------------------

    fs.writeFile(dataPath, JSON.stringify(guitarData, null, 2), (err) => {
      if (err) return res.status(500).send("Error writing to data layer");
      res.send({ status: "success" });
    });
  });
});

app.listen(3001, () => {
  console.log('Server listening on port 3001');
});
