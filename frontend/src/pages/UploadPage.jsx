import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { useApp } from '../context/AppContext';
import {
  Upload, FileText, Image as ImageIcon, FileSpreadsheet, Trash2,
  Sparkles, PlayCircle, X, ShieldAlert, Cpu, Network, CheckCircle, Database
} from 'lucide-react';
import ProfileDropdown from '../components/ProfileDropdown';

const DOMAINS = ['Auto-detect', 'FinTech', 'HealthTech', 'E-Commerce', 'Enterprise', 'Government', 'EdTech'];

const FILE_ICONS = {
  '.pdf': { icon: FileText, color: 'text-rose-500 bg-rose-50 dark:bg-rose-950/20' },
  '.docx': { icon: FileSpreadsheet, color: 'text-blue-500 bg-blue-50 dark:bg-blue-950/20' },
  '.doc': { icon: FileSpreadsheet, color: 'text-blue-500 bg-blue-50 dark:bg-blue-950/20' },
  '.png': { icon: ImageIcon, color: 'text-purple-500 bg-purple-50 dark:bg-purple-950/20' },
  '.jpg': { icon: ImageIcon, color: 'text-purple-500 bg-purple-50 dark:bg-purple-950/20' },
  '.jpeg': { icon: ImageIcon, color: 'text-purple-500 bg-purple-50 dark:bg-purple-950/20' },
  '.txt': { icon: FileText, color: 'text-zinc-500 bg-zinc-100 dark:bg-zinc-800' }
};

