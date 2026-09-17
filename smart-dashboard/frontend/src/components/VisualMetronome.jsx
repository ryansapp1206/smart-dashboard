import { useState, useEffect, useRef } from 'react';

export default function VisualMetronome({ bpm = 0, currentView, timerActive }) {
  const [pulse, setPulse] = useState(false);
  const audioCtxRef = useRef(null);

  useEffect(() => {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!audioCtxRef.current && AudioContext) {
      audioCtxRef.current = new AudioContext();
    }
  }, []);

  const playClick = () => {
    if (!audioCtxRef.current) return;
    const ctx = audioCtxRef.current;
    if (ctx.state === 'suspended') ctx.resume();
    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();
    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);
    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(800, ctx.currentTime);
    oscillator.frequency.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);
    gainNode.gain.setValueAtTime(1, ctx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);
    oscillator.start(ctx.currentTime);
    oscillator.stop(ctx.currentTime + 0.1);
  };

  useEffect(() => {
    if (bpm <= 0 || currentView !== 'hub') return;
    const intervalMs = 60000 / bpm;
    const timer = setInterval(() => {
      playClick();
      setPulse(true);
      setTimeout(() => setPulse(false), 100); 
    }, intervalMs);
    return () => clearInterval(timer);
  }, [bpm, currentView]);

  if (bpm <= 0 || currentView !== 'hub' || timerActive) return null;

  return (
    <div className="fixed bottom-12 left-1/2 -translate-x-1/2 flex items-center gap-6 z-50 bg-zinc-900/90 px-12 py-6 rounded-full border border-zinc-700 backdrop-blur-xl shadow-2xl">
      <span className="text-[3rem] font-extrabold text-zinc-200 tracking-wider">{bpm} <span className="text-zinc-500">BPM</span></span>
      <div className={`w-8 h-8 rounded-full transition-all duration-75 ${pulse ? 'bg-blue-500 scale-150 shadow-[0_0_30px_rgba(59,130,246,1)]' : 'bg-zinc-700 scale-100 opacity-50'}`}></div>
    </div>
  );
}