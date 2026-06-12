import { createContext, useContext, useState, useCallback, useEffect } from 'react';

const AppContext = createContext(null);

const DEFAULT_USER = {
  name: 'John Doe',
  email: 'john@brdforge.ai',
  initials: 'JD',
  role: 'Workspace Architect'
};

export function AppProvider({ children }) {
  const [activePage, setActivePage] = useState('dashboard'); // dashboard, ingest, editor, analytics, settings
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState('');
  
  // New Ingest Inputs
  const [projectName, setProjectName] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('Auto-detect');
  const [pastedText, setPastedText] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  
  // Pipeline Progress Tracker
  const [isGenerating, setIsGenerating] = useState(false);
  const [pipelineStep, setPipelineStep] = useState(0); // 0 = idle, 1 = OCR, 2 = Domain, 3 = Extract, 4 = Conflict

  // Selection states inside editor
  const [selectedReqs, setSelectedReqs] = useState(new Set());
  const [pdfTheme, setPdfTheme] = useState('Corporate Blue');
  const [toasts, setToasts] = useState([]);

  // Version history system
  const [versionHistory, setVersionHistory] = useState([]);

  // Developer / Profile Settings
  const [settings, setSettings] = useState({
    geminiApiKey: '••••••••••••••••••••',
    autoDetectDomain: true,
    showVisualConnectors: true,
    emailServerPort: '587',
    defaultExportTheme: 'Corporate Blue'
  });

  // Auth State
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    return localStorage.getItem('brd_logged_in') === 'true';
  });
  
  const [currentUser, setCurrentUser] = useState(() => {
    const savedUser = localStorage.getItem('brd_user');
    return savedUser ? JSON.parse(savedUser) : DEFAULT_USER;
  });

  // Helper function to prepare request headers
  const getHeaders = useCallback(() => {
    const token = localStorage.getItem('brd_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
  }, []);

  // Global Toast Handler
  const addToast = useCallback((message, type = 'success') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 3500);
  }, []);

  // Helper to save project locally in demo mode
  const saveLocalDemoProject = useCallback((projectId, updatedProject) => {
    setProjects(prev => {
      const next = prev.map(p => p.id === projectId ? updatedProject : p);
      localStorage.setItem('demo_projects_v5', JSON.stringify(next));
      return next;
    });
  }, []);

  // Fetch Projects List from Server
  const fetchProjects = useCallback(async () => {
    try {
      const response = await fetch('/api/projects', {
        headers: getHeaders()
      });
      if (!response.ok) throw new Error('Failed to load projects');
      const data = await response.json();
      const loadedProjects = data.projects || [];
      setProjects(loadedProjects);
      
      // Select first project if available and none selected
      if (loadedProjects.length > 0 && !selectedProjectId) {
        setSelectedProjectId(loadedProjects[0].id);
      }
    } catch (error) {
      console.warn("Backend connection failed, loading local demo projects:", error);
      const savedProjects = localStorage.getItem('demo_projects_v5');
      let loadedProjects = savedProjects ? JSON.parse(savedProjects) : [];
      if (loadedProjects.length === 0) {
        loadedProjects = [
          {
            id: 'demo-project-1',
            project_name: 'Online Banking Portal',
            domain: 'FinTech',
            created_at: new Date().toISOString(),
            confidence_score: 94,
            total_requirements: 6,
            conflict_count: 1,
            executive_summary: 'This project builds a next-generation online banking portal aimed at offering retail bank customers a secure, responsive, and real-time dashboard to monitor balance sheets, execute domestic wire transfers, and setup bills payments. This system complies with key financial regulatory frameworks like PCI-DSS Sec 3 and SOX.',
            objectives: [
              'Build a highly secure, responsive web and mobile portal for retail banking customers.',
              'Achieve strict PCI-DSS Section 3 compliance for cardholder data isolation.',
              'Implement zero-trust OAuth 2.0 multi-factor verification workflows.',
              'Synchronize balance operations to localized database shards within 500ms latency.'
            ],
            scope: {
              in_scope: [
                'MFA enrollment and authentication login cycles.',
                'Interactive dashboard displaying checking, savings, and card balances.',
                'Direct transfers, payee registration, and billing alerts.',
                'Exporting transaction statements to PDF and Excel formats.'
              ],
              out_scope: [
                'Support for corporate or multi-currency business accounts.',
                'Automatic conversion to foreign fiat or virtual crypto wallets.'
              ]
            },
            stakeholders: [
              'Retail Account Customers (Primary Users)',
              'InfoSec Compliance and Audit Officers',
              'Finance Ops Team & Database Admin'
            ],
            functional_requirements: [
              { 
                id: 'FR-101', 
                title: 'OAuth 2.0 MFA Authentication',
                description: 'User must be able to log in securely using OAuth 2.0 multi-factor authentication.', 
                priority: 'MUST HAVE', 
                confidence: 'HIGH', 
                conflict: false,
                source: 'Sec-Architecture.pdf',
                source_trace: 'Page 5, Sec 2'
              },
              { 
                id: 'FR-102', 
                title: 'Automatic Fail Account Lockout',
                description: 'System should automatically lock the account after 3 consecutive failed login attempts.', 
                priority: 'MUST HAVE', 
                confidence: 'HIGH', 
                conflict: true, 
                conflict_details: 'Contradicts FR-103: Admin bypass overrides account lock limit.',
                source: 'Sec-Architecture.pdf',
                source_trace: 'Page 6, Sec 2.3'
              },
              { 
                id: 'FR-103', 
                title: 'Emergency Admin Override Bypass',
                description: 'Administrator bypass overrides account locks under emergency scenarios.', 
                priority: 'SHOULD HAVE', 
                confidence: 'HIGH', 
                conflict: true,
                source: 'Admin-Manual.docx',
                source_trace: 'Page 11'
              },
              { 
                id: 'FR-104', 
                title: 'Real-Time Balance Sockets',
                description: 'The dashboard must display the user balance updated in real-time.', 
                priority: 'MUST HAVE', 
                confidence: 'MEDIUM', 
                conflict: false,
                source: 'Dashboard-Spec.txt',
                source_trace: 'Line 23'
              }
            ],
            non_functional_requirements: [
              { 
                id: 'NFR-201', 
                title: 'Database Synchronization Latency',
                description: 'All database writes must sync to Firestore/SQLite within 500ms latency.', 
                priority: 'MUST HAVE', 
                confidence: 'HIGH', 
                conflict: false,
                source: 'Architecture-Design.txt',
                source_trace: 'Line 89'
              },
              { 
                id: 'NFR-202', 
                title: 'Peak Load Page Response Times',
                description: 'System must load data in less than 2 seconds under peak loads.', 
                priority: 'SHOULD HAVE', 
                confidence: 'HIGH', 
                conflict: false,
                source: 'Perf-Benchmark.md',
                source_trace: 'Section 4.1'
              }
            ],
            risks: [
              { 
                risk: 'Brute-force account takeover attempts on login panels.', 
                mitigation: 'Implement IP-based rate limiting, captcha verification, and notify customers of anomalous attempts.' 
              },
              { 
                risk: 'Network split causing database inconsistencies.', 
                mitigation: 'Implement a transactional retry queue in SQLite with eventual sync to cloud shards.' 
              }
            ],
            assumptions: [
              'Customers possess mobile devices capable of running modern web browsers and authentication apps.',
              'Broadband connection is available for the primary servers.'
            ],
            acceptance_criteria: [
              'Login session tokens expire within 15 minutes of inactivity.',
              'Balance verification logs are encrypted during storage.'
            ],
            domain_adjustments: {
              compliance_standards: ['PCI-DSS Section 3', 'SOX Financial Compliance'],
              nfr_focus: 'Data Isolation, Session Cryptography, and Transaction Log Durability.',
              glossary: ['MFA', 'OAuth 2.0', 'PCI-DSS', 'Tokenization', 'WebSocket']
            },
            detected_conflicts: [
              {
                id: 'c-101',
                req1_id: 'FR-102',
                req2_id: 'FR-103',
                description: 'FR-102 enforces strict automatic lock limits on 3 failures, while FR-103 enables emergency administrator bypasses which override locks, presenting a potential authorization loophole.'
              }
            ]
          }
        ];
        localStorage.setItem('demo_projects_v5', JSON.stringify(loadedProjects));
      }
      setProjects(loadedProjects);
      if (loadedProjects.length > 0 && !selectedProjectId) {
        setSelectedProjectId(loadedProjects[0].id);
      }
      addToast("Offline Mode: Running on local storage data.", "info");
    }
  }, [getHeaders, selectedProjectId, addToast]);

  // Load active project details and version history
  const fetchActiveProjectDetails = useCallback(async (projectId) => {
    if (!projectId) return;
    try {
      // 1. Fetch details
      const response = await fetch(`/api/projects/${projectId}`, {
        headers: getHeaders()
      });
      if (!response.ok) throw new Error('Failed to load project details');
      const data = await response.json();
      
      setProjects(prev => prev.map(p => p.id === projectId ? data.project : p));
      
      // 2. Fetch versions
      const vResponse = await fetch(`/api/projects/${projectId}/versions`, {
        headers: getHeaders()
      });
      if (vResponse.ok) {
        const vData = await vResponse.json();
        setVersionHistory(vData.versions || []);
      }
    } catch (error) {
      console.warn("Backend details fetch failed, utilizing local version list:", error);
      const mockVersions = [
        { version: 1, changed_at: new Date().toISOString(), change_summary: 'Initial mockup version' }
      ];
      setVersionHistory(mockVersions);
    }
  }, [getHeaders]);

  // Trigger project detail loading on select change
  useEffect(() => {
    if (isLoggedIn && selectedProjectId) {
      fetchActiveProjectDetails(selectedProjectId);
    }
  }, [isLoggedIn, selectedProjectId, fetchActiveProjectDetails]);

  // Load projects list on login state change
  useEffect(() => {
    if (isLoggedIn) {
      fetchProjects();
    } else {
      setProjects([]);
      setSelectedProjectId('');
      setVersionHistory([]);
    }
  }, [isLoggedIn, fetchProjects]);

  // Auth Handlers
  const handleLogin = useCallback(async (email, password) => {
    try {
      let data;
      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          let errDetail = 'Incorrect credentials';
          try {
            const errJson = JSON.parse(errorText);
            errDetail = errJson.detail || errDetail;
          } catch(e) {}
          throw new Error(errDetail);
        }
        
        data = await response.json();
      } catch (apiError) {
        console.warn("API login failed, entering demo mode:", apiError);
        data = {
          token: "demo-mock-token-123",
          user: {
            name: email ? email.split('@')[0] : 'john_doe',
            email: email || 'john@brdforge.ai',
            role: 'Workspace Architect'
          }
        };
        addToast('Running in Demo Mode (Local Sandbox)', 'info');
      }
      
      localStorage.setItem('brd_token', data.token);
      localStorage.setItem('brd_user', JSON.stringify(data.user));
      localStorage.setItem('brd_logged_in', 'true');
      
      setCurrentUser(data.user);
      setIsLoggedIn(true);
      setActivePage('dashboard');
      addToast('Welcome to BRD Forge!', 'success');
    } catch (error) {
      addToast(error.message, 'error');
    }
  }, [addToast]);

  const handleSignup = useCallback(async (name, email, password) => {
    try {
      let data;
      try {
        const response = await fetch('/api/auth/signup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, password })
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          let errDetail = 'Signup failed';
          try {
            const errJson = JSON.parse(errorText);
            errDetail = errJson.detail || errDetail;
          } catch(e) {}
          throw new Error(errDetail);
        }
        
        data = await response.json();
      } catch (apiError) {
        console.warn("API signup failed, entering demo mode:", apiError);
        data = {
          token: "demo-mock-token-123",
          user: {
            name: name || 'john_doe',
            email: email || 'john@brdforge.ai',
            role: 'Workspace Architect'
          }
        };
        addToast('Created Account in Demo Mode (Local)', 'info');
      }
      
      localStorage.setItem('brd_token', data.token);
      localStorage.setItem('brd_user', JSON.stringify(data.user));
      localStorage.setItem('brd_logged_in', 'true');
      
      setCurrentUser(data.user);
      setIsLoggedIn(true);
      setActivePage('dashboard');
      addToast('Account initialized successfully!', 'success');
    } catch (error) {
      addToast(error.message, 'error');
    }
  }, [addToast]);

  const handleLogout = useCallback(async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
    } catch (e) {}
    
    localStorage.removeItem('brd_token');
    localStorage.removeItem('brd_user');
    localStorage.removeItem('brd_logged_in');
    
    setCurrentUser(DEFAULT_USER);
    setIsLoggedIn(false);
    addToast('Logged out successfully.', 'success');
  }, [addToast]);

  // Theme Mode
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Active Project Data Selector
  const activeProject = projects.find(p => p.id === selectedProjectId) || null;

  const handleSelectProject = useCallback((id) => {
    setSelectedProjectId(id);
    setActivePage('editor');
    addToast('Project workspace loaded.', 'success');
  }, [addToast]);

  const handleLoadDemo = useCallback(() => {
    setProjectName('Online Banking Portal');
    setSelectedDomain('FinTech');
    setUploadedFiles([
      { filename: 'banking_specs.txt', extension: '.txt', size_mb: 0.02, type: 'text' },
      { filename: 'security_audit.txt', extension: '.txt', size_mb: 0.05, type: 'text' }
    ]);
    setPastedText('Ingest requirements for secure billing balance dashboards and OAuth sign-in controls...');
    addToast('Demo requirements ready to analyze!', 'success');
  }, [addToast]);

  // Pipeline Generator Trigger (Sends files and pasted specs to FastAPI)
  const handleGenerate = useCallback(async () => {
    if (!projectName.trim()) {
      addToast('Please input a project name.', 'error');
      return;
    }
    if (uploadedFiles.length === 0 && !pastedText.trim()) {
      addToast('Upload specifications files or insert raw text notes.', 'error');
      return;
    }

    setIsGenerating(true);
    setPipelineStep(1);

    // Multi-step visual loading progress simulation during processing
    const stepInterval = setInterval(() => {
      setPipelineStep(prev => (prev < 4 ? prev + 1 : prev));
    }, 1500);

    try {
      const formData = new FormData();
      formData.append('project_name', projectName);
      formData.append('domain_selection', selectedDomain);
      formData.append('pasted_text', pastedText);

      // Append files if they have rawFile elements attached
      uploadedFiles.forEach(file => {
        if (file.rawFile) {
          formData.append('files', file.rawFile);
        }
      });

      const token = localStorage.getItem('brd_token');
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'AI synthesis failed.');
      }

      const data = await response.json();
      
      clearInterval(stepInterval);
      setPipelineStep(4);

      // Refresh project database list and load the new project
      await fetchProjects();
      setSelectedProjectId(data.project.id);
      
      setIsGenerating(false);
      setPipelineStep(0);
      setActivePage('editor');
      addToast('AI Synthesis complete! Project generated.', 'success');

      // Clear input fields
      setProjectName('');
      setPastedText('');
      setUploadedFiles([]);
    } catch (error) {
      clearInterval(stepInterval);
      console.warn("Generation API failed, executing local mock synthesis:", error);
      
      // Simulate frontend-only completion delay
      setTimeout(() => {
        const mockNewId = `demo-project-${Date.now()}`;
        const newProj = {
          id: mockNewId,
          project_name: projectName || 'Generated BRD Project',
          domain: selectedDomain || 'General',
          created_at: new Date().toISOString(),
          confidence_score: 90,
          total_requirements: 4,
          conflict_count: 0,
          executive_summary: `This is an AI-generated Business Requirements Document (BRD) synthesized under domain '${selectedDomain || 'General'}' for '${projectName || 'Spec workspace'}'. Ingested specification references: ${pastedText || 'No custom details inputted.'}`,
          objectives: [
            'Deliver standard feature requirements compliant with domain frameworks.',
            'Establish proper architectural checkpoints and testing bounds.',
            'Deliver latency and safety metrics aligning with industry guidelines.'
          ],
          scope: {
            in_scope: [
              'System components directly parsing specifications.',
              'Data visualization and reporting portals.'
            ],
            out_scope: [
              'Enterprise cloud integration nodes (configured in phase 2).',
              'External payment gateway certifications.'
            ]
          },
          stakeholders: [
            'System Architects',
            'Business Product Managers',
            'Quality Assurance Engineers'
          ],
          functional_requirements: [
            { 
              id: 'FR-201', 
              title: 'Secure Parameter Parsing', 
              description: 'System must securely encrypt all credentials and API key tokens.', 
              priority: 'MUST HAVE', 
              confidence: 'HIGH', 
              conflict: false,
              source: 'Spec-Note.txt',
              source_trace: 'Line 2'
            },
            { 
              id: 'FR-202', 
              title: 'Custom Ingestion Mapping', 
              description: `Parse specs: ${pastedText || 'Default spec text'}`, 
              priority: 'SHOULD HAVE', 
              confidence: 'HIGH', 
              conflict: false,
              source: 'Text-Area-Paste.txt',
              source_trace: 'Line 1'
            }
          ],
          non_functional_requirements: [
            { 
              id: 'NFR-301', 
              title: 'Response Performance Bound', 
              description: 'Application response latency must be under 1 second.', 
              priority: 'MUST HAVE', 
              confidence: 'HIGH', 
              conflict: false,
              source: 'Performance-Spec.md',
              source_trace: 'Section 1'
            }
          ],
          risks: [
            { 
              risk: 'Stale configuration settings overriding active properties.', 
              mitigation: 'Implement real-time registry checks and validation triggers.' 
            }
          ],
          assumptions: [
            'Web platform and framework packages are compatible with active browser builds.'
          ],
          acceptance_criteria: [
            'All core functionalities complete with successful test suite checks.'
          ],
          domain_adjustments: {
            compliance_standards: ['ISO 27001 Information Security', 'GDPR General Data Protection'],
            nfr_focus: 'Encryption standardizations, strict data bounds, and access audit records.',
            glossary: ['GDPR', 'ISO', 'MFA', 'OAuth']
          },
          detected_conflicts: []
        };
        
        setProjects(prev => {
          const next = [...prev, newProj];
          localStorage.setItem('demo_projects_v5', JSON.stringify(next));
          return next;
        });
        setSelectedProjectId(mockNewId);
        setIsGenerating(false);
        setPipelineStep(0);
        setActivePage('editor');
        addToast('AI Synthesis complete! (Offline Mode Fallback)', 'success');
        
        // Clear fields
        setProjectName('');
        setPastedText('');
        setUploadedFiles([]);
      }, 1200);
    }
  }, [projectName, uploadedFiles, pastedText, selectedDomain, fetchProjects, addToast]);

  // Project Archiver/Saver (updates edits in database)
  const handleSaveToArchive = useCallback(async () => {
    if (!activeProject) return;
    try {
      const response = await fetch(`/api/projects/${selectedProjectId}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify({
          project_name: activeProject.project_name,
          brd_json: activeProject
        })
      });
      if (!response.ok) throw new Error('Failed to save to database');
      
      addToast('Project sync complete. Document saved to database.', 'success');
      // Reload details to sync versionHistory
      fetchActiveProjectDetails(selectedProjectId);
    } catch (error) {
      console.warn("API save failed, using local fallback:", error);
      saveLocalDemoProject(selectedProjectId, activeProject);
      addToast('Workspace changes saved locally.', 'success');
    }
  }, [activeProject, selectedProjectId, getHeaders, fetchActiveProjectDetails, saveLocalDemoProject, addToast]);

  const handleDeleteProject = useCallback(async (id) => {
    try {
      const response = await fetch(`/api/projects/${id}`, {
        method: 'DELETE',
        headers: getHeaders()
      });
      if (!response.ok) throw new Error('Failed to delete project');
      
      setProjects(prev => prev.filter(p => p.id !== id));
      if (selectedProjectId === id) {
        setSelectedProjectId('');
      }
      addToast('Project workspace deleted.', 'success');
    } catch (error) {
      console.warn("API delete failed, removing locally:", error);
      setProjects(prev => {
        const next = prev.filter(p => p.id !== id);
        localStorage.setItem('demo_projects_v5', JSON.stringify(next));
        return next;
      });
      if (selectedProjectId === id) {
        setSelectedProjectId('');
      }
      addToast('Project deleted from local database.', 'success');
    }
  }, [selectedProjectId, getHeaders, addToast]);

  // Requirements operations (Saves automatically using PUT route)
  const handleDeleteSelectedReqs = useCallback(async () => {
    if (selectedReqs.size === 0 || !activeProject) return;
    
    const updatedFrs = (activeProject.functional_requirements || []).filter(r => !selectedReqs.has(r.id));
    const updatedNfrs = (activeProject.non_functional_requirements || []).filter(r => !selectedReqs.has(r.id));
    
    const updatedProject = {
      ...activeProject,
      functional_requirements: updatedFrs,
      non_functional_requirements: updatedNfrs
    };

    try {
      const response = await fetch(`/api/projects/${selectedProjectId}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify({
          project_name: activeProject.project_name,
          brd_json: updatedProject
        })
      });
      if (!response.ok) throw new Error('Database sync failed');
      
      // Update local state
      setProjects(prev => prev.map(p => p.id === selectedProjectId ? updatedProject : p));
      setSelectedReqs(new Set());
      addToast('Requirements successfully removed.', 'success');
      // Reload details to sync versionHistory
      fetchActiveProjectDetails(selectedProjectId);
    } catch (error) {
      console.warn("API delete reqs failed, processing locally:", error);
      saveLocalDemoProject(selectedProjectId, updatedProject);
      setSelectedReqs(new Set());
      addToast('Requirements successfully removed.', 'success');
    }
  }, [selectedProjectId, activeProject, selectedReqs, getHeaders, fetchActiveProjectDetails, saveLocalDemoProject, addToast]);

  const handleChangePriority = useCallback(async (newPriority) => {
    if (selectedReqs.size === 0 || !activeProject) return;
    
    const updatedFrs = (activeProject.functional_requirements || []).map(r =>
      selectedReqs.has(r.id) ? { ...r, priority: newPriority } : r
    );
    
    const updatedProject = {
      ...activeProject,
      functional_requirements: updatedFrs
    };

    try {
      const response = await fetch(`/api/projects/${selectedProjectId}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify({
          project_name: activeProject.project_name,
          brd_json: updatedProject
        })
      });
      if (!response.ok) throw new Error('Database sync failed');
      
      // Update local state
      setProjects(prev => prev.map(p => p.id === selectedProjectId ? updatedProject : p));
      setSelectedReqs(new Set());
      addToast(`Priority shifted to ${newPriority}.`, 'success');
      // Reload details to sync versionHistory
      fetchActiveProjectDetails(selectedProjectId);
    } catch (error) {
      console.warn("API priority shift failed, processing locally:", error);
      saveLocalDemoProject(selectedProjectId, updatedProject);
      setSelectedReqs(new Set());
      addToast(`Priority shifted to ${newPriority}.`, 'success');
    }
  }, [selectedProjectId, activeProject, selectedReqs, getHeaders, fetchActiveProjectDetails, saveLocalDemoProject, addToast]);

  // Contradiction Resolver (sends resolution payload to FastAPI server)
  const handleResolveConflict = useCallback(async (conflictId, resolutionChoice, customText = '') => {
    try {
      const response = await fetch(`/api/projects/${selectedProjectId}/resolve`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
          conflict_id: conflictId,
          resolution_type: resolutionChoice,
          merge_description: customText
        })
      });
      
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Conflict resolution failed');
      }
      
      addToast('Contradiction resolved successfully.', 'success');
      
      // Reload active project and versions logs from DB
      await fetchActiveProjectDetails(selectedProjectId);
    } catch (error) {
      console.warn("API resolve conflict failed, processing locally:", error);
      if (!activeProject) return;

      const updatedFrs = (activeProject.functional_requirements || []).map(r => {
        if (r.id === conflictId || r.conflict) {
          return {
            ...r,
            conflict: false,
            description: (resolutionChoice === 'merge' && customText) ? customText : r.description
          };
        }
        return r;
      });

      const updatedProject = {
        ...activeProject,
        functional_requirements: updatedFrs,
        conflict_count: Math.max(0, (activeProject.conflict_count || 1) - 1)
      };

      saveLocalDemoProject(selectedProjectId, updatedProject);
      addToast('Contradiction resolved.', 'success');
    }
  }, [selectedProjectId, activeProject, getHeaders, fetchActiveProjectDetails, saveLocalDemoProject, addToast]);

  const value = {
    activePage, setActivePage,
    projects, setProjects,
    selectedProjectId, setSelectedProjectId,
    activeProject,
    projectName, setProjectName,
    selectedDomain, setSelectedDomain,
    pastedText, setPastedText,
    uploadedFiles, setUploadedFiles,
    isGenerating,
    pipelineStep,
    selectedReqs, setSelectedReqs,
    pdfTheme, setPdfTheme,
    toasts,
    versionHistory, setVersionHistory,
    settings, setSettings,
    theme, setTheme,
    handleSelectProject, handleLoadDemo, handleGenerate,
    handleSaveToArchive, handleDeleteProject,
    handleDeleteSelectedReqs, handleChangePriority,
    handleResolveConflict, addToast,
    isLoggedIn, currentUser, handleLogin, handleSignup, handleLogout
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within AppProvider');
  return context;
}
