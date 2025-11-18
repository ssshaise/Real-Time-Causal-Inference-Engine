// src/frontend/src/components/WorkflowAnimation.jsx
import { motion } from "framer-motion";
import { Database, Network, Cpu } from "lucide-react";

export default function WorkflowAnimation() {
  return (
    <div className="relative w-full max-w-7xl mx-auto h-80 flex items-center justify-center gap-4 md:gap-12 px-4">
      
      {/* 1. Left Card: Raw Data */}
      <motion.div 
        initial={{ opacity: 0, x: -50 }}
        whileInView={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
        className="z-10 bg-white dark:bg-[#0f172a] p-8 rounded-3xl shadow-2xl border border-gray-100 dark:border-gray-700 w-72 relative overflow-hidden group"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800/50 dark:to-gray-900/50 opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div className="relative z-10 text-center">
            <div className="mx-auto h-14 w-14 bg-blue-100 dark:bg-blue-900/30 rounded-2xl mb-4 flex items-center justify-center text-blue-600 dark:text-blue-400">
                <Database size={28} />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">Observational Data</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">CSV / SQL Ingestion</p>
        </div>
      </motion.div>

      {/* Pipe 1 */}
      <div className="flex-1 h-[2px] bg-gray-200 dark:bg-gray-800 relative overflow-hidden max-w-[100px]">
         <motion.div 
            className="absolute top-0 left-0 h-full w-1/2 bg-gradient-to-r from-transparent via-brand-500 to-transparent"
            animate={{ x: ["-100%", "200%"] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
         />
      </div>

      {/* 2. Middle Card: Discovery Engine (NEW) */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.8 }}
        whileInView={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="z-10 bg-white dark:bg-[#0f172a] p-8 rounded-full shadow-2xl border border-brand-500/30 w-40 h-40 flex flex-col items-center justify-center relative"
      >
        <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-brand-500 animate-spin"></div>
         <Cpu size={32} className="text-brand-500 mb-2" />
         <span className="text-xs font-bold text-gray-500 dark:text-gray-400">PC ALGO</span>
      </motion.div>

      {/* Pipe 2 */}
      <div className="flex-1 h-[2px] bg-gray-200 dark:bg-gray-800 relative overflow-hidden max-w-[100px]">
         <motion.div 
            className="absolute top-0 left-0 h-full w-1/2 bg-gradient-to-r from-transparent via-purple-500 to-transparent"
            animate={{ x: ["-100%", "200%"] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "linear", delay: 0.75 }}
         />
      </div>

      {/* 3. Right Card: Causal Graph */}
      <motion.div 
        initial={{ opacity: 0, x: 50 }}
        whileInView={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="z-10 bg-white dark:bg-[#0f172a] p-8 rounded-3xl shadow-2xl border border-purple-100 dark:border-purple-900/50 w-72 relative overflow-hidden"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-brand-50/50 to-purple-50/50 dark:from-brand-900/10 dark:to-purple-900/10"></div>
        <div className="relative z-10 text-center">
            <div className="mx-auto h-14 w-14 bg-purple-100 dark:bg-purple-900/30 rounded-2xl mb-4 flex items-center justify-center text-purple-600 dark:text-purple-400">
                <Network size={28} />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">Directed Graph</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Recovered Structure</p>
        </div>
      </motion.div>

    </div>
  );
}