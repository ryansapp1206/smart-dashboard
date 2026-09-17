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
  const { time, weather, events, guitarData, autoView, apiLatency, requestCount } = useDashboardState();
  const currentView = guitarData?.current_view || 'calendar';

  const renderScreen = () => {
    if (currentView === 'help') return <HelpScreen />;
    if (currentView === 'hub') return <ChordHub switches={guitarData?.switches} />;
    if (currentView === 'all_chords') return <ChordLibrary chords={guitarData?.chords} />;
    
    // SAFETY CHECK: Only render SingleChord if the chord array explicitly exists in the database
    if (guitarData?.chords && guitarData.chords[currentView]) {
      return <SingleChord chordName={currentView} chordData={guitarData.chords[currentView]} />;
    }

    // Default auto-rotating calendar fallback
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
      <ConfirmationModal pendingUpdate={guitarData?.pending_update} />
      <ListeningIndicator isListening={guitarData?.is_listening} />
      <VisualMetronome bpm={guitarData?.metronome_bpm} currentView={currentView} timerActive={guitarData?.timer_active} />
      <PracticeTimer timerActive={guitarData?.timer_active} />
    </>
  );
}