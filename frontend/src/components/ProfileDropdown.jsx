import { useState, useRef, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { User, LogOut, ChevronDown } from 'lucide-react';

export default function ProfileDropdown() {
  const { currentUser, handleLogout, setActivePage } = useApp();
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const profileRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (profileRef.current && !profileRef.current.contains(e.target)) {
        setShowProfileMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!currentUser) return null;

  return (
    <div className="relative" ref={profileRef}>
      <button
        onClick={() => setShowProfileMenu(!showProfileMenu)}
        className="flex items-center gap-2 cursor-pointer group px-3 py-1.5 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200/60 dark:border-zinc-800 rounded-xl transition-all duration-200 shadow-sm active:scale-[0.98]"
      >
        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center text-white text-[10px] font-bold shadow-md shadow-blue-500/10 group-hover:shadow-blue-500/20 transition-shadow">
          {currentUser.initials}
        </div>
        <div className="hidden sm:flex flex-col text-left">
          <span className="text-[11px] font-bold text-zinc-700 dark:text-zinc-300 leading-none">{currentUser.name}</span>
          <span className="text-[9px] text-zinc-400 dark:text-zinc-500 mt-0.5 leading-none">{currentUser.role}</span>
        </div>
        <ChevronDown size={12} className="text-zinc-400 group-hover:text-zinc-600 dark:group-hover:text-zinc-300 transition-colors" />
      </button>

      {showProfileMenu && (
        <div className="absolute right-0 top-full mt-2 w-52 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-1.5 z-50 shadow-xl" style={{ boxShadow: '0 10px 32px rgba(0,0,0,0.1)' }}>
          <div className="px-3 py-2.5 mb-1 bg-zinc-50 dark:bg-zinc-800/55 rounded-lg">
            <span className="block text-xs font-bold text-zinc-900 dark:text-zinc-100 truncate">{currentUser.name}</span>
            <span className="block text-[9px] text-zinc-400 dark:text-zinc-500 truncate mt-0.5">{currentUser.email}</span>
          </div>
          <button
            onClick={() => { setActivePage('settings'); setShowProfileMenu(false); }}
            className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-semibold text-zinc-600 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors cursor-pointer"
          >
            <User size={13} />
            Profile Settings
          </button>
          <button
            onClick={() => { handleLogout(); setShowProfileMenu(false); }}
            className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-semibold text-zinc-600 dark:text-zinc-400 hover:bg-rose-50 dark:hover:bg-rose-950/20 hover:text-rose-600 dark:hover:text-rose-400 transition-colors cursor-pointer"
          >
            <LogOut size={13} />
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
}
