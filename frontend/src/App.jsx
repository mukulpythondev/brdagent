import { AppProvider, useApp } from './context/AppContext';
import Sidebar from './components/Sidebar';
import ToastContainer from './components/ToastContainer';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import VisualizerPage from './pages/VisualizerPage';
import ArchivePage from './pages/ArchivePage';
import SettingsPage from './pages/SettingsPage';
import LoginPage from './pages/LoginPage';

import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 premium-card m-6">
          <h2 className="text-base font-extrabold text-rose-600 dark:text-rose-400 uppercase tracking-wider">Runtime Error</h2>
          <p className="text-xs text-rose-500 mt-2 font-semibold font-mono">{this.state.error?.toString()}</p>
          <pre className="text-[10px] text-rose-400 mt-4 overflow-auto max-h-60 bg-zinc-50 dark:bg-zinc-950 p-4 rounded-lg font-mono">
            {this.state.error?.stack}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}

function AppContent() {
  const { activePage, isLoggedIn } = useApp();

  // Show login page if not authenticated
  if (!isLoggedIn) {
    return (
      <>
        <LoginPage />
        <ToastContainer />
      </>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-[#f4f6fb] dark:bg-[#09090b] font-sans transition-colors duration-300 relative grid-bg">
      {/* Decorative ambient background glows */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-blue-500/4 dark:bg-blue-500/8 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-500/4 dark:bg-cyan-500/8 blur-[100px] pointer-events-none" />
      
      {/* Side-bar Navigation */}
      <Sidebar />
      
      {/* Main Workspace Frame */}
      <main className={`flex-1 h-full relative z-10 ${['editor', 'analytics'].includes(activePage) ? 'overflow-hidden' : 'overflow-y-auto'}`}>
        {activePage === 'dashboard' && <DashboardPage />}
        {activePage === 'ingest' && <UploadPage />}
        {activePage === 'editor' && (
          <ErrorBoundary>
            <VisualizerPage showAnalytics={false} />
          </ErrorBoundary>
        )}
        {activePage === 'analytics' && (
          <ErrorBoundary>
            <VisualizerPage showAnalytics={true} />
          </ErrorBoundary>
        )}
        {activePage === 'archive' && <ArchivePage />}
        {activePage === 'settings' && <SettingsPage />}
      </main>
      
      {/* Global notifications container */}
      <ToastContainer />
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}
