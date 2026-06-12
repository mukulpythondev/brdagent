import { useState, useRef, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { LayoutDashboard, FileText, Settings, Sun, Moon, Zap, Flame, Sparkles, User, LogOut, ChevronDown } from 'lucide-react';

export default function Header() {
  const { activePage, setActivePage, theme, setTheme, currentUser, handleLogout } = useApp();
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const profileRef = useRef(null);

  const NAV_ITEMS = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'ingest', label: 'Upload & Ingest', icon: Sparkles },
    { id: 'editor', label: 'BRD Visualizer', icon: FileText },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  // Close profile menu on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (profileRef.current && !profileRef.current.contains(e.target)) {
        setShowProfileMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full backdrop-blur-xl bg-white/80 dark:bg-zinc-950/80 transition-colors duration-200" style={{ boxShadow: '0 1px 6px rgba(0,0,0,0.03)' }}>
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => setActivePage('dashboard')}>
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/15">
            <Flame size={18} className="text-white" />
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold text-sm tracking-tight text-zinc-900 dark:text-zinc-50">BRD Forge</span>
            <span className="text-[9px] font-semibold text-zinc-400 dark:text-zinc-500 tracking-wider">AI Requirements Engine</span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id || (item.id === 'editor' && activePage === 'analytics');
            return (
              <button
                key={item.id}
                onClick={() => setActivePage(item.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold tracking-wide transition-all duration-200 cursor-pointer ${
                  isActive
                    ? 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-md shadow-blue-500/15'
                    : 'text-zinc-500 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 hover:text-zinc-900 dark:hover:text-zinc-100'
                }`}
              >
                <Icon size={14} />
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          {/* Status Badge */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-emerald-50 dark:bg-emerald-950/25 text-emerald-600 dark:text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <Zap size={10} className="text-emerald-500" />
            <span>AI Live</span>
          </div>

          {/* Theme Switcher */}
          <div className="flex items-center bg-zinc-50 dark:bg-zinc-800/60 p-0.5 rounded-lg">
            <button
              onClick={() => setTheme('light')}
              className={`p-1.5 rounded-md transition-all duration-200 cursor-pointer ${
                theme === 'light'
                  ? 'bg-white text-amber-600 shadow-sm'
                  : 'text-zinc-500 hover:text-zinc-700 dark:text-zinc-400 dark:hover:text-zinc-200 hover:bg-zinc-100 dark:hover:bg-zinc-700/50'
              }`}
              title="Light Mode"
            >
              <Sun size={13} />
            </button>
            <button
              onClick={() => setTheme('dark')}
              className={`p-1.5 rounded-md transition-all duration-200 cursor-pointer ${
                theme === 'dark'
                  ? 'bg-zinc-900 text-blue-400 shadow-sm'
                  : 'text-zinc-500 hover:text-zinc-700 dark:text-zinc-400 dark:hover:text-zinc-200 hover:bg-zinc-100 dark:hover:bg-zinc-700/50'
              }`}
              title="Dark Mode"
            >
              <Moon size={13} />
            </button>
          </div>

          {/* Profile Avatar */}
          {currentUser && (
            <div className="relative" ref={profileRef}>
              <button
                onClick={() => setShowProfileMenu(!showProfileMenu)}
                className="flex items-center gap-2 cursor-pointer group"
              >
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center text-white text-[10px] font-bold shadow-md shadow-blue-500/10 group-hover:shadow-blue-500/20 transition-shadow">
                  {currentUser.initials}
                </div>
                <ChevronDown size={12} className="text-zinc-400 group-hover:text-zinc-600 dark:group-hover:text-zinc-300 transition-colors" />
              </button>

              {/* Profile Dropdown */}
              {showProfileMenu && (
                <div className="absolute right-0 top-full mt-2 w-56 premium-card p-2 z-50" style={{ boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }}>
                  <div className="px-3 py-2.5 mb-1">
                    <span className="block text-xs font-bold text-zinc-900 dark:text-zinc-100">{currentUser.name}</span>
                    <span className="block text-[10px] text-zinc-400 dark:text-zinc-500">{currentUser.email}</span>
                    <span className="inline-block mt-1.5 text-[9px] font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/30 px-2 py-0.5 rounded-full uppercase tracking-wider">{currentUser.role}</span>
                  </div>
                  <div className="h-px bg-zinc-100 dark:bg-zinc-800 my-1" />
                  <button
                    onClick={() => { setActivePage('settings'); setShowProfileMenu(false); }}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium text-zinc-600 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors cursor-pointer"
                  >
                    <User size={13} />
                    Profile Settings
                  </button>
                  <button
                    onClick={() => { handleLogout(); setShowProfileMenu(false); }}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium text-zinc-600 dark:text-zinc-400 hover:bg-rose-50 dark:hover:bg-rose-950/20 hover:text-rose-600 dark:hover:text-rose-400 transition-colors cursor-pointer"
                  >
                    <LogOut size={13} />
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

      </div>
    </header>
  );
}
