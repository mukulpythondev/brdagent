import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Legend, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  CartesianGrid
} from 'recharts';
import { useApp } from '../context/AppContext';
import {
  ChevronDown, ChevronRight, AlertOctagon, Download,
  FileText, FileSpreadsheet, Mail, Trash2, ArrowUpDown,
  Shield, Target, Users, CheckSquare, Lightbulb,
  BookOpen, ListChecks, TrendingUp, Palette, Share2, Printer, LayoutDashboard,
  BrainCircuit
} from 'lucide-react';
import ProfileDropdown from '../components/ProfileDropdown';

const CHART_COLORS = {
  HIGH: '#10b981', MEDIUM: '#f59e0b', LOW: '#ef4444',
  'MUST HAVE': '#2563eb', 'SHOULD HAVE': '#06b6d4', 'COULD HAVE': '#94a3b8'
};

const PDF_THEMES = [
  { name: 'Corporate Blue', primary: 'bg-blue-600', text: 'text-blue-600' },
  { name: 'Emerald Clean', primary: 'bg-emerald-600', text: 'text-emerald-600' },
  { name: 'Warm Crimson', primary: 'bg-rose-600', text: 'text-rose-600' },
  { name: 'Slate Minimalist', primary: 'bg-zinc-800', text: 'text-zinc-800' }
];

const CustomAnalyticsTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white/95 dark:bg-zinc-900/95 backdrop-blur-md px-3 py-2 border border-zinc-200/80 dark:border-zinc-800/80 rounded-xl shadow-xl text-left">
        <p className="text-[11px] font-bold text-zinc-900 dark:text-zinc-50">{payload[0].name}</p>
        <p className="text-[11px] font-semibold text-blue-600 dark:text-blue-400 mt-0.5">
          {payload[0].value} {payload[0].value === 1 ? 'Requirement' : 'Requirements'}
        </p>
      </div>
    );
  }
  return null;
};

