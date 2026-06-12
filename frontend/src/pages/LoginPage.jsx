import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useApp } from '../context/AppContext';
import { Flame, Mail, Lock, User, ArrowRight, Eye, EyeOff } from 'lucide-react';

export default function LoginPage() {
  const { handleLogin, handleSignup } = useApp();
  const [isSignUp, setIsSignUp] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isSignUp) {
      handleSignup(name || 'User', email || 'user@brdforge.ai', password);
    } else {
      handleLogin(email || 'john@brdforge.ai', password, name);
    }
  };

  return (
    <div data-theme="dark" className="min-h-screen w-full flex items-center justify-center bg-[#09090b] text-zinc-100 relative overflow-hidden grid-bg dark">
      {/* Ambient glows */}
      <div className="absolute top-[-15%] left-[-8%] w-[45%] h-[45%] rounded-full bg-blue-500/15 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-5%] w-[35%] h-[35%] rounded-full bg-cyan-500/12 blur-[100px] pointer-events-none" />
      <div className="absolute top-[50%] left-[60%] w-[20%] h-[20%] rounded-full bg-emerald-500/8 blur-[80px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
        className="w-full max-w-md mx-4 relative z-10"
      >
        {/* Brand header */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center shadow-xl shadow-blue-500/20 mx-auto mb-4">
            <Flame size={24} className="text-white" />
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-zinc-50">
            BRD Forge
          </h1>
          <p className="text-sm text-zinc-400 mt-1 font-medium">
            AI-Powered Requirements Intelligence
          </p>
        </div>

        {/* Auth card */}
        <motion.div layout className="premium-card p-8">
          {/* Tab switcher */}
          <div className="flex mb-6 rounded-xl bg-zinc-800/60 p-1">
            <button
              onClick={() => setIsSignUp(false)}
              className={`flex-1 py-2.5 rounded-lg text-xs font-bold tracking-wide transition-all duration-200 cursor-pointer ${
                !isSignUp
                  ? 'bg-zinc-900 text-zinc-50 shadow-sm'
                  : 'text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setIsSignUp(true)}
              className={`flex-1 py-2.5 rounded-lg text-xs font-bold tracking-wide transition-all duration-200 cursor-pointer ${
                isSignUp
                  ? 'bg-zinc-900 text-zinc-50 shadow-sm'
                  : 'text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200'
              }`}
            >
              Create Account
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <AnimatePresence mode="wait">
              {isSignUp && (
                <motion.div
                  key="name"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <label className="block text-[10px] font-bold text-zinc-400 uppercase tracking-widest mb-1.5">Full Name</label>
                  <div className="relative">
                    <User size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-400" />
                    <input
                      type="text"
                      value={name}
                      onChange={e => setName(e.target.value)}
                      placeholder="John Doe"
                      className="w-full text-sm bg-zinc-900/80 rounded-xl py-3 pl-10 pr-4 text-zinc-100 focus:outline-none focus:ring-2 focus:ring-blue-500/30 placeholder-zinc-500 font-medium border border-zinc-800"
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div>
              <label className="block text-[10px] font-bold text-zinc-400 uppercase tracking-widest mb-1.5">Email Address</label>
              <div className="relative">
                <Mail size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-400" />
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="you@company.com"
                  className="w-full text-sm bg-zinc-900/80 rounded-xl py-3 pl-10 pr-4 text-zinc-100 focus:outline-none focus:ring-2 focus:ring-blue-500/30 placeholder-zinc-500 font-medium border border-zinc-800"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] font-bold text-zinc-400 uppercase tracking-widest mb-1.5">Password</label>
              <div className="relative">
                <Lock size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full text-sm bg-zinc-900/80 rounded-xl py-3 pl-10 pr-12 text-zinc-100 focus:outline-none focus:ring-2 focus:ring-blue-500/30 placeholder-zinc-500 font-medium border border-zinc-800"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-300 cursor-pointer"
                >
                  {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              </div>
            </div>

            {!isSignUp && (
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-xs text-zinc-400 cursor-pointer">
                  <input type="checkbox" className="w-3.5 h-3.5 rounded text-blue-600 bg-zinc-900 border-zinc-800" />
                  <span>Remember me</span>
                </label>
                <button type="button" className="text-xs font-semibold text-blue-400 hover:text-blue-300 cursor-pointer">
                  Forgot password?
                </button>
              </div>
            )}

            <button
              type="submit"
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white text-sm font-bold shadow-lg shadow-blue-500/20 hover:shadow-blue-500/30 active:scale-[0.98] transition-all cursor-pointer mt-2"
            >
              {isSignUp ? 'Create Account' : 'Sign In to Forge'}
              <ArrowRight size={14} />
            </button>
          </form>

          {/* Social divider */}
          <div className="flex items-center gap-4 my-5">
            <div className="flex-1 h-px bg-zinc-800" />
            <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">or</span>
            <div className="flex-1 h-px bg-zinc-800" />
          </div>

          <button
            onClick={() => handleLogin('user@google.com', '', 'Google User')}
            className="w-full flex items-center justify-center gap-3 py-3 rounded-xl bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 hover:border-zinc-700/80 text-sm font-bold text-zinc-200 hover:text-white transition-all duration-200 active:scale-[0.98] cursor-pointer shadow-md shadow-black/10"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="flex-shrink-0">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4" />
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18A10.96 10.96 0 001 12c0 1.77.42 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
            </svg>
            <span>Continue with Google</span>
          </button>
        </motion.div>

        {/* Footer */}
        <p className="text-center text-[10px] text-zinc-500 mt-6 font-medium">
          By continuing, you agree to BRD Forge's Terms of Service and Privacy Policy
        </p>
      </motion.div>
    </div>
  );
}
