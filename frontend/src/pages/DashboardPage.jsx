import { useApp } from '../context/AppContext';
import { BarChart, Bar, Cell, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { PlusCircle, ArrowRight, FolderKanban, AlertOctagon, TrendingUp, CheckCircle2 } from 'lucide-react';
import ProfileDropdown from '../components/ProfileDropdown';

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white/95 dark:bg-zinc-900/95 backdrop-blur-md px-3 py-2 border border-zinc-200/80 dark:border-zinc-800/80 rounded-xl shadow-xl text-left">
        <p className="text-xs font-bold text-zinc-900 dark:text-zinc-50">{payload[0].name}</p>
        <p className="text-xs font-semibold text-blue-600 dark:text-blue-400 mt-0.5">
          {payload[0].value} {payload[0].value === 1 ? 'Requirement' : 'Requirements'}
        </p>
      </div>
    );
  }
  return null;
};

const CHART_COLORS = ['#2563eb', '#06b6d4', '#94a3b8'];

export default function DashboardPage() {
  const { projects, handleSelectProject, handleLoadDemo, setActivePage, versionHistory, theme } = useApp();

  const totalProjects = projects.length;
  const activeConflicts = projects.reduce((acc, p) => acc + p.conflict_count, 0);
  const avgConfidence = totalProjects > 0 ? Math.round(projects.reduce((acc, p) => acc + p.confidence_score, 0) / totalProjects) : 0;

  const mustCount = projects.reduce((acc, p) => acc + (p.functional_requirements?.filter(r => r.priority === 'MUST HAVE').length || 0), 0);
  const shouldCount = projects.reduce((acc, p) => acc + (p.functional_requirements?.filter(r => r.priority === 'SHOULD HAVE').length || 0), 0);
  const couldCount = projects.reduce((acc, p) => acc + (p.functional_requirements?.filter(r => r.priority === 'COULD HAVE').length || 0), 0);

  const chartData = [
    { name: 'Must Have', value: mustCount },
    { name: 'Should Have', value: shouldCount },
    { name: 'Could Have', value: couldCount }
  ].filter(d => d.value > 0);

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
          <h2 className="text-lg font-extrabold tracking-tight text-zinc-900 dark:text-zinc-50">Dashboard</h2>
          <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-0.5 font-medium">System metrics and active portfolio overview</p>
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
              Generate BRD
            </button>
          </div>
          <div className="h-6 w-px bg-zinc-200 dark:bg-zinc-800 hidden sm:block" />
          <ProfileDropdown />
        </div>
      </div>

      <div className="h-12" />

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mb-8">
        <div className="premium-card p-5 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-semibold text-zinc-500 dark:text-zinc-400 tracking-wide uppercase">Active Projects</span>
            <span className="block text-2xl font-extrabold text-zinc-900 dark:text-zinc-50 mt-1">{totalProjects}</span>
          </div>
          <div className="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-950/30 text-blue-500 flex items-center justify-center">
            <FolderKanban size={18} />
          </div>
        </div>

        <div className="premium-card p-5 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-semibold text-zinc-500 dark:text-zinc-400 tracking-wide uppercase">Contradictions</span>
            <span className="block text-2xl font-extrabold text-zinc-900 dark:text-zinc-50 mt-1">{activeConflicts} Active</span>
          </div>
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${activeConflicts > 0 ? 'bg-rose-50 dark:bg-rose-950/30 text-rose-500' : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-400'}`}>
            <AlertOctagon size={18} />
          </div>
        </div>

        <div className="premium-card p-5 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-semibold text-zinc-500 dark:text-zinc-400 tracking-wide uppercase">Quality Score</span>
            <span className="block text-2xl font-extrabold text-blue-600 dark:text-blue-400 mt-1">{avgConfidence}%</span>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 text-emerald-500 flex items-center justify-center">
            <TrendingUp size={18} />
          </div>
        </div>
      </div>

      {/* Top Grid: Recent Workspaces and Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        
        {/* Recent Workspaces */}
        <div className="premium-card p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-50 flex items-center gap-2 mb-5">
              <FolderKanban size={16} className="text-blue-500" />
              Recent Workspaces
            </h3>
            
            {projects.length === 0 ? (
              <p className="text-xs text-zinc-400 py-6 text-center">No active projects.</p>
            ) : (
              <div className="space-y-1">
                {projects.slice(0, 3).map((proj) => (
                  <div key={proj.id} className="py-3.5 flex items-center justify-between gap-4 rounded-xl px-3 hover:bg-zinc-50 dark:hover:bg-zinc-800/30 transition-colors -mx-3">
                    <div className="min-w-0">
                      <span className="text-[9px] font-semibold text-blue-500 uppercase tracking-widest">{proj.domain}</span>
                      <h4 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 leading-tight mt-0.5 truncate">{proj.project_name}</h4>
                      <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1">
                        {proj.total_requirements} specs · {proj.conflict_count} conflicts
                      </p>
                    </div>

                    <button
                      onClick={() => handleSelectProject(proj.id)}
                      className="flex items-center gap-1 text-[11px] font-bold text-blue-600 dark:text-blue-400 hover:text-blue-500 transition-colors uppercase tracking-wide flex-shrink-0 cursor-pointer"
                    >
                      Launch
                      <ArrowRight size={12} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Priority Breakdown (Chart) */}
        <div className="premium-card p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-50 flex items-center gap-2 mb-5">
              <TrendingUp size={15} className="text-blue-500" />
              Priority Breakdown
            </h3>

            {chartData.length === 0 ? (
              <p className="text-xs text-zinc-400 py-6 text-center">No requirement data available.</p>
            ) : (
              <div className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: -25, bottom: 5 }}>
                    <CartesianGrid vertical={false} strokeDasharray="3 3" stroke={theme === 'dark' ? '#27272a' : '#f1f5f9'} />
                    <XAxis 
                      dataKey="name" 
                      tickLine={false} 
                      axisLine={{ stroke: theme === 'dark' ? '#27272a' : '#cbd5e1', strokeWidth: 1 }} 
                      tick={{ fontSize: 9, fill: '#64748b', fontWeight: 500 }} 
                      padding={{ left: 60, right: 60 }}
                    />
                    <YAxis 
                      tickLine={false} 
                      axisLine={{ stroke: theme === 'dark' ? '#27272a' : '#cbd5e1', strokeWidth: 1 }} 
                      tick={{ fontSize: 9, fill: '#94a3b8' }} 
                      allowDecimals={false} 
                    />
                    <Tooltip 
                      cursor={{ fill: 'rgba(37, 99, 235, 0.04)', radius: [6, 6, 0, 0] }} 
                      content={<CustomTooltip />}
                    />
                    <Bar dataKey="value" radius={[6, 6, 0, 0]} barSize={42}>
                      {chartData.map((entry, idx) => (
                        <Cell key={entry.name} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Bottom Row: Activity Log */}
      <div className="premium-card p-6">
        <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-50 mb-5">
          Activity Log
        </h3>
        
        <div className="flow-root">
          <ul className="-mb-8">
            {versionHistory.map((log, logIdx) => (
              <li key={log.id}>
                <div className="relative pb-6">
                  {logIdx !== versionHistory.length - 1 ? (
                    <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-zinc-150 dark:bg-zinc-800" aria-hidden="true" />
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
                      <p className="text-[10px] text-zinc-500 dark:text-zinc-400 mt-0.5 leading-relaxed">
                        {log.details}
                      </p>
                      <div className="text-[9px] text-zinc-400 dark:text-zinc-500 mt-1.5 flex items-center gap-1.5 justify-between">
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
  );
}
