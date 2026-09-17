export default function ListeningIndicator({ isListening }) {
  if (!isListening) return null;
  return (
    <div className="fixed inset-0 pointer-events-none z-50 animate-pulse shadow-[inset_0_0_80px_rgba(59,130,246,0.3)] bg-[radial-gradient(ellipse_at_center,_transparent_40%,_rgba(59,130,246,0.15)_80%,_rgba(59,130,246,0.5)_100%)]"></div>
  );
}