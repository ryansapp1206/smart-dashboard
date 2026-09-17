import { useState, useEffect, useRef } from 'react';

export default function VisualMetronome({ bpm = 0, currentView, timerActive }) {
  const [pulse, setPulse] = useState(false);
  const audioCtxRef = useRef(null);

  // Initialize the Web Audio API context once on component mount
  useEffect(() => {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!audioCtxRef.current && AudioContext) {
      audioCtxRef.current = new AudioContext();
    }
  }, []);

  // Synthesizes a sharp, percussive metronome "click" natively
  const playClick = () => {
    if (!audioCtxRef.current) return;
    const ctx = audioCtxRef.current;
    
    // Resume context if suspended (browser autoplay policy safeguard)
    if (ctx.state === 'suspended') ctx.resume();
    
    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);
    
    // Envelope shaping: Rapid pitch and volume drop to simulate a mechanical click
    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(800, ctx.currentTime);
    oscillator.frequency.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);
    
    gainNode.gain.setValueAtTime(1, ctx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);
    
    oscillator.start(ctx.currentTime);
    oscillator.stop(ctx.currentTime + 0.1);
  };

  // Metronome Engine: Translates BPM into milliseconds and drives the audio/visual loop
  useEffect(() => {
    // Only run if a valid BPM is set and the user is on the Chord Hub
    if (bpm <= 0 || currentView !== 'hub') return;
    
    const intervalMs = 60000 / bpm;
    const timer = setInterval(() => {
      playClick();
      
      // Flash the visual indicator for 100ms
      setPulse(true);
      setTimeout(() => setPulse(false), 100); 
    }, intervalMs);
    
    return () => clearInterval(timer);
  }, [bpm, currentView]);

  // Hide the metronome UI if inactive, not in the Hub, or if the Practice Timer is currently taking over the screen
  if (bpm <= 0 || currentView !== 'hub' || timerActive) return null;

  return (
    <div className="fixed bottom-12 left-1/2 -translate-x-1/2 flex items-center gap-6 z-50 bg-zinc-900/90 px-12 py-6 rounded-full border border-zinc-700 backdrop-blur-xl shadow-2xl">
      <span className="text-[3rem] font-extrabold text-zinc-200 tracking-wider">
        {bpm} <span className="text-zinc-500">BPM</span>
      </span>
      
      {/* Visual pulse indicator (Expands and glows blue in sync with the audio click) */}
      <div className={`w-8 h-8 rounded-full transition-all duration-75 ${pulse ? 'bg-blue-500 scale-150 shadow-[0_0_30px_rgba(59,130,246,1)]' : 'bg-zinc-700 scale-100 opacity-50'}`}></div>
    </div>
  );
}