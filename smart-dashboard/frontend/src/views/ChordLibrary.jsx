export default function ChordLibrary({ chords }) {
  const fretArray = [1, 2, 3, 4];
  const stringArray = [0, 1, 2, 3, 4, 5];

  if (!chords) return null;

  return (
    <div key="all_chords" className="fixed inset-0 box-border bg-zinc-950 py-12 px-32 flex flex-col items-center animate-fade-in overflow-hidden">
      <h1 className="text-[3.5rem] font-bold text-zinc-500 mb-12 tracking-[0.2em] uppercase shrink-0">Chord Library</h1>
      
      <div className="w-full flex-1 grid grid-cols-4 gap-8 min-h-0 pb-8">
        {Object.entries(chords).map(([chordName, chordArr]) => (
          <div key={chordName} className="bg-zinc-900/30 rounded-[2rem] border border-zinc-800 p-8 flex flex-col items-center h-full min-h-0">
            <h2 className="text-[3rem] font-bold text-zinc-100 mb-6 shrink-0">{chordName}</h2>
            <svg className="h-full w-auto drop-shadow-lg" viewBox="0 0 600 1000">
              <line x1="50" y1="120" x2="550" y2="120" stroke="#e4e4e7" strokeWidth="16" strokeLinecap="round" />
              {fretArray.map(fret => (
                <line key={`fret-${fret}`} x1="50" y1={fret * 200 + 120} x2="550" y2={fret * 200 + 120} stroke="#3f3f46" strokeWidth="6" />
              ))}
              {stringArray.map((string, idx) => (
                <line key={`string-${string}`} x1={string * 100 + 50} y1="120" x2={string * 100 + 50} y2="920" stroke="#71717a" strokeWidth={6 - idx * 0.6} />
              ))}
              {chordArr.map((fretPos, stringIdx) => {
                const x = stringIdx * 100 + 50; 
                if (fretPos === -1) return <text key={`mute-${stringIdx}`} x={x} y="70" fill="#f43f5e" fontSize="60" fontFamily="sans-serif" fontWeight="bold" textAnchor="middle">X</text>;
                if (fretPos === 0) return <circle key={`open-${stringIdx}`} cx={x} cy="60" r="20" fill="none" stroke="#3b82f6" strokeWidth="6" />;
                if (fretPos > 0) return <circle key={`dot-${stringIdx}`} cx={x} cy={(fretPos - 1) * 200 + 220} r="35" fill="#3b82f6" />;
                return null;
              })}
            </svg>
          </div>
        ))}
      </div>
    </div>
  );
}