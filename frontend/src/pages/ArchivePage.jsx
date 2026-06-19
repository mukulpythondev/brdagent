import { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Search, PlusCircle, Trash2, ArrowRight, FolderKanban, Calendar, AlertOctagon, TrendingUp, Layers } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ProfileDropdown from '../components/ProfileDropdown';

export default function ArchivePage() {
  const { projects, handleSelectProject, handleDeleteProject, handleLoadDemo, setActivePage } = useApp();
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = projects.filter(p =>
    !searchQuery.trim() || p.project_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatDate = (isoStr) => {
    try {
      return new Date(isoStr).toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric'
      });
    } catch { return isoStr; }
  };

  const getDomainColor = (domain) => {
    switch (domain?.toLowerCase()) {
      case 'fintech':
        return 'bg-blue-50 text-blue-600 dark:bg-blue-950/30 dark:text-blue-400';
      case 'healthtech':
        return 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/30 dark:text-emerald-400';
      case 'e-commerce':
        return 'bg-purple-50 text-purple-600 dark:bg-purple-950/30 dark:text-purple-400';
      default:
        return 'bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400';
    }
  };

  const totalProjects = projects.length;
  const activeConflicts = projects.reduce((acc, p) => acc + p.conflict_count, 0);
  const avgConfidence = totalProjects > 0 ? Math.round(projects.reduce((acc, p) => acc + p.confidence_score, 0) / totalProjects) : 0;

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-4 pb-8">
      
      {/* Floating Header */}
      <div className="sticky top-4 z-20 bg-white/90 dark:bg-zinc-900/90 backdrop-blur-xl rounded-2xl border border-zinc-200/80 dark:border-zinc-800/80 shadow-md px-6 py-3.5 flex flex-col md:flex-row md:items-center md:justify-between gap-4 transition-all duration-200">
        <div>
          <h2 className="text-lg font-extrabold tracking-tight text-zinc-900 dark:text-zinc-50">Project Archive</h2>
          <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-0.5 font-medium">Manage and load previously generated specifications</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex gap-2">
            <button
              onClick={handleLoadDemo}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-white dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-800 hover:text-zinc-900 dark:hover:text-zinc-100 shadow-sm active:scale-[0.98] rounded-xl text-xs font-semibold transition-all cursor-pointer"
            >
              Load Demo
            </button>
            <button
              onClick={() => setActivePage('ingest')}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white rounded-xl text-xs font-semibold transition-all shadow-lg shadow-blue-500/15 cursor-pointer active:scale-[0.98]"
            >
              <PlusCircle size={13} />
              Upload & Ingest
            </button>
          </div>
          <div className="h-6 w-px bg-zinc-200 dark:bg-zinc-800 hidden sm:block" />
          <ProfileDropdown />
        </div>
      </div>

      <div className="h-12" />

      {/* Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mb-8">
        <div className="premium-card p-5 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-semibold text-zinc-500 dark:text-zinc-400 tracking-wide uppercase">Projects</span>
            <span className="block text-2xl font-extrabold text-zinc-900 dark:text-zinc-50 mt-1">{totalProjects}</span>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-950/30 text-blue-500 flex items-center justify-center">
            <FolderKanban size={18} />
          </div>
        </div>

        <div className="premium-card p-5 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-semibold text-zinc-500 dark:text-zinc-400 tracking-wide uppercase">Contradictions</span>
            <span className="block text-2xl font-extrabold text-zinc-900 dark:text-zinc-50 mt-1">{activeConflicts}</span>
          </div>
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${activeConflicts > 0 ? 'bg-rose-50 dark:bg-rose-950/30 text-rose-500' : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-400'}`}>
            <AlertOctagon size={18} />
          </div>
        </div>

        <div className="premium-card p-5 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-semibold text-zinc-500 dark:text-zinc-400 tracking-wide uppercase">Avg Quality</span>
            <span className="block text-2xl font-extrabold text-blue-600 dark:text-blue-400 mt-1">{avgConfidence}%</span>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 text-emerald-500 flex items-center justify-center">
            <TrendingUp size={18} />
          </div>
        </div>
      </div>

      {/* Search and Filters Bar */}
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-4 mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 shadow-sm">
        <div className="relative w-full max-w-md">
          <Search size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-400" />
          <input
            type="text"
            placeholder="Search archived projects by name or domain..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full text-xs bg-zinc-50/50 dark:bg-zinc-950/40 border border-zinc-200 dark:border-zinc-800/80 rounded-xl py-2.5 pl-10 pr-4 text-zinc-850 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-blue-500/20 placeholder-zinc-400 font-medium transition-all shadow-inner"
          />
        </div>
        <span className="text-[11px] font-bold text-zinc-500 bg-zinc-50 dark:bg-zinc-850/50 px-3 py-1.5 rounded-xl border border-zinc-200 dark:border-zinc-800/80 flex-shrink-0 self-start sm:self-auto">
          {filtered.length} {filtered.length === 1 ? 'project' : 'projects'} found
        </span>
      </div>

      {/* Projects Listing */}
      <div>
        {projects.length === 0 ? (
          <div className="premium-card text-center py-16">
            <FolderKanban size={32} className="mx-auto text-zinc-300 dark:text-zinc-700 mb-3" />
            <h3 className="text-sm font-bold text-zinc-700 dark:text-zinc-300">No projects yet</h3>
            <p className="text-xs text-zinc-500 max-w-xs mx-auto mt-1">Generate your first BRD to get started.</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="premium-card text-center py-16">
            <Search size={32} className="mx-auto text-zinc-300 dark:text-zinc-700 mb-3" />
            <h3 className="text-sm font-bold text-zinc-700 dark:text-zinc-300">No results</h3>
            <p className="text-xs text-zinc-500 max-w-xs mx-auto mt-1">No match for "{searchQuery}".</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <AnimatePresence mode="popLayout">
              {filtered.map((proj) => (
                <motion.div
                  key={proj.id}
                  layout
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="premium-card p-6 flex flex-col justify-between relative group hover:shadow-lg transition-all duration-300"
                >
                  <div>
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div>
                        <span className={`px-2.5 py-0.5 rounded-full text-[9px] font-bold tracking-wide uppercase ${getDomainColor(proj.domain)}`}>
                          {proj.domain}
                        </span>
                        <h4 className="text-sm font-bold text-zinc-900 dark:text-zinc-50 mt-2 tracking-tight">{proj.project_name}</h4>
                      </div>
                      <div className="flex items-center gap-1 bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-100/50 dark:border-emerald-900/30 rounded-lg px-2 py-1 flex-shrink-0">
                        <TrendingUp size={10} className="text-emerald-500" />
                        <span className="text-[10px] font-bold text-emerald-500">{proj.confidence_score}%</span>
                      </div>
                    </div>

                    <p className="text-xs text-zinc-500 dark:text-zinc-400 line-clamp-3 leading-relaxed mb-4 min-h-[3rem]">
                      {proj.executive_summary || 'No overview.'}
                    </p>

                    <div className="flex items-center gap-3.5 py-2.5 text-[10px] text-zinc-500 dark:text-zinc-400 font-semibold mb-4 border-t border-b border-zinc-150/40 dark:border-zinc-800/40">
                      <span className="flex items-center gap-1.5">
                        <Layers size={11} className="text-blue-500" />
                        {proj.total_requirements} specs
                      </span>
                      
                      <span className={`flex items-center gap-1.5 ${proj.conflict_count > 0 ? 'text-rose-500' : ''}`}>
                        <AlertOctagon size={11} />
                        {proj.conflict_count} conflicts
                      </span>

                      <span className="flex items-center gap-1.5 ml-auto text-[9px] text-zinc-400 dark:text-zinc-500 font-medium">
                        <Calendar size={11} />
                        {formatDate(proj.created_at)}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <button
                      onClick={(event) => {
                        event.stopPropagation();
                        if (window.confirm(`Delete "${proj.project_name}" from the archive?`)) {
                          handleDeleteProject(proj.id);
                        }
                      }}
                      className="p-1.5 text-zinc-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/20 rounded-lg transition-all cursor-pointer border border-transparent hover:border-rose-100 dark:hover:border-rose-900/30"
                      title="Delete Project"
                    >
                      <Trash2 size={13} />
                    </button>

                    <button
                      onClick={() => handleSelectProject(proj.id)}
                      className="flex items-center gap-1 text-xs font-bold text-blue-600 dark:text-blue-400 hover:text-blue-500 transition-colors cursor-pointer group/btn"
                    >
                      Open BRD
                      <ArrowRight size={13} className="group-hover/btn:translate-x-0.5 transition-transform" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>

    </div>
  );
}
