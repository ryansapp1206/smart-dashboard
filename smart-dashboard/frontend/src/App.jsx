import { useDashboardState } from './hooks/useDashboardState.js';
import ListeningIndicator from './components/ListeningIndicator.jsx';
import ConfirmationModal from './components/ConfirmationModal.jsx';
import VisualMetronome from './components/VisualMetronome.jsx';
import PracticeTimer from './components/PracticeTimer.jsx';

import HelpScreen from './views/HelpScreen.jsx';
import ChordHub from './views/ChordHub.jsx';
import ChordLibrary from './views/ChordLibrary.jsx';
import SingleChord from './views/SingleChord.jsx';
import CalendarWeek from './views/CalendarWeek.jsx';
import CalendarMonth from './views/CalendarMonth.jsx';

export default function App() {
  // Centralized state hub managing API polling and local data synchronization
  const { time, weather, events, guitarData, autoView, apiLatency, requestCount } = useDashboardState();
  const currentView = guitarData?.current_view || 'calendar';

  // Dynamic router handling view transitions based on voice bridge payloads
  const renderScreen = () => {
    if (currentView === 'help') return <HelpScreen />;
    if (currentView === 'hub') return <ChordHub switches={guitarData?.switches} />;
    if (currentView === 'all_chords') return <ChordLibrary chords={guitarData?.chords} />;
    
    // Render specific single chord view only if chord data is validated in the local database
    if (guitarData?.chords && guitarData.chords[currentView]) {
      return <SingleChord chordName={currentView} chordData={guitarData.chords[currentView]} />;
    }

    // Default idle state: Auto-rotating calendar driven by the useDashboardState timer
    if (autoView === 'week') {
      return (
        <CalendarWeek 
          time={time} 
          weather={weather} 
          events={events} 
          apiLatency={apiLatency} 
          requestCount={requestCount} 
        />
      );
    }
    
    return (
      <CalendarMonth 
        time={time} 
        weather={weather} 
        events={events} 
        apiLatency={apiLatency} 
        requestCount={requestCount} 
      />
    );
  };

  return (
    <>
      {renderScreen()}
      
      {/* Global UI Overlays: Render persistently across all active views */}
      <ConfirmationModal pendingUpdate={guitarData?.pending_update} />
      <ListeningIndicator isListening={guitarData?.is_listening} />
      <VisualMetronome bpm={guitarData?.metronome_bpm} currentView={currentView} timerActive={guitarData?.timer_active} />
      <PracticeTimer timerActive={guitarData?.timer_active} />
    </>
  );
}