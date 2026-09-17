import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css'; 

// Global Error Boundary: Catches unhandled React rendering exceptions down the component tree (implemented due to prior issues)
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, errorMsg: '', errorStack: '' };
  }

  // React lifecycle method triggered when a child component throws an error
  static getDerivedStateFromError(error) {
    return { hasError: true, errorMsg: error.toString(), errorStack: error.stack };
  }

  render() {
    // Fallback UI: Renders a high-contrast native HTML error log directly to the display 
    // for easier debugging without needing SSH access to the ThinkCentre
    if (this.state.hasError) {
      return (
        <div style={{ backgroundColor: '#09090b', color: '#ef4444', height: '100vh', padding: '40px', fontFamily: 'monospace' }}>
          <h1 style={{ fontSize: '3rem', marginBottom: '20px' }}>Dashboard Crash</h1>
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

// Mount the application tree wrapped in StrictMode for development checks and the ErrorBoundary for runtime safety
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
);