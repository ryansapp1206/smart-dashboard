import { useState, useEffect } from 'react';

export function useDashboardState() {
  const [time, setTime] = useState(new Date());
  const [weather, setWeather] = useState(null);
  const [events, setEvents] = useState([]);
  const [guitarData, setGuitarData] = useState({ current_view: 'calendar' });
  const [autoView, setAutoView] = useState('month');
  const [apiLatency, setApiLatency] = useState(0);
  const [requestCount, setRequestCount] = useState(0);

  // Poll local state database every 500ms to instantly reflect voice commands
  // Tracks request latency for the frontend debug UI
  useEffect(() => {
    const fetchGuitarData = async () => {
      const startTime = performance.now();
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/guitar`);
        
        // Failsafe: Ignore 204 No Content responses if the backend is actively rewriting the JSON file
        if (response.status === 204) return;
        
        const data = await response.json();
        setGuitarData(data);
        
        const endTime = performance.now();
        setApiLatency(Math.round(endTime - startTime));
        setRequestCount(prev => prev + 1);
      } catch (error) {
        console.error("Failed to fetch guitar data:", error);
        setApiLatency('ERR');
      }
    };
    fetchGuitarData();
    const guitarInterval = setInterval(fetchGuitarData, 500);
    return () => clearInterval(guitarInterval);
  }, []);

  // Auto-rotate calendar views when idling on the home screen
  // Month view holds for 60s, week view holds for 15s
  // TO-DO FIND OPTIMAL TIMING FOR ROTATION BASED ON USER FEEDBACK
  useEffect(() => {
    let rotationTimer;
    if (guitarData?.current_view === 'calendar') {
      if (autoView === 'month') {
        rotationTimer = setTimeout(() => setAutoView('week'), 60000);
      } else if (autoView === 'week') {
        rotationTimer = setTimeout(() => setAutoView('month'), 15000);
      }
    } else {
      setAutoView('month');
    }
    return () => clearTimeout(rotationTimer);
  }, [guitarData?.current_view, autoView]);

  // Fetch and format Google Calendar events every 10 minutes
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/calendar`);
        const data = await response.json();
        const rawEvents = Array.isArray(data) ? data : (data.items || []);
        
        const formattedEvents = rawEvents.map((item, index) => {
          const startObj = item.start || {};
          let startDate = startObj.dateTime ? new Date(startObj.dateTime) : new Date(startObj.date ? startObj.date + 'T00:00:00' : new Date());
          return {
            id: index,
            title: item.summary || 'No Title',
            start: startDate,
            time: startObj.dateTime ? startDate.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }) : 'All Day',
            color: 'bg-blue-500'
          };
        });
        setEvents(formattedEvents);
      } catch (error) {
        console.error("Failed to fetch events:", error);
      }
    };
    fetchEvents();
    const interval = setInterval(fetchEvents, 600000);
    return () => clearInterval(interval);
  }, []);

  // Real-time clock synchronization for the UI
  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Poll Open-Meteo weather API every 15 minutes to avoid rate limits
  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const lat = import.meta.env.VITE_WEATHER_LAT;
        const lon = import.meta.env.VITE_WEATHER_LON;
        const response = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true&temperature_unit=fahrenheit`);
        const data = await response.json();
        setWeather(data.current_weather);
      } catch (error) {
        console.error("Failed to fetch weather:", error);
      }
    };
    fetchWeather();
    const weatherInterval = setInterval(fetchWeather, 900000);
    return () => clearInterval(weatherInterval);
  }, []);

  return { time, weather, events, guitarData, autoView, apiLatency, requestCount };
}