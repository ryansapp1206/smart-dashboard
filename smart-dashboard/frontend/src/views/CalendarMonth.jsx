import DashboardHeader from '../components/DashboardHeader.jsx';

// Color-codes calendar events based on keyword matching.
// Explicitly highlights core coursework (Computer Science and Mathematics) with distinct gradients.
// TO-DO: ADD VOICE COMMANDS FOR ADJUSTING COLOR CORDINATION FOR FUTURE EVENTS AND CLASSES
const getEventStyle = (title) => {
  if (title.includes('CS')) return 'border-blue-500 bg-gradient-to-r from-blue-500/10 to-transparent text-blue-100';
  if (title.includes('MATH')) return 'border-rose-500 bg-gradient-to-r from-rose-500/10 to-transparent text-rose-100';
  return 'border-zinc-500 bg-gradient-to-r from-zinc-500/10 to-transparent text-zinc-300';
};

export default function CalendarMonth({ time, weather, events, apiLatency, requestCount }) {
  // Standard calendar math to determine grid structure
  const today = new Date();
  const daysInMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1).getDay();
  const calendarDays = Array.from({ length: daysInMonth }, (_, i) => i + 1);

  return (
    // Full-screen container with animate-fade-in for smooth transitions from other dashboard views
    <div key="calendar-month" className="fixed inset-0 box-border bg-zinc-950 text-zinc-100 py-10 pb-20 px-32 font-sans overflow-hidden flex flex-col animate-fade-in bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-zinc-900 via-zinc-950 to-zinc-950">
      
      {/* Inject the global dashboard header telemetry */}
      <DashboardHeader time={time} today={today} weather={weather} apiLatency={apiLatency} requestCount={requestCount} />

      <div className="flex-1 flex flex-col mt-4">
        <h3 className="text-[3.2rem] font-extrabold mb-8 text-zinc-400 tracking-[0.15em] uppercase shrink-0">This Month</h3>
        
        {/* 7-column CSS grid for the month layout */}
        <div className="grid grid-cols-7 gap-4 flex-1">
          
          {/* Day of the week headers */}
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => (
            <div key={d} className="text-center text-[2.4rem] text-zinc-500 font-bold tracking-widest uppercase mb-4">{d}</div>
          ))}
          
          {/* Invisible spacer blocks to push the 1st of the month to the correct day column */}
          {Array(firstDay).fill(null).map((_, i) => <div key={`empty-${i}`} className="bg-zinc-900/10 rounded-2xl border border-zinc-800/20" />)}
          
          {/* Render the actual calendar days */}
          {calendarDays.map(day => {
            const isToday = day === today.getDate();
            
            // Filter the global events array down to just the ones falling on this specific calendar cell
            const eventsThisDay = events.filter(e => e.start.getDate() === day && e.start.getMonth() === today.getMonth() && e.start.getFullYear() === today.getFullYear());
            
            const dayOfWeek = (firstDay + day - 1) % 7;
            const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
            
            // Dim weekends and heavily highlight the current day
            let cellClasses = 'bg-zinc-900/40 border-zinc-800/50';
            if (isWeekend) cellClasses = 'bg-zinc-950/40 border-zinc-900/50';
            if (isToday) cellClasses = 'bg-blue-900/10 border-blue-500/50 shadow-[0_0_30px_rgba(59,130,246,0.1)]';

            return (
              <div key={day} className={`h-full rounded-2xl border flex p-4 gap-4 items-start overflow-hidden transition-all ${cellClasses}`}>
                <span className={`text-[3.2rem] font-bold shrink-0 tracking-tighter leading-none mt-1 ${isToday ? 'text-blue-400' : isWeekend ? 'text-zinc-600' : 'text-zinc-400'}`}>
                  {day}
                </span>
                
                {/* Event Stack */}
                <div className="flex-1 flex flex-col gap-2 w-full overflow-hidden">
                  {eventsThisDay.map(e => (
                    <div key={e.id} className={`text-[1.8rem] font-medium border-l-[4px] px-3 py-1 h-[45px] rounded-r-md flex justify-between items-center gap-2 ${getEventStyle(e.title)}`}>
                      <span className="truncate">{e.title}</span>
                      <span className="text-[1.5rem] text-blue-400/80 shrink-0 font-medium tabular-nums">{e.time}</span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}