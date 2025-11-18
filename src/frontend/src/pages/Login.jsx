// src/frontend/src/pages/Login.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, KeyRound, Mail, User, Lock } from 'lucide-react';
import { api } from '../api';

export default function Login() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ email: '', password: '', name: '' });
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
        if (isLogin) {
            const res = await api.login(formData.email, formData.password);
            if (res.status === 'success') {
                localStorage.setItem('user_email', formData.email); // Simple session
                navigate('/dashboard');
            }
        } else {
            const res = await api.signup(formData.email, formData.password, formData.name);
            if (res.status === 'success') {
                setIsLogin(true); // Switch to login after signup
                alert("Account created! Please login.");
            }
        }
    } catch (err) {
        setError(err.response?.data?.detail || "Authentication failed");
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Glows */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
         <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-brand-600/20 rounded-full blur-[120px]"></div>
         <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-purple-600/20 rounded-full blur-[120px]"></div>
      </div>

      <div className="w-full max-w-md relative z-10">
        <button onClick={() => navigate('/')} className="flex items-center gap-2 text-gray-400 hover:text-white mb-8 transition">
            <ArrowLeft size={20} /> Back to Home
        </button>

        <div className="bg-[#161616] border border-white/10 p-8 rounded-3xl shadow-2xl backdrop-blur-xl">
           <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-white mb-2">{isLogin ? 'Welcome Back' : 'Join the Future'}</h2>
              <p className="text-gray-400">{isLogin ? 'Access your Causal Engine' : 'Create your research account'}</p>
           </div>

           <form onSubmit={handleSubmit} className="space-y-4">
              {!isLogin && (
                 <div className="relative">
                    <User className="absolute left-4 top-3.5 text-gray-500" size={20} />
                    <input 
                      type="text" placeholder="Full Name" required
                      className="w-full bg-black/20 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white focus:border-brand-500 focus:ring-1 focus:ring-brand-500 outline-none transition"
                      onChange={e => setFormData({...formData, name: e.target.value})}
                    />
                 </div>
              )}
              <div className="relative">
                 <Mail className="absolute left-4 top-3.5 text-gray-500" size={20} />
                 <input 
                    type="email" placeholder="Email Address" required
                    className="w-full bg-black/20 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white focus:border-brand-500 focus:ring-1 focus:ring-brand-500 outline-none transition"
                    onChange={e => setFormData({...formData, email: e.target.value})}
                 />
              </div>
              <div className="relative">
                 <Lock className="absolute left-4 top-3.5 text-gray-500" size={20} />
                 <input 
                    type="password" placeholder="Password" required
                    className="w-full bg-black/20 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white focus:border-brand-500 focus:ring-1 focus:ring-brand-500 outline-none transition"
                    onChange={e => setFormData({...formData, password: e.target.value})}
                 />
              </div>

              {error && <p className="text-red-500 text-sm text-center">{error}</p>}

              <button type="submit" className="w-full bg-brand-600 hover:bg-brand-500 text-white font-bold py-3 rounded-xl transition shadow-lg shadow-brand-500/25 mt-4">
                 {isLogin ? 'Login' : 'Create Account'}
              </button>
           </form>

           <div className="mt-6 text-center">
              <p className="text-gray-500 text-sm">
                 {isLogin ? "Don't have an account? " : "Already have an account? "}
                 <button onClick={() => setIsLogin(!isLogin)} className="text-brand-500 font-bold hover:underline">
                    {isLogin ? 'Sign Up' : 'Login'}
                 </button>
              </p>
           </div>
        </div>
      </div>
    </div>
  );
}