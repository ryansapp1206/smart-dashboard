import DashboardHeader from '../components/DashboardHeader.jsx';

const getEventStyle = (title) => {
  if (title.includes('CS')) return 'border-blue-500 bg-gradient-to-r from-blue-500/10 to-transparent text-blue-100';
  if (title.includes('MATH')) return 'border-rose-500 bg-gradient-to-r from-rose-500/10 to-transparent text-rose-100';
  return 'border-zinc-500 bg-gradient-to-r from-zinc-500/10 to-transparent text-zinc-300';
};

export default function CalendarWeek({ time, weather, events, apiLatency, requestCount }) {
  const today = new Date();
  const upcoming7Days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(today);
    d.setDate(today.getDate() + i);
    return d;
  });

  return (
    <div key="calendar-week" className="fixed inset-0 box-border bg-zinc-950 text-zinc-100 py-10 px-32 font-sans overflow-hidden flex flex-col animate-fade-in bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-zinc-900 via-zinc-950 to-zinc-950">
      <DashboardHeader time={time} today={today} weather={weather} apiLatency={apiLatency} requestCount={requestCount} />
      
      <div className="flex-1 flex gap-16 w-full mt-4">
        <div className="w-1/2 flex flex-col">
          <h3 className="text-[3.2rem] font-extrabold mb-8 text-zinc-400 tracking-[0.15em] uppercase shrink-0">Upcoming Schedule</h3>
          <div className="flex-1 flex flex-col gap-4">
            {upcoming7Days.map(d => {
              const isToday = d.getDate() === today.getDate() && d.getMonth() === today.getMonth();
              const eventsThisDay = events.filter(e => e.start.getDate() === d.getDate() && e.start.getMonth() === d.getMonth() && e.start.getFullYear() === d.getFullYear());
              
              return (
                <div key={d.toISOString()} className={`flex-1 rounded-2xl flex items-center p-6 gap-8 transition-colors ${isToday ? 'bg-blue-900/10 border border-blue-500/30' : 'bg-zinc-900/40 border border-zinc-800/50'}`}>
                  <div className="flex flex-col items-center justify-center min-w-[100px]">
                    <span className={`text-[1.6rem] uppercase font-bold tracking-widest ${isToday ? 'text-blue-400' : 'text-zinc-500'}`}>{d.toLocaleDateString('en-US', { weekday: 'short' })}</span>
                    <span className={`text-[4rem] font-black tracking-tighter leading-none ${isToday ? 'text-blue-100' : 'text-zinc-300'}`}>{d.getDate()}</span>
                  </div>
                  
                  <div className="flex-1 flex flex-col gap-3 overflow-hidden border-l border-zinc-700/50 pl-8">
                    {eventsThisDay.length > 0 ? eventsThisDay.map(e => (
                      <div key={e.id} className={`text-[1.8rem] font-medium border-l-[4px] px-4 py-2 rounded-r-md flex justify-between items-center ${getEventStyle(e.title)}`}>
                        <span className="truncate">{e.title}</span>
                        <span className="text-[1.5rem] text-blue-400/80 shrink-0">{e.time}</span>
                      </div>
                    )) : <span className="text-zinc-600/80 text-[1.8rem] italic font-light">No events scheduled</span>}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        <div className="w-1/2 rounded-[2rem] border border-zinc-800/30 bg-gradient-to-br from-zinc-900/20 to-transparent"></div>
      </div>
    </div>
  );
}