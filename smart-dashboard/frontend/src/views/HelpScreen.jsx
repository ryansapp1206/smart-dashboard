export default function HelpScreen() {
  // Static reference screen mapping out available voice commands for the user
  return (
    // Full-screen overlay with a subtle radial gradient background
    <div key="help" className="fixed inset-0 box-border overflow-hidden bg-zinc-950 px-32 py-12 flex flex-col items-center justify-center animate-fade-in bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-zinc-900 via-zinc-950 to-zinc-950">
      
      <h1 className="text-[4rem] font-bold text-zinc-100 mb-12 tracking-widest uppercase flex items-center gap-6">
        {/* Pulsing blue dot mimics the global listening indicator for visual consistency */}
        <div className="w-6 h-6 bg-blue-500 rounded-full animate-pulse shadow-[0_0_20px_#3b82f6]"></div>
        System Commands
      </h1>
      
      {/* 3-column grid for standard command categories */}
      <div className="grid grid-cols-3 gap-8 w-full max-w-[1600px]">
        
        {/* Navigation Commands */}
        <div className="bg-zinc-900/50 rounded-2xl p-8 border border-zinc-800">
          <h2 className="text-[2rem] text-blue-400 font-semibold mb-4 tracking-wide uppercase">Navigation</h2>
          <p className="text-[2rem] text-zinc-400"><span className="text-zinc-100 font-medium">"Home"</span> or <span className="text-zinc-100 font-medium">"Calendar"</span></p>
          <p className="text-[2rem] text-zinc-400 mt-2"><span className="text-zinc-100 font-medium">"Help"</span> or <span className="text-zinc-100 font-medium">"Commands"</span></p>
        </div>

        {/* Library / View Commands */}
        <div className="bg-zinc-900/50 rounded-2xl p-8 border border-zinc-800">
          <h2 className="text-[2rem] text-emerald-400 font-semibold mb-4 tracking-wide uppercase">Library</h2>
          <p className="text-[2rem] text-zinc-400"><span className="text-zinc-100 font-medium">"Open Hub"</span> or <span className="text-zinc-100 font-medium">"Scores"</span></p>
          <p className="text-[2rem] text-zinc-400 mt-2"><span className="text-zinc-100 font-medium">"Show all chords"</span></p>
        </div>

        {/* Metronome / Timer Commands */}
        <div className="bg-zinc-900/50 rounded-2xl p-8 border border-zinc-800">
          <h2 className="text-[2rem] text-orange-400 font-semibold mb-4 tracking-wide uppercase">Metronome</h2>
          <p className="text-[2rem] text-zinc-400"><span className="text-zinc-100 font-medium">"Set metronome to 60"</span></p>
          <p className="text-[2rem] text-zinc-400 mt-2"><span className="text-zinc-100 font-medium">"Stop metronome"</span></p>
        </div>

        {/* Full-width block (col-span-3) for the complex 2-step database update syntax */}
        <div className="bg-zinc-900/50 rounded-2xl p-10 border border-zinc-800 col-span-3 text-center">
          <h2 className="text-[2rem] text-blue-400 font-semibold mb-4 tracking-wide uppercase">Database Update</h2>
          <p className="text-[2.5rem] text-zinc-400 font-light">
            <span className="text-zinc-100 font-medium">"Update</span> [Chord] <span className="text-zinc-100 font-medium">to</span> [Chord] <span className="text-zinc-100 font-medium">to</span> [Score]<span className="text-zinc-100 font-medium">"</span>
          </p>
          <p className="text-[1.8rem] text-zinc-600 mt-4 italic">Example: "Update A to D minor to 68"</p>
        </div>
      </div>
    </div>
  );
}