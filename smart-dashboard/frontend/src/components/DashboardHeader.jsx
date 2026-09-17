export default function DashboardHeader({ time, today, apiLatency, requestCount, weather }) {
  return (
    <div className="flex justify-between items-start shrink-0 mb-10 w-full">
      <div className="flex flex-col shrink-0">
        <h2 className="text-[3rem] text-zinc-400 font-medium tracking-[0.1em] mb-2 uppercase">
          {today.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
        </h2>
        <h1 className="text-[12rem] font-extrabold tracking-tighter leading-none text-zinc-50 drop-shadow-sm">
          {time.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}
        </h1>
      </div>

      <div className="flex-1 flex justify-center items-start pt-12">
        <div className="flex items-center gap-8 font-mono text-[1.8rem] text-zinc-500 bg-zinc-900/40 border border-zinc-800/80 px-10 py-8 rounded-full backdrop-blur-sm">
          <span className="flex items-center gap-4">
            <div className={`w-4 h-4 rounded-full shadow-[0_0_12px_currentColor] ${apiLatency === 'ERR' ? 'bg-red-500 text-red-500' : 'bg-emerald-500 text-emerald-500 animate-pulse'}`}></div> 
            {import.meta.env.VITE_DISPLAY_IP}
          </span>
          <span className="text-zinc-700">|</span>
          <span className="w-[160px] tabular-nums whitespace-nowrap">
            PING: <span className={apiLatency > 100 ? 'text-amber-400' : 'text-zinc-300'}>{apiLatency}</span>ms
          </span>
          <span className="text-zinc-700">|</span>
          <span className="w-[170px] tabular-nums whitespace-nowrap">
            REQ: <span className="text-zinc-300">{requestCount.toLocaleString()}</span>
          </span>
          <span className="text-zinc-700">|</span>
          <span className="text-zinc-400">VOSK: STABLE</span>
        </div>
      </div>

      <div className="flex items-center gap-8 shrink-0 mt-8">
        {weather && (
          <>
            {/* Note: In a future pass, extract these SVGs into a <WeatherIcon code={weather.weathercode} /> component */}
            {weather.weathercode === 0 && (
              <svg className="w-50 h-50 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
            )}
            {((weather.weathercode > 0 && weather.weathercode <= 3) || weather.weathercode === 45 || weather.weathercode === 48) && (
              <svg className="w-50 h-50 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"></path></svg>
            )}
            {((weather.weathercode >= 71 && weather.weathercode <= 77) || weather.weathercode === 85 || weather.weathercode === 86) && (
              <svg className="w-50 h-50 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><line x1="2" y1="12" x2="22" y2="12"></line><line x1="12" y1="2" x2="12" y2="22"></line><line x1="20" y1="4" x2="4" y2="20"></line><line x1="4" y1="4" x2="20" y2="20"></line><circle cx="12" cy="12" r="2"></circle></svg>
            )}
            {((weather.weathercode >= 51 && weather.weathercode <= 67) || (weather.weathercode >= 80 && weather.weathercode <= 82) || (weather.weathercode >= 95 && weather.weathercode <= 99)) && (
              <svg className="w-50 h-50 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"></path><path d="M16 20l-2-2"></path><path d="M12 22l-2-2"></path><path d="M8 22l-2-2"></path></svg>
            )}
            <span className="text-[9rem] font-bold leading-none tracking-tighter text-zinc-100">{Math.round(weather.temperature)}°</span>
            <div className="flex flex-col justify-center border-l-2 border-zinc-700 pl-8 ml-2">
              <span className="text-[2.2rem] font-medium text-zinc-400 tracking-wide uppercase">Local</span>
              <span className="text-[2.8rem] font-bold text-zinc-200 leading-none">{import.meta.env.VITE_LOCATION_NAME}</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}