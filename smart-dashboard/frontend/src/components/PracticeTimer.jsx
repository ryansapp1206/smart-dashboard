import { useState, useEffect, useRef } from 'react';

export default function PracticeTimer({ timerActive }) {
  const [phase, setPhase] = useState('idle');
  const [timeLeft, setTimeLeft] = useState(0);
  const audioCtxRef = useRef(null);

  // Synthesizes a dual-tone chime (A5 & C#6) using the Web Audio API.
  // This ensures the alert plays natively without relying on external media files.
  const playChime = () => {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!audioCtxRef.current && AudioContext) audioCtxRef.current = new AudioContext();
    if (!audioCtxRef.current) return;
    
    const ctx = audioCtxRef.current;
    if (ctx.state === 'suspended') ctx.resume();
    
    const osc1 = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const gainNode = ctx.createGain();
    
    osc1.type = 'sine'; osc2.type = 'sine';
    osc1.frequency.setValueAtTime(880, ctx.currentTime);
    osc2.frequency.setValueAtTime(1108.73, ctx.currentTime); 
    
    osc1.connect(gainNode); osc2.connect(gainNode);
    gainNode.connect(ctx.destination);
    
    // Envelope shaping: Instant attack, 2-second exponential fade out
    gainNode.gain.setValueAtTime(0, ctx.currentTime);
    gainNode.gain.linearRampToValueAtTime(1, ctx.currentTime + 0.05);
    gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 2);
    
    osc1.start(ctx.currentTime); osc2.start(ctx.currentTime);
    osc1.stop(ctx.currentTime + 2); osc2.stop(ctx.currentTime + 2);
  };

  // Watch for backend state changes to trigger the timer sequence
  useEffect(() => {
    if (timerActive && phase === 'idle') {
      setPhase('getReady');
      setTimeLeft(5); // 5-second buffer to physically prepare the guitar
    } else if (!timerActive) {
      setPhase('idle');
    }
  }, [timerActive]);

  // Main countdown interval and phase state machine
  useEffect(() => {
    if (phase === 'idle') return;
    
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          // Transition from prep phase to actual 60-second practice phase
          if (phase === 'getReady') {
            setPhase('running');
            return 60;
          } 
          // Timer concludes: Play chime, wait 3 seconds, then tell backend to reset state
          else if (phase === 'running') {
            setPhase('done');
            playChime();
            setTimeout(() => {
               fetch(`${import.meta.env.VITE_API_BASE_URL}/api/guitar/update`, {
                 method: 'POST',
                 headers: { 'Content-Type': 'application/json' },
                 body: JSON.stringify({ timer_active: false })
               });
            }, 3000);
            return 0;
          } else {
            return 0;
          }
        }
        return prev - 1;
      });
    }, 1000);
    
    return () => clearInterval(timer);
  }, [phase]);

  if (phase === 'idle') return null;

  // Phase 1: Full-screen countdown block so user can get hands on the fretboard
  if (phase === 'getReady') {
    return (
      <div className="fixed inset-0 flex items-center justify-center z-50 bg-zinc-950/80 backdrop-blur-md pointer-events-none">
        <span className="text-[15rem] font-black text-white drop-shadow-[0_0_60px_rgba(255,255,255,0.4)]">
          {timeLeft}
        </span>
      </div>
    );
  }

  const isDone = phase === 'done';
  return (
    <>
      {/* Background vignette (Pulses red when finished) */}
      <div className={`fixed inset-0 pointer-events-none z-40 transition-opacity duration-1000 ${isDone ? 'animate-pulse shadow-[inset_0_0_120px_rgba(239,68,68,0.3)] bg-[radial-gradient(ellipse_at_center,_transparent_50%,_rgba(239,68,68,0.2)_100%)]' : 'shadow-[inset_0_0_40px_rgba(239,68,68,0.1)]'}`}></div>
      
      {/* Floating timer pill at the bottom center of the screen */}
      <div className={`fixed bottom-12 left-1/2 -translate-x-1/2 flex items-center justify-center min-w-[250px] z-50 bg-zinc-900/90 px-12 py-6 rounded-full border backdrop-blur-xl shadow-2xl transition-colors duration-500 ${isDone ? 'border-red-500/50 shadow-[0_0_40px_rgba(239,68,68,0.4)]' : 'border-zinc-700'}`}>
        <span className={`text-[4rem] font-black tracking-widest tabular-nums ${isDone ? 'text-red-400' : 'text-zinc-200'}`}>
          0:{timeLeft.toString().padStart(2, '0')}
        </span>
      </div>
    </>
  );
}