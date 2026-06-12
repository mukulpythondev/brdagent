import { AnimatePresence, motion } from 'framer-motion';
import { useApp } from '../context/AppContext';
import { CheckCircle, XCircle } from 'lucide-react';

export default function ToastContainer() {
  const { toasts } = useApp();

  return (
    <div style={{ position: 'fixed', bottom: 24, right: 24, zIndex: 1000, display: 'flex', flexDirection: 'column', gap: 8 }}>
      <AnimatePresence>
        {toasts.map(toast => (
          <motion.div
            key={toast.id}
            className={`toast ${toast.type}`}
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.25 }}
          >
            {toast.type === 'success' ? (
              <CheckCircle size={16} style={{ color: 'var(--color-success)' }} />
            ) : (
              <XCircle size={16} style={{ color: 'var(--color-danger)' }} />
            )}
            {toast.message}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
