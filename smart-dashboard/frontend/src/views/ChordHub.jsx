export default function ChordHub({ switches }) {
  return (
    <div key="hub" className="fixed inset-0 box-border overflow-hidden bg-zinc-950 px-32 pb-8 pt-24 flex flex-col items-center animate-fade-in bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-zinc-900 via-zinc-950 to-zinc-950">
      <h1 className="text-[3.5rem] font-bold text-zinc-500 mb-12 tracking-[0.2em] uppercase shrink-0">Performance Matrix</h1>
      
      <div className="w-full h-full grid grid-cols-7 gap-6 items-start content-start">
        {switches?.map((sw, idx) => {
          let colorClasses = 'text-zinc-400 border-zinc-800 bg-zinc-900/30';
          if (sw.score >= 60) colorClasses = 'text-emerald-400 border-emerald-500/30 bg-emerald-950/20 shadow-[0_0_20px_rgba(16,185,129,0.05)]';
          else if (sw.score >= 30) colorClasses = 'text-amber-400 border-amber-500/30 bg-amber-950/20';
          else if (sw.score > 0) colorClasses = 'text-rose-400 border-rose-500/30 bg-rose-950/20';
          
          return (
            <div key={idx} className={`rounded-2xl border p-6 flex flex-col items-center justify-center gap-2 ${colorClasses}`}>
              <span className="text-[2rem] font-medium tracking-wide">{sw.from} <span className="text-zinc-600">→</span> {sw.to}</span>
              <span className="text-[2.2rem] font-bold tabular-nums">{sw.score} <span className="text-[1.2rem] opacity-50">BPM</span></span>
            </div>
          );
        })}
      </div>
    </div>
  );
}