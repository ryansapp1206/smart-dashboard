export default function SingleChord({ chordName, chordData }) {
  // Static arrays to generate the standard 6-string, 4-fret SVG guitar grid
  const fretArray = [1, 2, 3, 4];
  const stringArray = [0, 1, 2, 3, 4, 5];

  return (
    // Full-screen centered view
    <div key={chordName} className="fixed inset-0 box-border bg-zinc-950 py-12 px-32 flex flex-col items-center justify-center animate-fade-in overflow-hidden bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-zinc-900 to-zinc-950">
      
      <h1 className="text-[6rem] font-black text-zinc-100 mb-12 tracking-widest uppercase drop-shadow-md">
        {chordName}
      </h1>
      
      {/* Scaled-up SVG Chord Diagram*/}
      <svg className="h-[75vh] w-auto drop-shadow-2xl" viewBox="0 0 600 1000">
        
        {/* Guitar nut (Top heavy line) */}
        <line x1="50" y1="120" x2="550" y2="120" stroke="#e4e4e7" strokeWidth="16" strokeLinecap="round" />
        
        {/* Fret wires */}
        {fretArray.map(fret => (
          <line key={`fret-${fret}`} x1="50" y1={fret * 200 + 120} x2="550" y2={fret * 200 + 120} stroke="#3f3f46" strokeWidth="6" />
        ))}
        
        {/* Strings */}
        {stringArray.map((string, idx) => (
          <line key={`string-${string}`} x1={string * 100 + 50} y1="120" x2={string * 100 + 50} y2="920" stroke="#71717a" strokeWidth={6 - idx * 0.6} />
        ))}
        
        {/* Fingering Markers mapped from the chordData array */}
        {chordData.map((fretPos, stringIdx) => {
          const x = stringIdx * 100 + 50; 
          
          // NEEDS HEIGHT FOR STRING INDICATORS FIXED
          // TO-DO: REFACTTOR TO ENSURE CODE IS NOT DUPLICATED ACROSS CHORD LIBRARY AND SINGLE CHORD VIEWS
          // Muted string (Red X)
          if (fretPos === -1) return <text key={`mute-${stringIdx}`} x={x} y="70" fill="#f43f5e" fontSize="60" fontFamily="sans-serif" fontWeight="bold" textAnchor="middle">X</text>;
          
          // Open string (Blue hollow circle )
          if (fretPos === 0) return <circle key={`open-${stringIdx}`} cx={x} cy="60" r="20" fill="none" stroke="#3b82f6" strokeWidth="6" />;
          
          // Fretted note (Solid blue circle)
          if (fretPos > 0) return <circle key={`dot-${stringIdx}`} cx={x} cy={(fretPos - 1) * 200 + 220} r="35" fill="#3b82f6" />;
          
          return null;
        })}
      </svg>
    </div>
  );
}