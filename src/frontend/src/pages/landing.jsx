// src/frontend/src/pages/Landing.jsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, GitCommit, Cpu, Database, Github, Linkedin, Mail, LogOut, User, LayoutDashboard } from 'lucide-react';
import WorkflowAnimation from '../components/WorkflowAnimation';
import FeatureSlider from '../components/FeatureSlider';

export default function Landing() {
  const navigate = useNavigate();
  
  // AUTH STATE
  const [userEmail, setUserEmail] = useState(null);
  const [userName, setUserName] = useState("");

  useEffect(() => {
    // 1. Force Dark Mode
    document.documentElement.classList.add('dark');
    
    // 2. Check Login Status
    const email = localStorage.getItem('user_email');
    if (email) {
        setUserEmail(email);
        // Extract name from email (e.g., "ruchir" from "ruchir@gmail.com") and Capitalize
        const namePart = email.split('@')[0];
        setUserName(namePart.charAt(0).toUpperCase() + namePart.slice(1));
    }
  }, []);

  const handleLogout = () => {
      localStorage.removeItem('user_email');
      setUserEmail(null);
      setUserName("");
      navigate('/'); // Stay on home but reset state
  };

  const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-[#020617] text-white font-sans selection:bg-brand-500 selection:text-white overflow-hidden relative">
      
      {/* --- BACKGROUND --- */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-[#050505]"></div>
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-[#00e5ff] blur-[100px] opacity-40 animate-pulse"></div>
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-[#d946ef] blur-[100px] opacity-40 animate-pulse delay-1000"></div>
        <div className="absolute top-[20%] left-[20%] w-[60%] h-[60%] bg-[radial-gradient(circle,rgba(124,58,237,0.15)_0%,transparent_70%)] blur-[80px]"></div>
      </div>

      <div className="relative z-10">
        
        {/* --- NAVBAR WITH AUTH LOGIC --- */}
        <nav className="fixed w-full top-0 z-50 bg-black/10 backdrop-blur-xl border-b border-white/5 px-6 py-4">
           <div className="max-w-7xl mx-auto flex justify-between items-center">
              <div className="text-2xl font-bold flex items-center gap-2 tracking-tighter cursor-pointer" onClick={() => window.scrollTo(0,0)}>
                <div className="w-8 h-8 bg-brand-500 rounded-lg flex items-center justify-center shadow-[0_0_15px_rgba(139,92,246,0.5)]">
                  <GitCommit className="text-white w-5 h-5" />
                </div>
                RCIE <span className="text-brand-500">Engine</span>
              </div>
              
              <div className="flex items-center gap-6">
                <div className="hidden md:flex gap-6 text-sm font-semibold text-gray-300">
                  <button onClick={() => scrollToSection('about')} className="hover:text-brand-500 transition">About</button>
                  <button onClick={() => scrollToSection('contact')} className="hover:text-brand-500 transition">Contact</button>
                </div>
                
                {/* AUTH SWITCHER */}
                {userEmail ? (
                    // IF LOGGED IN: Show Name + Dashboard + Logout
                    <div className="flex items-center gap-4 pl-4 border-l border-white/10">
                        <div className="text-right hidden sm:block">
                            <p className="text-xs text-gray-400">Welcome back,</p>
                            <p className="text-sm font-bold text-brand-400">{userName}</p>
                        </div>
                        <button 
                            onClick={() => navigate('/dashboard')} 
                            className="p-2 bg-brand-600 hover:bg-brand-500 rounded-full text-white transition shadow-lg shadow-brand-500/20"
                            title="Go to Dashboard"
                        >
                            <LayoutDashboard size={20} />
                        </button>
                        <button 
                            onClick={handleLogout} 
                            className="p-2 bg-white/5 hover:bg-red-500/20 hover:text-red-500 rounded-full text-gray-400 transition"
                            title="Logout"
                        >
                            <LogOut size={20} />
                        </button>
                    </div>
                ) : (
                    // IF LOGGED OUT: Show Login Button
                    <button onClick={() => navigate('/login')} className="bg-brand-600 hover:bg-brand-500 text-white px-5 py-2.5 rounded-full font-bold text-sm transition-all shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_30px_rgba(139,92,246,0.5)]">
                      Login
                    </button>
                )}
              </div>
           </div>
        </nav>

        <header className="pt-40 pb-32 px-4 text-center max-w-6xl mx-auto">
           <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-brand-500/10 text-brand-300 font-medium text-sm mb-8 border border-brand-500/20 backdrop-blur-md">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-500"></span>
              </span>
              v1.0 Research-Grade System Online
            </motion.div>

           <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-5xl md:text-8xl font-extrabold leading-tight tracking-tight mb-8 text-white drop-shadow-2xl">
              Don't Just Predict.<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00e5ff] to-[#d946ef]">Understand Why.</span>
           </motion.h1>

           <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }} className="text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed mb-12">
              The first real-time Causal Inference Engine. Move beyond correlation. 
              Discover hidden structures, train structural models, and simulate future outcomes without the risk.
           </motion.p>

           <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.4 }} className="flex flex-col sm:flex-row gap-4 justify-center mb-24">
              {/* SMART BUTTON: Changes based on login status */}
              <button 
                onClick={() => navigate(userEmail ? '/dashboard' : '/login')} 
                className="group bg-brand-600 hover:bg-brand-500 text-white px-8 py-4 rounded-full font-bold text-lg flex items-center justify-center gap-3 transition-all shadow-[0_0_20px_rgba(139,92,246,0.4)] hover:shadow-[0_0_40px_rgba(139,92,246,0.6)] hover:-translate-y-1"
              >
                {userEmail ? "Open Dashboard" : "Launch Discovery"} 
                <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform"/>
              </button>
              
              <button onClick={() => navigate('/architecture')} className="bg-white/5 backdrop-blur-sm border border-white/10 text-white px-8 py-4 rounded-full font-bold text-lg hover:bg-white/10 transition-all hover:-translate-y-1">
                View Architecture
              </button>
           </motion.div>

           <WorkflowAnimation />
        </header>

        <section id="about" className="py-32 bg-black/20 border-y border-white/5 relative backdrop-blur-sm">
             <div className="max-w-7xl mx-auto px-6">
              <div className="grid lg:grid-cols-2 gap-20 items-center">
                <div className="order-2 lg:order-1">
                  <h2 className="text-5xl font-bold mb-8 leading-tight text-white">Why <span className="text-brand-500">Causal Inference?</span></h2>
                  <div className="prose prose-lg dark:prose-invert text-gray-400">
                    <p className="mb-6">Standard Machine Learning models are effectively "Pattern Spotters." They know that <em>"When X happens, Y usually happens."</em> This is correlation. It works for prediction, but fails at decision-making.</p>
                    <p className="mb-6"><strong>The Problem:</strong> If you ask a standard model, <em>"What happens if I change X?"</em>, it has to guess because it has never seen that specific intervention before.</p>
                    <p className="mb-8"><strong>The RCIE Solution:</strong> Our engine builds a <strong>Logic Map</strong> of the business mechanism itself. By recovering the Causal DAG, we mathematically separate "Correlation" from "Causation."</p>
                  </div>
                </div>
                <div className="order-1 lg:order-2 bg-gradient-to-br from-white/5 to-white/0 p-2 rounded-[3rem] border border-white/10 relative h-full flex items-center backdrop-blur-md shadow-2xl">
                   <FeatureSlider />
                </div>
              </div>
            </div>
        </section>

        <footer id="contact" className="bg-black/40 py-20 border-t border-white/5 backdrop-blur-md">
            <div className="max-w-7xl mx-auto px-6 text-center">
              <h2 className="text-3xl font-bold mb-8">Built for Research. Engineered for Speed.</h2>
              <p className="text-gray-400 max-w-2xl mx-auto mb-12">
                This project was built using React, FastAPI, PyTorch, and Google Gemini. 
                It serves as a proof-of-concept for next-generation Decision Support Systems.
              </p>
              <div className="flex justify-center gap-6 mb-12">
                <a href="https://github.com/YOUR_USERNAME" target="_blank" rel="noreferrer" className="p-3 bg-white/5 rounded-full hover:bg-brand-500 hover:text-white transition shadow-sm"><Github size={24}/></a>
                <a href="https://linkedin.com/in/YOUR_USERNAME" target="_blank" rel="noreferrer" className="p-3 bg-white/5 rounded-full hover:bg-brand-500 hover:text-white transition shadow-sm"><Linkedin size={24}/></a>
                <a href="mailto:your.email@example.com" className="p-3 bg-white/5 rounded-full hover:bg-brand-500 hover:text-white transition shadow-sm"><Mail size={24}/></a>
              </div>
              <div className="text-sm text-gray-500 border-t border-white/10 pt-8">
                © 2025 RCIE Platform. Open Source Research Project.
              </div>
            </div>
        </footer>
      </div>
    </div>
  );
}