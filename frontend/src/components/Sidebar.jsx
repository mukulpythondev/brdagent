import { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import {
  Upload, BarChart3, Archive, Settings, Sun, Moon, Flame,
  LayoutDashboard, FileText, ChevronLeft, ChevronRight, LogOut
} from 'lucide-react';

export default function Sidebar() {
  const { activePage, setActivePage, theme, setTheme, currentUser, handleLogout } = useApp();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [width, setWidth] = useState(260);
  const [isResizing, setIsResizing] = useState(false);

  const NAV_ITEMS = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'ingest', label: 'Upload & Ingest', icon: Upload },
    { id: 'editor', label: 'BRD Visualizer', icon: FileText },
    { id: 'analytics', label: 'Analytics Insights', icon: BarChart3 },
    { id: 'archive', label: 'Project Archive', icon: Archive },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  const startResizing = (e) => {
    e.preventDefault();
    setIsResizing(true);
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing) return;
      const newWidth = Math.max(180, Math.min(e.clientX, 400));
      setWidth(newWidth);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };

    if (isResizing) {
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing]);

  return (
    <aside
      className={`h-full bg-white dark:bg-[#111113] flex flex-col flex-shrink-0 relative z-30 ${isResizing ? '' : 'transition-[width] duration-300 ease-in-out'
        }`}
      style={{
        width: isCollapsed ? 80 : width,
        boxShadow: '1px 0 8px rgba(0,0,0,0.03)'
      }}
    >
      {/* Resizer Handle */}
      {!isCollapsed && (
        <div
          onMouseDown={startResizing}
          className="absolute top-0 right-[-6px] w-[12px] h-full cursor-col-resize z-40 group flex items-center justify-center"
        >
          <div className={`w-[2px] h-full transition-colors duration-200 ${isResizing ? 'bg-blue-500' : 'bg-transparent group-hover:bg-blue-500/50'
            }`} />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col gap-1 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <span className="w-1 h-1 rounded-full bg-blue-500/80" />
            <span className="w-1 h-1 rounded-full bg-blue-500/80" />
            <span className="w-1 h-1 rounded-full bg-blue-500/80" />
          </div>
        </div>
      )}

      {/* Sidebar Collapse Toggle */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute top-5 right-[-12px] w-6 h-6 rounded-full bg-white dark:bg-zinc-900 shadow-lg flex items-center justify-center text-zinc-500 hover:text-blue-600 dark:hover:text-blue-400 transition-all duration-200 cursor-pointer z-[60] hover:scale-110"
        style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
        title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
      >
        {isCollapsed ? <ChevronRight size={12} /> : <ChevronLeft size={12} />}
      </button>

      {/* Brand Header */}
      <div className={`h-16 flex items-center gap-2.5 transition-all duration-300 ${isCollapsed ? 'px-6 justify-center' : 'px-6'
        }`}>
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/15 flex-shrink-0">
          <Flame size={17} className="text-white" />
        </div>
        {!isCollapsed && (
          <div className="flex flex-col transition-opacity duration-300">
            <span className="font-extrabold text-sm tracking-tight text-zinc-900 dark:text-zinc-50">BRD Forge</span>
            <span className="text-[9px] font-semibold text-zinc-400 dark:text-zinc-500 tracking-wider">AI Requirements Engine</span>
          </div>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActivePage(item.id)}
              title={isCollapsed ? item.label : undefined}
              className={`w-full flex items-center gap-3 py-2.5 rounded-xl text-[13px] font-semibold transition-all duration-200 relative group cursor-pointer ${isCollapsed ? 'px-0 justify-center' : 'px-3.5'
                } ${isActive
                  ? 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-md shadow-blue-500/15'
                  : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800/40 hover:text-zinc-900 dark:hover:text-zinc-100'
                }`}
            >
              <Icon size={16} className={`flex-shrink-0 transition-transform duration-200 group-hover:scale-110 ${isActive ? 'text-white' : 'text-zinc-400 dark:text-zinc-500 group-hover:text-blue-500'}`} />
              {!isCollapsed && <span className="truncate">{item.label}</span>}
            </button>
          );
        })}
      </nav>

      {/* Sidebar Footer */}
      <div className={`p-4 space-y-3 transition-all duration-300 ${isCollapsed ? 'flex flex-col items-center p-3 gap-2' : ''
        }`}>
        {/* User profile mini */}
        {!isCollapsed && currentUser && (
          <div className="flex items-center gap-3 px-3 py-2.5 mb-2 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200/50 dark:border-zinc-800 rounded-xl shadow-sm">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center text-white text-[10px] font-bold flex-shrink-0">
              {currentUser.initials}
            </div>
            <div className="flex-1 min-w-0">
              <span className="block text-xs font-bold text-zinc-800 dark:text-zinc-200 truncate">{currentUser.name}</span>
              <span className="block text-[9px] text-zinc-400 dark:text-zinc-500 truncate">{currentUser.email}</span>
            </div>
            <button
              onClick={handleLogout}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/20 transition-all cursor-pointer border border-transparent hover:border-zinc-200/50 dark:hover:border-zinc-800"
              title="Logout"
            >
              <LogOut size={13} />
            </button>
          </div>
        )}

        {isCollapsed ? (
          <>
            <button
              onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
              className="w-10 h-10 rounded-xl bg-zinc-100 dark:bg-zinc-800 border border-zinc-200/60 dark:border-zinc-750/60 hover:bg-blue-50 dark:hover:bg-zinc-700 flex items-center justify-center text-zinc-500 dark:text-zinc-400 hover:text-blue-600 dark:hover:text-blue-400 transition-all duration-200 shadow-sm cursor-pointer"
              title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
            >
              {theme === 'light' ? <Moon size={15} /> : <Sun size={15} />}
            </button>
            {currentUser && (
              <button
                onClick={handleLogout}
                className="w-10 h-10 rounded-xl bg-zinc-100 dark:bg-zinc-800 border border-zinc-200/60 dark:border-zinc-750/60 hover:bg-rose-50 dark:hover:bg-rose-950/20 flex items-center justify-center text-zinc-400 hover:text-rose-500 transition-all cursor-pointer"
                title="Logout"
              >
                <LogOut size={14} />
              </button>
            )}
          </>
        ) : (
          <div className="flex items-center gap-2.5 w-full">
            <button
              onClick={() => setTheme('light')}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-[11px] font-bold transition-all duration-200 cursor-pointer ${theme === 'light'
                  ? 'bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 border border-blue-200/50 dark:border-blue-900/40 shadow-sm'
                  : 'bg-white dark:bg-zinc-900 text-zinc-650 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-850'
                }`}
            >
              <Sun size={13} />
              <span>Light</span>
            </button>
            <button
              onClick={() => setTheme('dark')}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-[11px] font-bold transition-all duration-200 cursor-pointer ${theme === 'dark'
                  ? 'bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 border border-blue-200/50 dark:border-blue-900/40 shadow-sm'
                  : 'bg-white dark:bg-zinc-900 text-zinc-650 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-850'
                }`}
            >
              <Moon size={13} />
              <span>Dark</span>
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}
