export default function ListeningIndicator({ isListening }) {
  // Hide the component entirely if the wake word hasn't been triggered
  if (!isListening) return null;
  
  // Renders a full-screen pulsing blue vignette overlay. 
  // pointer-events-none ensures the glowing border doesn't block underlying touch/mouse interactions on the dashboard.
  return (
    <div className="fixed inset-0 pointer-events-none z-50 animate-pulse shadow-[inset_0_0_80px_rgba(59,130,246,0.3)] bg-[radial-gradient(ellipse_at_center,_transparent_40%,_rgba(59,130,246,0.15)_80%,_rgba(59,130,246,0.5)_100%)]"></div>
  );
}