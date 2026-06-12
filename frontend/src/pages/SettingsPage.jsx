import { useApp } from '../context/AppContext';
import { Sliders, Key, CheckCircle2, History, User, Database } from 'lucide-react';
import ProfileDropdown from '../components/ProfileDropdown';

export default function SettingsPage() {
  const { settings, setSettings, versionHistory, addToast, currentUser } = useApp();

  const handleToggle = (key) => {
    setSettings(prev => ({ ...prev, [key]: !prev[key] }));
    addToast('Setting updated.', 'success');
  };

  const handleInputChange = (key, val) => {
    setSettings(prev => ({ ...prev, [key]: val }));
  };

  const formatDate = (isoStr) => {
    try {
      return new Date(isoStr).toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
      });
    } catch { return isoStr; }
  };

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-4 pb-8">
      {/* Floating Header */}
      <div className="sticky top-4 z-20 bg-white/90 dark:bg-zinc-900/90 backdrop-blur-xl rounded-2xl border border-zinc-200/80 dark:border-zinc-800/80 shadow-md px-6 py-3.5 flex flex-col md:flex-row md:items-center md:justify-between gap-4 transition-all duration-200">
        <div>
          <h2 className="text-lg font-extrabold tracking-tight text-zinc-900 dark:text-zinc-50">Settings</h2>
          <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-0.5 font-medium">System configuration and audit logs</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[10px] font-bold bg-emerald-50 dark:bg-emerald-950/25 text-emerald-600 dark:text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span>Sync Active</span>
          </div>
          <div className="h-6 w-px bg-zinc-200 dark:bg-zinc-800" />
          <ProfileDropdown />
        </div>
      </div>

      <div className="h-12" />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Left Column */}
        <div className="md:col-span-2 space-y-6">
          
          <div className="premium-card p-6">
            <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-50 flex items-center gap-2 mb-6">
              <Database size={16} className="text-blue-500" />
              AI Engine Status
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-[10px] font-semibold text-zinc-500 uppercase tracking-wide mb-1.5">Active LLM</label>
                <div className="text-sm font-medium text-zinc-800 dark:text-zinc-200 bg-zinc-50/80 dark:bg-zinc-800/30 p-3 rounded-xl">
                  Gemini 1.5 Pro (gemini-1.5-pro-latest)
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-semibold text-zinc-500 uppercase tracking-wide mb-1.5">OCR Parser</label>
                  <div className="text-sm font-medium text-zinc-800 dark:text-zinc-200 bg-zinc-50/80 dark:bg-zinc-800/30 p-3 rounded-xl">
                    Gemini Vision API
                  </div>
                </div>
                <div>
                  <label className="block text-[10px] font-semibold text-zinc-500 uppercase tracking-wide mb-1.5">Database</label>
                  <div className="text-sm font-medium text-zinc-800 dark:text-zinc-200 bg-zinc-50/80 dark:bg-zinc-800/30 p-3 rounded-xl">
                    Local Sandbox Store
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-semibold text-zinc-500 uppercase tracking-wide mb-1.5">PDF Theme</label>
                <select
                  value={settings.defaultExportTheme}
                  onChange={(e) => handleInputChange('defaultExportTheme', e.target.value)}
                  className="w-full text-sm bg-zinc-50/80 dark:bg-zinc-800/30 rounded-xl py-2.5 px-3.5 text-zinc-800 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                >
                  <option value="Corporate Blue">Corporate Blue</option>
                  <option value="Emerald Clean">Emerald Clean</option>
                  <option value="Warm Crimson">Warm Crimson</option>
                  <option value="Slate Minimalist">Slate Minimalist</option>
                </select>
              </div>
            </div>
          </div>

          <div className="premium-card p-6">
            <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-50 flex items-center gap-2 mb-6">
              <Sliders size={16} className="text-blue-500" />
              Automation Rules
            </h3>

            <div className="space-y-1">
              <div className="flex items-center justify-between py-3 px-3 rounded-xl hover:bg-zinc-50/50 dark:hover:bg-zinc-800/20 transition-colors -mx-3">
                <div>
                  <span className="text-sm font-medium text-zinc-800 dark:text-zinc-200 block">Auto Domain Detection</span>
                  <span className="text-xs text-zinc-500 dark:text-zinc-400">Automatically classify requirements by industry.</span>
                </div>
                <button
                  onClick={() => handleToggle('autoDetectDomain')}
                  className={`w-11 h-6 rounded-full p-0.5 transition-all duration-200 cursor-pointer ${
                    settings.autoDetectDomain ? 'bg-blue-500 flex justify-end' : 'bg-zinc-200 dark:bg-zinc-700 flex justify-start'
                  }`}
                >
                  <span className="w-5 h-5 bg-white rounded-full shadow-md block" />
                </button>
              </div>

              <div className="flex items-center justify-between py-3 px-3 rounded-xl hover:bg-zinc-50/50 dark:hover:bg-zinc-800/20 transition-colors -mx-3">
                <div>
                  <span className="text-sm font-medium text-zinc-800 dark:text-zinc-200 block">Visual Conflict Linkers</span>
                  <span className="text-xs text-zinc-500 dark:text-zinc-400">Draw connecting lines between conflicting specs.</span>
                </div>
                <button
                  onClick={() => handleToggle('showVisualConnectors')}
                  className={`w-11 h-6 rounded-full p-0.5 transition-all duration-200 cursor-pointer ${
                    settings.showVisualConnectors ? 'bg-blue-500 flex justify-end' : 'bg-zinc-200 dark:bg-zinc-700 flex justify-start'
                  }`}
                >
                  <span className="w-5 h-5 bg-white rounded-full shadow-md block" />
                </button>
              </div>
            </div>
          </div>

        </div>

        {/* Right Column */}
        <div className="space-y-6">
          
          {/* Profile Card */}
          <div className="premium-card p-5 text-center">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center text-white font-bold mx-auto mb-3 text-lg shadow-lg shadow-blue-500/15">
              {currentUser?.initials || 'JD'}
            </div>
            <span className="block text-sm font-bold text-zinc-900 dark:text-zinc-100">{currentUser?.name || 'John Doe'}</span>
            <span className="text-[10px] font-semibold text-blue-500">{currentUser?.role || 'Workspace Architect'}</span>
            
            <div className="mt-4 pt-4 grid grid-cols-2 gap-2 text-center" style={{ borderTop: '1px solid rgba(148,163,184,0.1)' }}>
              <div>
                <span className="block text-lg font-extrabold text-zinc-900 dark:text-zinc-100">12</span>
                <span className="text-[9px] text-zinc-500 uppercase tracking-wide">Projects</span>
              </div>
              <div>
                <span className="block text-lg font-extrabold text-zinc-900 dark:text-zinc-100">84%</span>
                <span className="text-[9px] text-zinc-500 uppercase tracking-wide">Avg Quality</span>
              </div>
            </div>
          </div>

          {/* Audit Timeline */}
          <div className="premium-card p-5">
            <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-50 flex items-center gap-2 mb-4">
              <History size={13} className="text-blue-500" />
              Audit History
            </h3>
            
            <div className="flow-root">
              <ul className="-mb-8">
                {versionHistory.map((log, logIdx) => (
                  <li key={log.id}>
                    <div className="relative pb-6">
                      {logIdx !== versionHistory.length - 1 ? (
                        <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-zinc-100 dark:bg-zinc-800" aria-hidden="true" />
                      ) : null}
                      <div className="relative flex space-x-3">
                        <div>
                          <span className="h-8 w-8 rounded-full bg-blue-50 dark:bg-blue-950/30 text-blue-500 flex items-center justify-center">
                            <CheckCircle2 size={13} />
                          </span>
                        </div>
                        <div className="flex-1 min-w-0 pt-1.5">
                          <p className="text-xs font-bold text-zinc-800 dark:text-zinc-200">
                            {log.action}
                          </p>
                          <p className="text-[10px] text-zinc-500 dark:text-zinc-400 mt-0.5">
                            {log.details}
                          </p>
                          <div className="text-[9px] text-zinc-400 mt-1 flex items-center gap-1.5 justify-between">
                            <span>By {log.user}</span>
                            <span>{formatDate(log.timestamp)}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
