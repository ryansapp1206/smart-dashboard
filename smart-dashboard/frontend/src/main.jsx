import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css' // Adjust this if your main CSS file is App.css

// --- OUR CUSTOM ERROR CATCHER ---
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, errorMsg: '', errorStack: '' };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, errorMsg: error.toString(), errorStack: error.stack };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ backgroundColor: '#09090b', color: '#ef4444', height: '100vh', padding: '40px', fontFamily: 'monospace' }}>
          <h1 style={{ fontSize: '3rem', marginBottom: '20px' }}>⚠️ Dashboard Crash Detected</h1>
          <h2 style={{ fontSize: '2rem', color: '#f87171' }}>{this.state.errorMsg}</h2>
          <pre style={{ marginTop: '20px', color: '#a1a1aa', fontSize: '1.2rem', whiteSpace: 'pre-wrap' }}>
            {this.state.errorStack}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}
// --------------------------------

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
)