export default function VisualizerPage({ showAnalytics = false }) {
  const {
    activeProject, selectedReqs, setSelectedReqs,
    handleDeleteSelectedReqs, handleChangePriority, handleSaveToArchive,
    pdfTheme, setPdfTheme, addToast, handleResolveConflict, setActivePage
  } = useApp();

  const [activeSection, setActiveSection] = useState('summary');
  const [isRightCollapsed, setIsRightCollapsed] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [emailInput, setEmailInput] = useState('');
  
  const [resolverConflictId, setResolverConflictId] = useState(null);
  const [resolutionType, setResolutionType] = useState('keep_req1');
  const [mergeDescription, setMergeDescription] = useState('');

  const sectionRefs = {
    summary: useRef(null),
    objectives: useRef(null),
    scope: useRef(null),
    stakeholders: useRef(null),
    fr: useRef(null),
    nfr: useRef(null),
    risks: useRef(null),
    assumptions: useRef(null),
    acceptance: useRef(null),
    domain: useRef(null),
    architecture: useRef(null)
  };

  const handleScrollToSection = (sectionId) => {
    setActiveSection(sectionId);
    const targetRef = sectionRefs[sectionId];
    if (targetRef && targetRef.current) {
      targetRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  if (!activeProject) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-16 text-center">
        <AlertOctagon size={48} className="mx-auto text-zinc-300 dark:text-zinc-700 mb-4 animate-bounce" />
        <h3 className="text-base font-bold text-zinc-700 dark:text-zinc-300">No Project Loaded</h3>
        <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-2 max-w-xs mx-auto">Go to Dashboard or Upload to load a project.</p>
        <button onClick={() => setActivePage('dashboard')} className="mt-5 text-xs font-bold text-blue-600 hover:text-blue-500 cursor-pointer">Back to Dashboard</button>
      </div>
    );
  }

  const frs = activeProject.functional_requirements || [];
  const nfrs = activeProject.non_functional_requirements || [];
  const allReqs = [...frs, ...nfrs];
  const totalReqs = allReqs.length;
  const highConf = allReqs.filter(r => r.confidence === 'HIGH').length;
  const conflictsCount = (activeProject.detected_conflicts || []).length;
  const coverageScore = activeProject.coverage_score || 0;

  const confData = [
    { name: 'High', value: allReqs.filter(r => r.confidence === 'HIGH').length },
    { name: 'Medium', value: allReqs.filter(r => r.confidence === 'MEDIUM').length },
    { name: 'Low', value: allReqs.filter(r => r.confidence === 'LOW').length }
  ].filter(d => d.value > 0);

  const priorityData = [
    { name: 'Must Have', value: frs.filter(r => r.priority === 'MUST HAVE').length },
    { name: 'Should Have', value: frs.filter(r => r.priority === 'SHOULD HAVE').length },
    { name: 'Could Have', value: frs.filter(r => r.priority === 'COULD HAVE').length }
  ].filter(d => d.value > 0);

  const radarData = [
    { subject: 'Data Isolation', A: 90, fullMark: 100 },
    { subject: 'PCI-DSS Sec 3', A: 85, fullMark: 100 },
    { subject: 'MFA Coverage', A: 95, fullMark: 100 },
    { subject: 'Audit Logging', A: 70, fullMark: 100 },
    { subject: 'Encryption Level', A: 92, fullMark: 100 },
    { subject: 'Latency Resiliency', A: 80, fullMark: 100 }
  ];

  const aiArchitecture = activeProject.ai_architecture;
  const modelRoutes = activeProject.model_routing_decisions || [];
  const isSummaryOnlyProject = !activeProject.brd_json && totalReqs === 0 && (activeProject.total_requirements || 0) > 0;

  if (isSummaryOnlyProject) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-16 text-center">
        <FileText size={42} className="mx-auto text-blue-500 mb-4 animate-pulse" />
        <h3 className="text-base font-bold text-zinc-700 dark:text-zinc-300">Loading BRD details</h3>
        <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-2 max-w-xs mx-auto">Fetching the full generated requirements document...</p>
      </div>
    );
  }

  const toggleReqSelection = (id) => {
    setSelectedReqs(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleSelectAllFrs = () => {
    const allFrIds = frs.map(r => r.id);
    if (allFrIds.every(id => selectedReqs.has(id))) {
      setSelectedReqs(prev => {
        const next = new Set(prev);
        allFrIds.forEach(id => next.delete(id));
        return next;
      });
    } else {
      setSelectedReqs(prev => {
        const next = new Set(prev);
        allFrIds.forEach(id => next.add(id));
        return next;
      });
    }
  };

  const handleSendEmail = async () => {
    if (!emailInput.trim()) {
      addToast('Recipient email required.', 'error');
      return;
    }
    try {
      const token = localStorage.getItem('brd_token');
      const response = await fetch(`/api/projects/${activeProject.id}/share`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ email: emailInput })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Email transmission failed');
      }
      addToast(`BRD PDF successfully emailed to: ${emailInput}`, 'success');
      setShowEmailModal(false);
      setEmailInput('');
    } catch (error) {
      addToast(error.message, 'error');
    }
  };

  const triggerFileDownload = async (url, defaultFilename) => {
    try {
      const token = localStorage.getItem('brd_token');
      const response = await fetch(url, {
        headers: {
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        }
      });
      if (!response.ok) throw new Error('Download failed');
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = defaultFilename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
      addToast('Download complete!', 'success');
    } catch (err) {
      console.error(err);
      addToast('File download failed.', 'error');
    }
  };

  const triggerConflictResolve = (conflict) => {
    setResolverConflictId(conflict.id);
    setResolutionType('keep_req1');
    const r1 = frs.find(r => r.id === conflict.req1_id);
    const r2 = frs.find(r => r.id === conflict.req2_id);
    setMergeDescription(`Combined: ${r1?.description || ''} and ${r2?.description || ''}`);
  };

  const submitResolution = () => {
    handleResolveConflict(resolverConflictId, resolutionType, mergeDescription);
    setResolverConflictId(null);
  };

  // Borderless Document Section
  const DocumentSection = ({ id, title, icon: Icon, children }) => {
    return (
      <div
        ref={sectionRefs[id]}
        className="scroll-mt-32 premium-card p-6 mb-5"
      >
        <div className="flex items-center gap-2.5 mb-4">
          {Icon && <Icon size={15} className="text-blue-500" />}
          <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100">
            {title}
          </h3>
        </div>
        <div>{children}</div>
      </div>
    );
  };

  // Borderless Requirement Card
  const RequirementCard = ({ req, showSelect = false }) => {
    const isSelected = selectedReqs.has(req.id);

    return (
      <motion.div
        layout
        className={`rounded-xl p-5 mb-3 transition-all duration-200 relative ${
          isSelected 
            ? 'bg-blue-50/50 dark:bg-blue-950/15 ring-1 ring-blue-500/20' 
            : 'bg-zinc-50/50 dark:bg-zinc-800/20 hover:bg-zinc-100/50 dark:hover:bg-zinc-800/30'
        }`}
      >
        <div className="flex items-start justify-between gap-4 mb-3">
          <div className="flex items-start gap-3 min-w-0">
            {showSelect && (
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => toggleReqSelection(req.id)}
                className="mt-1 w-3.5 h-3.5 rounded text-blue-600 focus:ring-blue-500 focus:ring-0 cursor-pointer"
              />
            )}
            <div>
              <span className="font-mono text-[10px] font-semibold text-blue-500">{req.id}</span>
              <h4 className="text-sm font-bold text-zinc-900 dark:text-zinc-50 leading-tight mt-0.5">{req.title}</h4>
            </div>
          </div>
          <div className="flex items-center gap-1.5 flex-shrink-0">
            {req.priority && (
              <span className={`px-2.5 py-0.5 rounded-full text-[9px] font-semibold ${
                req.priority === 'MUST HAVE' 
                  ? 'bg-blue-50 text-blue-600 dark:bg-blue-950/25 dark:text-blue-400' 
                  : req.priority === 'SHOULD HAVE'
                    ? 'bg-cyan-50 text-cyan-600 dark:bg-cyan-950/25 dark:text-cyan-400'
                    : 'bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400'
              }`}>
                {req.priority}
              </span>
            )}
            <span className={`px-2.5 py-0.5 rounded-full text-[9px] font-semibold ${
              req.confidence === 'HIGH' 
                ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/25 dark:text-emerald-400' 
                : 'bg-amber-50 text-amber-600 dark:bg-amber-950/25 dark:text-amber-400'
            }`}>
              {req.confidence}
            </span>
          </div>
        </div>

        <p className="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed mb-3">
          {req.description}
        </p>

        <div className="flex items-center justify-between text-[10px] text-zinc-400 dark:text-zinc-500 font-medium pt-2.5">
          <span>Source: <strong className="text-zinc-500 dark:text-zinc-400">{req.source}</strong></span>
          <span className="truncate max-w-[240px]">{req.source_trace}</span>
        </div>
      </motion.div>
    );
  };

  return (
    <div className="h-full overflow-hidden flex flex-col relative bg-[#f4f6fb] dark:bg-[#09090b] px-4 sm:px-6 lg:px-8 pt-4 pb-4">
      {/* Floating Header */}
      <div className="absolute top-4 left-4 right-4 sm:left-6 sm:right-6 lg:left-8 lg:right-8 z-30 bg-white/90 dark:bg-zinc-900/90 backdrop-blur-xl rounded-2xl border border-zinc-200/80 dark:border-zinc-800/80 shadow-md px-6 py-3.5 flex flex-col md:flex-row md:items-center md:justify-between gap-4 transition-all duration-200">
        <div>
          <h2 className="text-lg font-extrabold tracking-tight text-zinc-900 dark:text-zinc-50">{showAnalytics ? "Analytics Insights" : "BRD Visualizer"}</h2>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="hidden lg:flex flex-col items-end text-right justify-center">
            <span className="px-2.5 py-0.5 rounded-full text-[9px] font-semibold bg-blue-50 text-blue-600 dark:bg-blue-950/30 dark:text-blue-400 uppercase tracking-wide">
              {activeProject.domain}
            </span>
            <p className="text-[10px] text-zinc-400 dark:text-zinc-500 mt-0.5 font-medium truncate max-w-[200px]">
              {activeProject.project_name}
            </p>
          </div>
          <div className="h-6 w-px bg-zinc-200 dark:bg-zinc-800 hidden lg:block" />
          
          <div className="flex gap-2">
            <button
              onClick={() => setActivePage('dashboard')}
              className="flex items-center gap-1.5 px-3 py-2 bg-white dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-800 hover:text-zinc-900 dark:hover:text-zinc-100 shadow-sm active:scale-[0.98] rounded-xl text-xs font-semibold transition-all cursor-pointer"
            >
              Dashboard
            </button>
            {!showAnalytics && (
              <button
                onClick={() => setIsRightCollapsed(!isRightCollapsed)}
                className="flex items-center gap-1.5 px-3 py-2 bg-white dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-800 hover:bg-rose-50 dark:hover:bg-rose-950/20 hover:text-rose-600 shadow-sm active:scale-[0.98] rounded-xl text-xs font-semibold transition-all cursor-pointer"
              >
                <AlertOctagon size={13} className={conflictsCount > 0 ? "text-rose-500 animate-pulse" : "text-zinc-400"} />
                <span>{isRightCollapsed ? "Show" : "Hide"} Conflicts</span>
              </button>
            )}
            <button
              onClick={handleSaveToArchive}
              className="flex items-center gap-1.5 px-3 py-2 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white rounded-xl text-xs font-semibold transition-all shadow-lg shadow-blue-500/15 cursor-pointer active:scale-[0.98]"
            >
              Save
            </button>
          </div>
          <div className="h-6 w-px bg-zinc-200 dark:bg-zinc-800 hidden sm:block" />
          <ProfileDropdown />
        </div>
      </div>

      <div className="flex-1 flex flex-col overflow-hidden">
        {showAnalytics ? (
          /* ANALYTICS VIEW */
          <div className="flex-1 overflow-y-auto px-6 pt-[132px] pb-6 scroll-smooth">
            <div className="mx-auto max-w-7xl space-y-8 pb-12">
              
              {/* Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
                <div className="premium-card p-5">
                  <span className="text-[10px] font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">Total Specs</span>
                  <span className="block text-2xl font-extrabold text-zinc-900 dark:text-zinc-50 mt-1">{totalReqs}</span>
                </div>
                <div className="premium-card p-5">
                  <span className="text-[10px] font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">High Quality</span>
                  <span className="block text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-1">{highConf}</span>
                </div>
                <div className="premium-card p-5">
                  <span className="text-[10px] font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">Contradictions</span>
                  <span className={`block text-2xl font-extrabold mt-1 ${conflictsCount > 0 ? 'text-rose-500' : 'text-zinc-500'}`}>{conflictsCount}</span>
                </div>
                <div className="premium-card p-5">
                  <span className="text-[10px] font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">Compliance</span>
                  <span className="block text-2xl font-extrabold text-blue-500 mt-1">{coverageScore}%</span>
                </div>
              </div>

              {/* Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                <div className="premium-card p-5 flex flex-col min-h-[300px]">
                  <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 mb-4">Quality Distribution</h3>
                  <div className="flex-1 min-h-[220px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={confData} cx="50%" cy="50%"
                          innerRadius={50} outerRadius={70} paddingAngle={4}
                          dataKey="value" stroke="none"
                        >
                          {confData.map(entry => (
                            <Cell key={entry.name} fill={CHART_COLORS[entry.name.toUpperCase()] || '#cbd5e1'} />
                          ))}
                        </Pie>
                        <Tooltip content={<CustomAnalyticsTooltip />} />
                        <Legend verticalAlign="bottom" height={36} iconType="circle" formatter={v => <span className="text-[10px] text-zinc-500 font-semibold">{v}</span>} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="premium-card p-5 flex flex-col min-h-[300px]">
                  <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 mb-4">Priority Breakdown</h3>
                  <div className="flex-1 min-h-[220px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={priorityData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                        <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="#e2e8f0" className="dark:stroke-zinc-800/50" />
                        <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fontSize: 10, fill: '#64748b' }} />
                        <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 10, fill: '#94a3b8' }} allowDecimals={false} />
                        <Tooltip cursor={{ fill: 'rgba(37, 99, 235, 0.04)', radius: [6, 6, 0, 0] }} content={<CustomAnalyticsTooltip />} />
                        <Bar dataKey="value" radius={[8, 8, 0, 0]} barSize={32}>
                          {priorityData.map(entry => (
                            <Cell key={entry.name} fill={CHART_COLORS[entry.name.toUpperCase()] || '#818cf8'} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="premium-card p-5 flex flex-col min-h-[300px]">
                  <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 mb-4">Compliance Index</h3>
                  <div className="flex-1 min-h-[220px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                        <PolarGrid gridType="circle" stroke="#e2e8f0" className="dark:stroke-zinc-800" />
                        <PolarAngleAxis dataKey="subject" tick={{ fontSize: 8, fill: '#64748b' }} />
                        <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 7 }} stroke="none" />
                        <Radar name="Score" dataKey="A" stroke="#2563eb" fill="#2563eb" fillOpacity={0.12} />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

              </div>

              {/* Export & Compliance */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                <div className="premium-card p-6">
                  <h4 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 flex items-center gap-2 mb-4">
                    <Palette size={14} className="text-blue-500" />
                    Export Settings
                  </h4>

                  <div className="grid grid-cols-2 gap-3 mb-6">
                    {PDF_THEMES.map(themeOption => (
                      <button
                        key={themeOption.name}
                        onClick={() => setPdfTheme(themeOption.name)}
                        className={`flex items-center gap-2.5 p-3 rounded-xl text-left text-[11px] font-semibold transition-all cursor-pointer ${
                          pdfTheme === themeOption.name
                            ? 'bg-blue-50 dark:bg-blue-950/20 ring-1 ring-blue-500/20'
                            : 'bg-zinc-50 dark:bg-zinc-800/30 hover:bg-zinc-100 dark:hover:bg-zinc-800/50'
                        }`}
                      >
                        <div className={`w-3.5 h-3.5 rounded-full ${themeOption.primary}`} />
                        <span>{themeOption.name}</span>
                      </button>
                    ))}
                  </div>

                  <div className="flex flex-wrap gap-2.5">
                    <button
                      onClick={() => triggerFileDownload(
                        `/api/projects/${activeProject.id}/export/pdf?theme=${encodeURIComponent(pdfTheme)}`,
                        `${activeProject.project_name.replace(/\s+/g, '_')}_Requirements.pdf`
                      )}
                      className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white rounded-xl text-xs font-semibold transition-all shadow-md shadow-blue-500/10 cursor-pointer"
                    >
                      <Download size={13} />
                      Export PDF
                    </button>
                    <button
                      onClick={() => triggerFileDownload(
                        `/api/projects/${activeProject.id}/export/docx`,
                        `${activeProject.project_name.replace(/\s+/g, '_')}_Requirements.docx`
                      )}
                      className="flex items-center gap-1.5 px-4 py-2 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-800/80 text-zinc-700 dark:text-zinc-200 rounded-xl text-xs font-semibold shadow-sm active:scale-[0.98] transition-all cursor-pointer"
                    >
                      <FileText size={13} />
                      Export Docx
                    </button>
                    <button
                      onClick={() => triggerFileDownload(
                        `/api/projects/${activeProject.id}/export/xlsx`,
                        `${activeProject.project_name.replace(/\s+/g, '_')}_Requirements.xlsx`
                      )}
                      className="flex items-center gap-1.5 px-4 py-2 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-800/80 text-zinc-700 dark:text-zinc-200 rounded-xl text-xs font-semibold shadow-sm active:scale-[0.98] transition-all cursor-pointer"
                    >
                      <FileSpreadsheet size={13} />
                      Export Excel
                    </button>
                    <button
                      onClick={() => setShowEmailModal(true)}
                      className="flex items-center gap-1.5 px-4 py-2 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-800/80 text-zinc-700 dark:text-zinc-200 rounded-xl text-xs font-semibold shadow-sm active:scale-[0.98] transition-all cursor-pointer"
                    >
                      <Mail size={13} />
                      Email
                    </button>
                  </div>
                </div>

                <div className="premium-card p-6">
                  <h4 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 flex items-center gap-2 mb-4">
                    <Shield size={14} className="text-blue-500" />
                    Compliance Details
                  </h4>

                  {activeProject.domain_adjustments ? (
                    <div className="space-y-4">
                      <div>
                        <span className="block text-[10px] font-semibold text-zinc-500 uppercase tracking-wide mb-1.5">Compliance Target</span>
                        <div className="flex flex-wrap gap-1.5">
                          {activeProject.domain_adjustments.compliance_standards?.map(std => (
                            <span key={std} className="px-2.5 py-0.5 bg-zinc-50 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 rounded-full text-[10px] font-medium">{std}</span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <span className="block text-[10px] font-semibold text-zinc-500 uppercase tracking-wide mb-1">Focus Area</span>
                        <p className="text-xs text-zinc-700 dark:text-zinc-300 leading-relaxed">{activeProject.domain_adjustments.nfr_focus}</p>
                      </div>
                      <div>
                        <span className="block text-[10px] font-semibold text-zinc-500 uppercase tracking-wide mb-1">Glossary</span>
                        <p className="text-[10px] text-zinc-500 dark:text-zinc-400 leading-relaxed">
                          {activeProject.domain_adjustments.glossary?.join(' · ')}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <p className="text-xs text-zinc-400">No compliance data configured.</p>
                  )}
                </div>

              </div>

            </div>
          </div>
        ) : (
          /* BRD VISUALIZER VIEW */
          <div className="flex-1 flex flex-col overflow-hidden pt-[132px]">
            
            {/* Jump-to bar */}
            <div className="h-12 flex-shrink-0 bg-[#f4f6fb]/85 dark:bg-[#09090b]/85 backdrop-blur-xl px-6 flex items-center gap-1 transition-colors z-10 overflow-x-auto">
              <span className="text-[9px] font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide mr-2 flex items-center gap-1.5 flex-shrink-0">
                <LayoutDashboard size={12} className="text-blue-500" />
                Jump To:
              </span>
              {[
                { id: 'summary', label: 'Summary' },
                { id: 'objectives', label: 'Objectives' },
                { id: 'scope', label: 'Scope' },
                { id: 'stakeholders', label: 'Stakeholders' },
                { id: 'fr', label: 'Functional' },
                { id: 'nfr', label: 'Non-Functional' },
                { id: 'risks', label: 'Risks' },
                { id: 'assumptions', label: 'Assumptions' },
                { id: 'acceptance', label: 'Acceptance' },
                { id: 'domain', label: 'Industry' },
                { id: 'architecture', label: 'AI Routing' }
              ].map((sec) => {
                const isSelected = activeSection === sec.id;
                return (
                  <button
                    key={sec.id}
                    onClick={() => handleScrollToSection(sec.id)}
                    className={`px-3 py-1.5 rounded-lg text-[10px] font-semibold transition-all duration-200 cursor-pointer flex-shrink-0 ${
                      isSelected
                        ? 'bg-blue-50 text-blue-600 dark:bg-blue-950/30 dark:text-blue-400'
                        : 'text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800/40 hover:text-zinc-800 dark:hover:text-zinc-200'
                    }`}
                  >
                    {sec.label}
                  </button>
                );
              })}
            </div>

            {/* Content + Conflict drawer */}
            <div className="flex-1 flex overflow-hidden">
              
              {/* Main content */}
              <div className="flex-1 h-full overflow-y-auto px-6 py-6 scroll-smooth pb-24">
                <div className="max-w-4xl space-y-5">
                  
                  <DocumentSection id="summary" title="Executive Summary" icon={BookOpen}>
                    <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
                      {activeProject.executive_summary}
                    </p>
                  </DocumentSection>

                  <DocumentSection id="objectives" title="Project Objectives" icon={Target}>
                    <div className="space-y-3">
                      {activeProject.objectives?.map((obj, idx) => (
                        <div key={idx} className="flex gap-3 items-start text-sm text-zinc-600 dark:text-zinc-400">
                          <span className="w-6 h-6 rounded-lg bg-blue-50 dark:bg-blue-950/30 text-blue-500 flex items-center justify-center text-[10px] font-bold flex-shrink-0">{idx + 1}</span>
                          <p className="leading-relaxed">{obj}</p>
                        </div>
                      ))}
                    </div>
                  </DocumentSection>

                  <DocumentSection id="scope" title="Scope Boundaries" icon={Shield}>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="rounded-xl p-4 bg-emerald-50/30 dark:bg-emerald-950/10">
                        <span className="block text-[10px] font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wide mb-2">In-Scope</span>
                        <ul className="space-y-1.5">
                          {activeProject.scope?.in_scope?.map((s, idx) => (
                            <li key={idx} className="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed">✓ {s}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="rounded-xl p-4 bg-rose-50/30 dark:bg-rose-950/10">
                        <span className="block text-[10px] font-semibold text-rose-600 dark:text-rose-400 uppercase tracking-wide mb-2">Out-of-Scope</span>
                        <ul className="space-y-1.5">
                          {activeProject.scope?.out_scope?.map((s, idx) => (
                            <li key={idx} className="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed">✗ {s}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </DocumentSection>

                  <DocumentSection id="stakeholders" title="Stakeholders" icon={Users}>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {activeProject.stakeholders?.map((sh, idx) => (
                        <div key={idx} className="rounded-xl p-3 bg-zinc-50/50 dark:bg-zinc-800/20 text-sm text-zinc-700 dark:text-zinc-300">
                          {sh}
                        </div>
                      ))}
                    </div>
                  </DocumentSection>

                  <DocumentSection id="fr" title="Functional Requirements" icon={ListChecks}>
                    <div className="flex items-center justify-between mb-4">
                      <label className="flex items-center gap-2 text-[10px] font-semibold text-zinc-500 uppercase tracking-wide cursor-pointer">
                        <input
                          type="checkbox"
                          checked={frs.length > 0 && frs.every(r => selectedReqs.has(r.id))}
                          onChange={handleSelectAllFrs}
                          className="w-3.5 h-3.5 rounded text-blue-600 focus:ring-blue-500 focus:ring-0"
                        />
                        Select all
                      </label>
                      <span className="text-[10px] font-medium text-zinc-500">{frs.length} specifications</span>
                    </div>
                    <div className="space-y-1">
                      {frs.map(fr => <RequirementCard key={fr.id} req={fr} showSelect />)}
                    </div>
                  </DocumentSection>

                  <DocumentSection id="nfr" title="Non-Functional Requirements" icon={Shield}>
                    <div className="space-y-1">
                      {nfrs.map(nfr => <RequirementCard key={nfr.id} req={nfr} />)}
                    </div>
                  </DocumentSection>

                  <DocumentSection id="risks" title="Risks & Mitigations" icon={AlertOctagon}>
                    {activeProject.risks?.length === 0 ? (
                      <p className="text-xs text-zinc-400">No risks identified.</p>
                    ) : (
                      activeProject.risks?.map((r, idx) => (
                        <div key={idx} className="rounded-xl p-4 mb-3 bg-zinc-50/50 dark:bg-zinc-800/20">
                          <span className="block text-sm font-bold text-zinc-900 dark:text-zinc-50">{r.risk}</span>
                          <span className="block text-xs text-zinc-500 dark:text-zinc-400 mt-1.5 leading-relaxed">
                            <strong className="text-blue-500 text-[10px] mr-1">Mitigation:</strong> 
                            {r.mitigation}
                          </span>
                        </div>
                      ))
                    )}
                  </DocumentSection>

                  <DocumentSection id="assumptions" title="Assumptions" icon={Lightbulb}>
                    <div className="space-y-2.5">
                      {activeProject.assumptions?.map((as, idx) => (
                        <p key={idx} className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
                          {as}
                        </p>
                      ))}
                    </div>
                  </DocumentSection>

                  <DocumentSection id="acceptance" title="Acceptance Criteria" icon={CheckSquare}>
                    <div className="space-y-2.5">
                      {activeProject.acceptance_criteria?.map((cr, idx) => (
                        <label key={idx} className="flex items-start gap-2.5 text-sm text-zinc-600 dark:text-zinc-400 cursor-pointer">
                          <input
                            type="checkbox"
                            className="mt-0.5 w-3.5 h-3.5 rounded text-blue-600 focus:ring-blue-500 focus:ring-0"
                          />
                          <span className="leading-relaxed">{cr}</span>
                        </label>
                      ))}
                    </div>
                  </DocumentSection>

                  <DocumentSection id="domain" title="Industry Adjustments" icon={Lightbulb}>
                    {activeProject.domain_adjustments ? (
                      <div className="rounded-xl p-5 bg-zinc-50/50 dark:bg-zinc-800/20 text-sm text-zinc-600 dark:text-zinc-400 space-y-3">
                        <p><strong>Compliance:</strong> {activeProject.domain_adjustments.compliance_standards?.join(', ')}</p>
                        <p><strong>Focus:</strong> {activeProject.domain_adjustments.nfr_focus}</p>
                        <p><strong>Glossary:</strong> {activeProject.domain_adjustments.glossary?.join(' · ')}</p>
                      </div>
                    ) : (
                      <p className="text-xs text-zinc-400">No industry data configured.</p>
                    )}
                  </DocumentSection>

                  <DocumentSection id="architecture" title="Adaptive AI Routing" icon={BrainCircuit}>
                    {aiArchitecture ? (
                      <div className="space-y-5">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                          <div className="rounded-xl bg-zinc-50/70 dark:bg-zinc-800/30 p-3">
                            <span className="text-[9px] font-bold uppercase tracking-wide text-zinc-400">Inputs</span>
                            <p className="text-sm font-bold text-zinc-800 dark:text-zinc-100 mt-1">{aiArchitecture.input_count}</p>
                          </div>
                          <div className="rounded-xl bg-zinc-50/70 dark:bg-zinc-800/30 p-3">
                            <span className="text-[9px] font-bold uppercase tracking-wide text-zinc-400">Modalities</span>
                            <p className="text-sm font-bold text-zinc-800 dark:text-zinc-100 mt-1">{aiArchitecture.input_modalities?.join(', ')}</p>
                          </div>
                          <div className="rounded-xl bg-zinc-50/70 dark:bg-zinc-800/30 p-3">
                            <span className="text-[9px] font-bold uppercase tracking-wide text-zinc-400">Models</span>
                            <p className="text-sm font-bold text-zinc-800 dark:text-zinc-100 mt-1">{aiArchitecture.models_used?.join(', ')}</p>
                          </div>
                          <div className="rounded-xl bg-zinc-50/70 dark:bg-zinc-800/30 p-3">
                            <span className="text-[9px] font-bold uppercase tracking-wide text-zinc-400">Advanced</span>
                            <p className="text-sm font-bold text-zinc-800 dark:text-zinc-100 mt-1">{aiArchitecture.advanced_decisions}/{aiArchitecture.total_decisions}</p>
                          </div>
                        </div>

                        <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">{aiArchitecture.strategy}</p>

                        <div className="space-y-2.5">
                          {modelRoutes.slice(0, 6).map((route, idx) => (
                            <div key={`${route.purpose}-${idx}`} className="rounded-xl border border-zinc-100 dark:border-zinc-800 bg-white/60 dark:bg-zinc-900/30 p-3">
                              <div className="flex flex-wrap items-center gap-2 mb-1.5">
                                <span className="font-mono text-[10px] font-bold text-blue-600 dark:text-blue-400">{route.model}</span>
                                <span className="text-[9px] px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-zinc-500 font-bold uppercase">{route.purpose?.replaceAll('_', ' ')}</span>
                                <span className="text-[9px] px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400 font-bold uppercase">{route.tier}</span>
                              </div>
                              <p className="text-[11px] text-zinc-500 dark:text-zinc-400 leading-relaxed">
                                {route.reasons?.join(' | ')}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <p className="text-xs text-zinc-400">Generate a new BRD to see adaptive model routing details.</p>
                    )}
                  </DocumentSection>

                </div>
              </div>

              {/* Conflict drawer */}
              <div className={`h-full flex-shrink-0 overflow-y-auto bg-white dark:bg-[#111113] transition-all duration-300 ${
                isRightCollapsed ? 'w-0 overflow-hidden' : 'w-80 p-5'
              }`} style={{ boxShadow: isRightCollapsed ? 'none' : '-1px 0 8px rgba(0,0,0,0.03)' }}>
                <div className="space-y-5 pb-20">
                  
                  {/* Conflict panel */}
                  <div className="premium-card p-5">
                    <div className="flex items-center justify-between pb-2.5 mb-4">
                      <h4 className="text-xs font-bold text-zinc-900 dark:text-zinc-100 flex items-center gap-1.5">
                        <AlertOctagon size={13} className="text-rose-500" />
                        Conflicts
                      </h4>
                      <span className="text-[9px] px-2 py-0.5 rounded-full bg-rose-50 dark:bg-rose-950/30 text-rose-500 font-semibold">{conflictsCount} active</span>
                    </div>

                    {conflictsCount === 0 ? (
                      <div className="text-center py-6">
                        <CheckSquare size={20} className="mx-auto text-emerald-500 mb-2" />
                        <p className="text-xs font-semibold text-zinc-700 dark:text-zinc-300">All Clear</p>
                        <p className="text-[10px] text-zinc-500 dark:text-zinc-400 mt-0.5">No logical conflicts detected.</p>
                      </div>
                    ) : (
                      <div className="space-y-3.5">
                        {activeProject.detected_conflicts?.map((conf) => (
                          <div key={conf.id} className="rounded-xl p-3.5 bg-rose-50/30 dark:bg-rose-950/10">
                            <span className="font-mono text-[9px] font-bold text-rose-500 block mb-1">{conf.req1_id} vs {conf.req2_id}</span>
                            <p className="text-[11px] text-zinc-600 dark:text-zinc-400 leading-relaxed mb-3">{conf.description}</p>
                            
                            <button
                              onClick={() => triggerConflictResolve(conf)}
                              className="w-full text-center py-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 dark:bg-rose-950/20 dark:hover:bg-rose-950/30 text-rose-600 dark:text-rose-400 text-[10px] font-bold transition-colors cursor-pointer"
                            >
                              Resolve Conflict
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Sync */}
                  <div className="premium-card p-5 text-center">
                    <p className="text-[10px] text-zinc-500 dark:text-zinc-400 mb-3">Sync edits to cloud</p>
                    <button
                      onClick={handleSaveToArchive}
                      className="w-full flex items-center justify-center gap-1.5 py-2 rounded-xl bg-blue-50 dark:bg-blue-950/25 text-blue-600 dark:text-blue-400 text-xs font-semibold hover:bg-blue-100/50 dark:hover:bg-blue-950/40 transition-all cursor-pointer"
                    >
                      <Share2 size={13} />
                      Sync Workspace
                    </button>
                  </div>

                </div>
              </div>

            </div>

          </div>
        )}
      </div>

      {/* Bulk Actions */}
      <AnimatePresence>
        {selectedReqs.size > 0 && !showAnalytics && (
          <motion.div
            initial={{ y: 80, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 80, opacity: 0 }}
            className="fixed bottom-6 inset-x-4 max-w-lg mx-auto z-45 bg-zinc-900 dark:bg-white rounded-2xl p-4 shadow-2xl flex items-center justify-between gap-4 text-white dark:text-zinc-900"
          >
            <span className="text-[11px] font-bold">{selectedReqs.size} selected</span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => handleChangePriority('MUST HAVE')}
                className="px-3.5 py-1.5 rounded-lg text-[10px] font-bold bg-zinc-800 hover:bg-zinc-700 dark:bg-zinc-100 dark:hover:bg-zinc-200 transition-colors cursor-pointer"
              >
                Set Must
              </button>
              <button
                onClick={() => handleChangePriority('SHOULD HAVE')}
                className="px-3.5 py-1.5 rounded-lg text-[10px] font-bold bg-zinc-800 hover:bg-zinc-700 dark:bg-zinc-100 dark:hover:bg-zinc-200 transition-colors cursor-pointer"
              >
                Set Should
              </button>
              <button
                onClick={handleDeleteSelectedReqs}
                className="px-3.5 py-1.5 rounded-lg text-[10px] font-bold bg-rose-600 hover:bg-rose-500 text-white transition-colors flex items-center gap-1 cursor-pointer"
              >
                <Trash2 size={11} />
                Delete
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Resolution Modal */}
      <AnimatePresence>
        {resolverConflictId && (
          <div className="fixed inset-0 z-50 bg-zinc-950/80 backdrop-blur-md flex items-center justify-center p-4">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="premium-card p-6 max-w-md w-full"
              style={{ boxShadow: '0 16px 64px rgba(0,0,0,0.2)' }}
            >
              <h3 className="text-base font-bold text-zinc-900 dark:text-zinc-50 flex items-center gap-1.5 mb-4">
                <AlertOctagon size={16} className="text-rose-500" />
                Resolve Conflict
              </h3>
              
              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-[10px] font-semibold text-zinc-500 uppercase tracking-wide mb-1.5">Resolution Path</label>
                  <select
                    value={resolutionType}
                    onChange={(e) => setResolutionType(e.target.value)}
                    className="w-full text-sm bg-zinc-50 dark:bg-zinc-900 rounded-xl py-2.5 px-3.5 text-zinc-800 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
                  >
                    <option value="keep_req1">Keep primary requirement</option>
                    <option value="keep_req2">Keep secondary requirement</option>
                    <option value="merge">Merge requirements</option>
                  </select>
                </div>

                {resolutionType === 'merge' && (
                  <div>
                    <label className="block text-[10px] font-semibold text-zinc-500 uppercase tracking-wide mb-1.5">Merged Description</label>
                    <textarea
                      value={mergeDescription}
                      onChange={(e) => setMergeDescription(e.target.value)}
                      rows={3}
                      className="w-full text-sm bg-zinc-50 dark:bg-zinc-900 rounded-xl py-2.5 px-3.5 text-zinc-800 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-blue-500/30 resize-none"
                    />
                  </div>
                )}
              </div>

              <div className="flex gap-2.5">
                <button
                  onClick={() => setResolverConflictId(null)}
                  className="flex-1 text-center py-2.5 bg-zinc-50 dark:bg-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-700 text-zinc-600 dark:text-zinc-300 rounded-xl text-xs font-semibold transition-all cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  onClick={submitResolution}
                  className="flex-1 text-center py-2.5 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white rounded-xl text-xs font-semibold transition-all shadow-md shadow-blue-500/10 cursor-pointer"
                >
                  Apply Resolution
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Email Modal */}
      <AnimatePresence>
        {showEmailModal && (
          <div className="fixed inset-0 z-50 bg-zinc-950/80 backdrop-blur-md flex items-center justify-center p-4" onClick={() => setShowEmailModal(false)}>
            <motion.div
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.95 }}
              onClick={(e) => e.stopPropagation()}
              className="premium-card p-6 max-w-sm w-full text-center"
              style={{ boxShadow: '0 16px 64px rgba(0,0,0,0.2)' }}
            >
              <Mail size={24} className="mx-auto text-blue-500 mb-3" />
              <h3 className="text-base font-bold text-zinc-900 dark:text-zinc-50 mb-1.5">Send BRD Document</h3>
              <p className="text-xs text-zinc-500 mb-5">Send the document as a PDF attachment.</p>

              <input
                type="email"
                placeholder="recipient@company.com"
                value={emailInput}
                onChange={e => setEmailInput(e.target.value)}
                className="w-full text-sm bg-zinc-50 dark:bg-zinc-900 rounded-xl py-2.5 px-3.5 text-zinc-800 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-blue-500/30 mb-5 text-center"
              />

              <div className="flex gap-2">
                <button onClick={() => setShowEmailModal(false)} className="flex-1 py-2.5 bg-zinc-50 dark:bg-zinc-800 rounded-xl text-xs font-semibold text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-all cursor-pointer">Cancel</button>
                <button onClick={handleSendEmail} className="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-cyan-500 text-white rounded-xl text-xs font-semibold shadow-md shadow-blue-500/10 transition-all cursor-pointer">Send</button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
}
