// src/frontend/src/pages/Architecture.jsx
import { motion } from 'framer-motion';
import { ArrowLeft, Server, Database, Cpu, Layout } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Architecture() {
  const navigate = useNavigate();

  const steps = [
    { title: "Frontend Layer", icon: <Layout size={32}/>, desc: "React + Vite + Tailwind. Sends user interventions to API.", color: "bg-blue-500" },
    { title: "API Gateway", icon: <Server size={32}/>, desc: "FastAPI (Python). Validates data and routes traffic.", color: "bg-green-500" },
    { title: "Causal Core", icon: <Cpu size={32}/>, desc: "PyTorch Neural Networks + PC Algorithm + Do-Calculus Engine.", color: "bg-purple-500" },
    { title: "Persistence", icon: <Database size={32}/>, desc: "DuckDB (SQL) for data & MLflow for model versioning.", color: "bg-orange-500" }
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8">
      <button onClick={() => navigate('/')} className="flex items-center gap-2 text-gray-400 hover:text-white mb-12 transition">
        <ArrowLeft size={20} /> Back to Home
      </button>

      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-5xl font-bold mb-16">System <span className="text-brand-500">Architecture</span></h1>
        
        <div className="relative">
          {/* Central Line */}
          <div className="absolute left-1/2 top-0 bottom-0 w-1 bg-gray-800 -translate-x-1/2 z-0 hidden md:block"></div>

          <div className="space-y-12 relative z-10">
            {steps.map((s, i) => (
              <motion.div 
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.2 }}
                className="flex flex-col md:flex-row items-center gap-8 group"
              >
                {/* Content Card */}
                <div className={`flex-1 p-6 rounded-2xl border border-gray-800 bg-[#111] hover:border-gray-600 transition-all ${i % 2 === 0 ? 'md:text-right' : 'md:order-2 md:text-left'}`}>
                  <h3 className="text-2xl font-bold mb-2">{s.title}</h3>
                  <p className="text-gray-400">{s.desc}</p>
                </div>

                {/* Center Icon */}
                <div className={`w-16 h-16 rounded-full flex items-center justify-center shadow-lg shadow-white/5 ${s.color} shrink-0 z-10`}>
                  {s.icon}
                </div>

                {/* Spacer for layout balance */}
                <div className="flex-1 hidden md:block"></div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}