export default function UploadPage() {
  const {
    projectName, setProjectName,
    selectedDomain, setSelectedDomain,
    pastedText, setPastedText,
    uploadedFiles, setUploadedFiles,
    isGenerating, pipelineStep,
    handleLoadDemo, handleGenerate
  } = useApp();

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => {
      const ext = '.' + file.name.split('.').pop().toLowerCase();
      return {
        filename: file.name,
        extension: ext,
        size_mb: (file.size / (1024 * 1024)).toFixed(2),
        type: ['.png', '.jpg', '.jpeg'].includes(ext) ? 'image' : 'text',
        rawFile: file
      };
    });
    setUploadedFiles(prev => [...prev, ...newFiles.filter(
      nf => !prev.some(ef => ef.filename === nf.filename)
    )]);
  }, [setUploadedFiles]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg'],
      'text/plain': ['.txt'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 10 * 1024 * 1024,
  });

  const removeFile = (filename) => {
    setUploadedFiles(prev => prev.filter(f => f.filename !== filename));
  };

  const clearInputs = () => {
    setProjectName('');
    setPastedText('');
    setUploadedFiles([]);
  };

  const totalSources = uploadedFiles.length + (pastedText.trim() ? 1 : 0);

  const TIMELINE_STEPS = [
    { step: 1, label: 'Document Parsing & OCR', desc: 'Reading layouts, text blocks, and diagrams', icon: Database },
    { step: 2, label: 'Domain Classification', desc: 'Matching compliance standards and glossaries', icon: Network },
    { step: 3, label: 'Semantic Extraction', desc: 'Identifying functional requirements', icon: Cpu },
    { step: 4, label: 'Contradiction Analysis', desc: 'Cross-checking for mismatches', icon: ShieldAlert }
  ];

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-4 pb-8">
      
      {/* Floating Header */}
      <div className="sticky top-4 z-20 bg-white/90 dark:bg-zinc-900/90 backdrop-blur-xl rounded-2xl border border-zinc-200/80 dark:border-zinc-800/80 shadow-md px-6 py-3.5 flex flex-col md:flex-row md:items-center md:justify-between gap-4 transition-all duration-200">
        <div>
          <h2 className="text-lg font-extrabold tracking-tight text-zinc-900 dark:text-zinc-50">Upload & Ingest</h2>
          <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-0.5 font-medium">Feed raw specs, wireframes, and notes to the AI generator</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex gap-2">
            <button
              onClick={clearInputs}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-white dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-800 hover:text-zinc-900 dark:hover:text-zinc-100 shadow-sm active:scale-[0.98] rounded-xl text-xs font-semibold transition-all cursor-pointer"
            >
              Clear Inputs
            </button>
            <button
              onClick={handleLoadDemo}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-white dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-800 hover:bg-blue-50 dark:hover:bg-zinc-800 hover:text-blue-600 shadow-sm active:scale-[0.98] rounded-xl text-xs font-semibold transition-all cursor-pointer"
            >
              Load Demo
            </button>
          </div>
          <div className="h-6 w-px bg-zinc-200 dark:bg-zinc-800 hidden sm:block" />
          <ProfileDropdown />
        </div>
      </div>

      <div className="h-12" />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column */}
        <div className="lg:col-span-5 space-y-6">
          
          <div className="premium-card p-6">
            <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-50 flex items-center gap-2 mb-5">
              <Upload size={14} className="text-blue-500" />
              Parameters
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-[10px] font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide mb-1.5">Project Name</label>
                <input
                  type="text"
                  placeholder="e.g. Online Banking Portal"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  className="w-full text-sm bg-zinc-50/80 dark:bg-zinc-900/80 rounded-xl py-2.5 px-3.5 text-zinc-800 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-blue-500/30 placeholder-zinc-400"
                />
              </div>

              <div>
                <label className="block text-[10px] font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide mb-1.5">Industry Domain</label>
                <select
                  value={selectedDomain}
                  onChange={(e) => setSelectedDomain(e.target.value)}
                  className="w-full text-sm bg-zinc-50/80 dark:bg-zinc-900/80 rounded-xl py-2.5 px-3.5 text-zinc-800 dark:text-zinc-100 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
                >
                  {DOMAINS.map(d => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>
            </div>
          </div>

          {/* Files */}
          <div className="premium-card p-6 flex flex-col h-[280px]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-50">File Sources</h3>
              {totalSources > 0 && (
                <button
                  onClick={clearInputs}
                  className="text-[10px] font-semibold text-zinc-400 hover:text-rose-500 px-2 py-1 rounded transition-colors cursor-pointer"
                >
                  Clear
                </button>
              )}
            </div>

            <div
              {...getRootProps()}
              className={`rounded-xl p-5 text-center cursor-pointer transition-all duration-200 bg-zinc-50/50 dark:bg-zinc-800/20 hover:bg-blue-50/30 dark:hover:bg-zinc-800/30 ${
                isDragActive ? 'ring-2 ring-blue-500/30 bg-blue-50/20' : ''
              }`}
              style={{ border: '2px dashed rgba(148,163,184,0.3)' }}
            >
              <input {...getInputProps()} />
              <Upload size={20} className="mx-auto text-blue-500 mb-2" />
              <p className="text-xs font-medium text-zinc-700 dark:text-zinc-200">
                Drag files here or <span className="text-blue-500">browse</span>
              </p>
              <p className="text-[10px] text-zinc-400 mt-1">PDF, DOCX, PNG — Max 10MB</p>
            </div>

            <div className="flex-1 overflow-y-auto mt-4 space-y-2.5">
              {uploadedFiles.length === 0 ? (
                <div className="text-center py-6 text-zinc-400 text-[10px]">
                  No files attached.
                </div>
              ) : (
                uploadedFiles.map((file) => {
                  const iconConfig = FILE_ICONS[file.extension] || FILE_ICONS['.txt'];
                  const IconComponent = iconConfig.icon;
                  return (
                    <div
                      key={file.filename}
                      className="flex items-center justify-between rounded-xl p-2.5 bg-zinc-50/50 dark:bg-zinc-800/20"
                    >
                      <div className="flex items-center gap-2.5 min-w-0">
                        <div className={`p-1.5 rounded-lg ${iconConfig.color}`}>
                          <IconComponent size={14} />
                        </div>
                        <div className="truncate">
                          <span className="block text-xs font-medium text-zinc-800 dark:text-zinc-200 truncate leading-tight">{file.filename}</span>
                          <span className="text-[9px] text-zinc-400">{file.size_mb} MB</span>
                        </div>
                      </div>
                      <button
                        onClick={() => removeFile(file.filename)}
                        className="p-1 rounded text-zinc-400 hover:text-rose-500 transition-all cursor-pointer"
                      >
                        <X size={13} />
                      </button>
                    </div>
                  );
                })
              )}
            </div>
          </div>

        </div>

        {/* Right Column */}
        <div className="lg:col-span-7 space-y-6">
          <div className="premium-card p-6 flex flex-col h-[520px]">
            <div className="flex items-center justify-between pb-3 mb-4">
              <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-50 flex items-center gap-2">
                <FileText size={15} className="text-blue-500" />
                Raw Specification Input
              </h3>
              <span className="text-[10px] font-medium px-2.5 py-0.5 rounded-full bg-zinc-50 dark:bg-zinc-800 text-zinc-500">
                {pastedText.length} chars
              </span>
            </div>

            <textarea
              className="flex-1 w-full bg-zinc-50/50 dark:bg-zinc-800/20 rounded-xl p-4 text-sm leading-relaxed focus:outline-none focus:ring-2 focus:ring-blue-500/20 text-zinc-800 dark:text-zinc-100 placeholder-zinc-400 resize-none"
              placeholder="Paste unstructured project notes, transcripts, emails, or draft criteria here..."
              value={pastedText}
              onChange={(e) => setPastedText(e.target.value)}
            />
          </div>
        </div>

      </div>

      {/* Generate Button */}
      <div className="mt-8 flex items-center justify-end gap-3">
        <button
          onClick={handleLoadDemo}
          className="flex items-center gap-1.5 px-6 py-2.5 bg-white dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800 rounded-xl text-xs font-semibold transition-all shadow-sm cursor-pointer"
          style={{ boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}
        >
          <PlayCircle size={14} />
          Load Demo
        </button>
        
        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="flex items-center gap-2 px-8 py-2.5 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white rounded-xl text-sm font-bold transition-all shadow-lg shadow-blue-500/15 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer active:scale-[0.98]"
        >
          {isGenerating ? (
            <>
              <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full loading-spinner" />
              Synthesizing...
            </>
          ) : (
            <>
              <Sparkles size={14} />
              Generate BRD
            </>
          )}
        </button>
      </div>

      {/* Pipeline Overlay */}
      <AnimatePresence>
        {isGenerating && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-zinc-950/80 backdrop-blur-md flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="premium-card p-8 max-w-lg w-full text-center"
              style={{ boxShadow: '0 16px 64px rgba(0,0,0,0.2)' }}
            >
              <div className="w-16 h-16 rounded-full border-4 border-blue-500/25 border-t-blue-500 loading-spinner mx-auto mb-6 flex items-center justify-center">
                <Cpu size={22} className="text-blue-500 loading-spinner [animation-duration:3s]" />
              </div>
              
              <h3 className="text-base font-extrabold text-zinc-900 dark:text-zinc-50 mb-1">Synthesizing Requirements</h3>
              <p className="text-xs text-zinc-500 mb-6">AI engine is processing documents</p>

              <div className="w-full bg-zinc-100 dark:bg-zinc-800 h-1 rounded-full mb-8 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-blue-500 to-cyan-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${(pipelineStep / 4) * 100}%` }}
                />
              </div>

              <div className="space-y-3 text-left">
                {TIMELINE_STEPS.map((stage) => {
                  const isDone = pipelineStep > stage.step;
                  const isCurrent = pipelineStep === stage.step;
                  const StageIcon = stage.icon;

                  return (
                    <div
                      key={stage.step}
                      className={`flex items-start gap-4 p-3 rounded-xl transition-all duration-300 ${
                        isCurrent 
                          ? 'bg-blue-50/30 dark:bg-blue-950/15' 
                          : isDone 
                            ? 'bg-emerald-50/20 dark:bg-emerald-950/10' 
                            : 'bg-zinc-50 dark:bg-zinc-800/20 opacity-45'
                      }`}
                    >
                      <div className={`p-2 rounded-lg ${
                        isDone 
                          ? 'bg-emerald-100 dark:bg-emerald-950/30 text-emerald-500' 
                          : isCurrent 
                            ? 'bg-blue-100 dark:bg-blue-950/30 text-blue-500 animate-pulse' 
                            : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-400'
                      }`}>
                        {isDone ? <CheckCircle size={15} /> : <StageIcon size={15} />}
                      </div>
                      
                      <div>
                        <span className={`block text-xs font-bold ${isCurrent ? 'text-blue-600 dark:text-blue-400' : isDone ? 'text-emerald-600 dark:text-emerald-400' : 'text-zinc-500'}`}>
                          {stage.label}
                        </span>
                        <span className="block text-[10px] text-zinc-400 mt-0.5 leading-snug">{stage.desc}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}
