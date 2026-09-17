export default function ConfirmationModal({ pendingUpdate }) {
  // Conditionally render only when the Python voice bridge initiates a two-step action
  if (!pendingUpdate) return null;

  return (
    // Full-screen backdrop overlay. pointer-events-none prevents touch/mouse interaction in kiosk mode.
    <div className="fixed inset-0 bg-zinc-950/90 backdrop-blur-md flex items-center justify-center z-50 pointer-events-none">
      
      {/* Modal Container */}
      <div className="bg-zinc-900 border border-zinc-700 rounded-[2rem] p-16 text-center max-w-5xl shadow-[0_30px_100px_rgba(0,0,0,0.8),0_0_40px_rgba(59,130,246,0.2)]">
        <h2 className="text-[4rem] text-zinc-100 font-extrabold tracking-tight mb-8">Confirm Action</h2>
        
        {/* Inject the parsed variables directly from the voice payload */}
        <p className="text-[3.2rem] text-zinc-400 leading-tight">
          Update <span className="text-blue-400 font-black">{pendingUpdate.chord1}</span> to <span className="text-blue-400 font-black">{pendingUpdate.chord2}</span> <br/>
          New Score: <span className="text-white font-black">{pendingUpdate.score}</span> BPM
        </p>
        
        {/* Visual cues corresponding to the secondary Vosk listening loop in listener.py */}
        <div className="mt-16 flex justify-center gap-8 text-[2rem] font-bold tracking-wide">
          <span className="bg-green-500/10 text-green-400 px-12 py-6 rounded-xl border border-green-500/30">Say "Yes"</span>
          <span className="bg-red-500/10 text-red-400 px-12 py-6 rounded-xl border border-red-500/30">Say "No"</span>
        </div>
      </div>
    </div>
  );
}