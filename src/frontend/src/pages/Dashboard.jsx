// src/frontend/src/pages/Dashboard.jsx
import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, Network, BrainCircuit, GitPullRequest, LineChart, ArrowRight, Play, 
  RotateCcw, ChevronDown, CheckCircle2, ArrowLeft, Target, Download, 
  UploadCloud, HardDrive, AlertTriangle, History, Clock, Trash2
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ErrorBar } from 'recharts';
import ForceGraph2D from 'react-force-graph-2d';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import { api } from '../api';

const DEFAULT_PATH = "data/raw/ecommerce_data.csv";

// --- UI COMPONENTS ---
const TabButton = ({ id, icon: Icon, label, activeTab, setActiveTab }) => (
  <button
    onClick={() => setActiveTab(id)}
    className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition-all duration-200 ${
      activeTab === id 
        ? 'bg-brand-600 text-white shadow-lg shadow-brand-500/25 scale-105' 
        : 'text-gray-500 hover:text-white hover:bg-white/5'
    }`}
  >
    <Icon size={18} />
    {label}
  </button>
);

const InputField = ({ label, value, onChange, type = "text", disabled = false, placeholder = "" }) => (
  <div className="w-full">
    {label && <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">{label}</label>}
    <input
      type={type}
      value={value}
      onChange={onChange}
      disabled={disabled}
      placeholder={placeholder}
      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-500 transition-all disabled:opacity-50"
    />
  </div>
);

const SelectField = ({ label, value, onChange, options }) => (
  <div className="w-full">
     {label && <label className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">{label}</label>}
     <div className="relative">
       <select
         value={value}
         onChange={onChange}
         className="w-full appearance-none bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-brand-500 transition-all cursor-pointer"
       >
         {options.map((o, i) => <option key={i} value={o.value} className="bg-[#1e1e1e]">{o.label}</option>)}
       </select>
       <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" size={16} />
     </div>
  </div>
);

export default function Dashboard() {
  const navigate = useNavigate();
  const userEmail = localStorage.getItem('user_email');
  
  // UI State
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  
  // Data State
  const [currentDataset, setCurrentDataset] = useState(DEFAULT_PATH);
  const [uploadMsg, setUploadMsg] = useState("");

  // Discovery State
  const [edges, setEdges] = useState([]);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [explanation, setExplanation] = useState("");
  const [algoMethod, setAlgoMethod] = useState('pc'); 

  // Training State
  const [epochs, setEpochs] = useState(100);
  const [trainMsg, setTrainMsg] = useState("");
  
  // Analysis State
  const [allNodes, setAllNodes] = useState([]);
  const [obsNode1, setObsNode1] = useState('');
  const [obsVal1, setObsVal1] = useState(0);
  const [obsNode2, setObsNode2] = useState('');
  const [obsVal2, setObsVal2] = useState(0); 
  const [intNode, setIntNode] = useState('');
  const [intVal, setIntVal] = useState(0);
  const [cfResult, setCfResult] = useState(null);
  
  const [simNode, setSimNode] = useState('');
  const [simVal, setSimVal] = useState(0);
  const [simData, setSimData] = useState([]);
  
  const [goalTarget, setGoalTarget] = useState('');
  const [goalValue, setGoalValue] = useState(0);
  const [goalControl, setGoalControl] = useState('');
  const [optResult, setOptResult] = useState(null);
  
  const graphWrapperRef = useRef(null);
  const [graphDimensions, setGraphDimensions] = useState({ w: 600, h: 500 });

  // --- EFFECTS ---
  useEffect(() => {
    document.documentElement.classList.add('dark');
    if (!userEmail) {
        navigate('/login');
    } else {
        loadHistory();
    }
  }, []);

  const loadHistory = async () => {
      if (!userEmail) return;
      try {
          const data = await api.getHistory(userEmail);
          setHistory(data);
      } catch (e) { console.error("Failed to load history", e); }
  };

  useEffect(() => {
    if (graphWrapperRef.current) {
      setGraphDimensions({ w: graphWrapperRef.current.offsetWidth, h: 500 });
    }
  }, [activeTab, graphData]);

  useEffect(() => {
    const uniqueNodes = new Set();
    edges.forEach(e => { uniqueNodes.add(e[0]); uniqueNodes.add(e[1]); });
    const sorted = Array.from(uniqueNodes).sort();
    setAllNodes(sorted);
    
    if (sorted.length > 0) {
      if (!obsNode1) setObsNode1(sorted[0]);
      if (!intNode) setIntNode(sorted[0]);
      if (!simNode) setSimNode(sorted[0]);
      if (!goalTarget) setGoalTarget(sorted[0]);
      if (!goalControl) setGoalControl(sorted[0]);
    }
  }, [edges]);

  // --- HANDLERS ---

  const handleLogout = () => {
      localStorage.removeItem('user_email');
      navigate('/');
  };

  const handleClearHistory = async () => {
      if(confirm("Are you sure you want to clear all history?")) {
          await api.clearHistory(userEmail);
          setHistory([]);
      }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    try {
        const res = await api.uploadDataset(file);
        setCurrentDataset(res.filename);
        setUploadMsg(`Uploaded: ${file.name}`);
    } catch (e) {
        alert("Upload Failed");
    }
    setLoading(false);
  };

  const handleDiscover = async () => {
    setLoading(true);
    try {
      const data = await api.discover(currentDataset, algoMethod);
      setEdges(data.edges);
      const uniqueNodes = new Set();
      if(data.nodes) data.nodes.forEach(n => uniqueNodes.add(n));
      const links = data.edges.map(e => ({ source: e[0], target: e[1] }));
      const nodes = Array.from(uniqueNodes).map(n => ({ id: n, name: n, val: 5 }));
      setGraphData({ nodes, links });
    } catch (e) { alert("Discovery Error. Is backend running?"); }
    setLoading(false);
  };

  const handleExplain = async () => {
    setLoading(true);
    try {
      const data = await api.explain(edges);
      setExplanation(data.narrative);
    } catch (e) { alert("AI Explanation Failed"); }
    setLoading(false);
  };

  const handleTrain = async () => {
    setLoading(true);
    try {
      await api.fitSCM(currentDataset, edges, epochs);
      setTrainMsg("✓ Neural SCM Model Trained Successfully");
    } catch (e) { alert("Training Failed"); }
    setLoading(false);
  };

  const handleCounterfactual = async () => {
    try {
      const observation = { [obsNode1]: Number(obsVal1) };
      if (obsNode2 && obsNode2 !== "") { observation[obsNode2] = Number(obsVal2); }
      const intervention = { [intNode]: Number(intVal) };
      
      const res = await api.counterfactual(observation, intervention, edges, currentDataset);
      setCfResult(res);

      if(userEmail) {
          await api.saveHistory(userEmail, 'counterfactual', { observation, intervention }, res);
          loadHistory();
      }
    } catch (e) { 
        const msg = e.response?.data?.detail || "Unknown error";
        alert(`Analysis Failed: ${msg}`); 
    }
  };

  const handleSimulate = async () => {
    try {
      const intervention = { [simNode]: Number(simVal) };
      const res = await api.simulate(intervention, edges, currentDataset);
      
      const chartData = Object.keys(res.mean_outcomes).map(k => ({ 
        name: k, 
        value: res.mean_outcomes[k],
        error: [res.lower_ci?.[k] ?? res.mean_outcomes[k], res.upper_ci?.[k] ?? res.mean_outcomes[k]]
      }));
      setSimData(chartData);

      if(userEmail) {
          await api.saveHistory(userEmail, 'simulation', { intervention }, res);
          loadHistory();
      }
    } catch (e) { 
        const msg = e.response?.data?.detail || e.message || "Unknown error";
        alert(`Simulation Failed: ${msg}`); 
    }
  };

  const handleOptimize = async () => {
      try {
          const res = await api.optimize(goalTarget, Number(goalValue), goalControl, edges, currentDataset);
          setOptResult(res);
      } catch (e) { alert("Optimization Failed"); }
  };

  const handleDownloadPDF = async () => {
      const element = document.getElementById('dashboard-content');
      const canvas = await html2canvas(element);
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('l', 'mm', 'a4');
      const imgProps = pdf.getImageProperties(imgData);
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
      pdf.save("RCIE_Executive_Report.pdf");
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-sans selection:bg-brand-500 selection:text-white pb-20">
      <nav className="sticky top-0 z-50 bg-[#0a0a0a]/80 backdrop-blur-md border-b border-white/10 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/')} className="p-2 rounded-xl hover:bg-white/10 transition text-gray-400"><ArrowLeft size={20} /></button>
            <div className="text-xl font-bold flex items-center gap-2">
              <Activity className="text-brand-600 w-6 h-6" /> RCIE Platform
            </div>
          </div>
          <div className="flex gap-2 bg-white/5 p-1 rounded-2xl hidden md:flex">
             <TabButton id={0} icon={Network} label="Discovery" activeTab={activeTab} setActiveTab={setActiveTab} />
             <TabButton id={1} icon={BrainCircuit} label="Training" activeTab={activeTab} setActiveTab={setActiveTab} />
             <TabButton id={2} icon={GitPullRequest} label="Analysis" activeTab={activeTab} setActiveTab={setActiveTab} />
          </div>
          <button onClick={handleDownloadPDF} className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg font-bold text-sm transition shadow-lg shadow-green-900/20">
             <Download size={16} /> Export Report
          </button>
        </div>
      </nav>

      <main id="dashboard-content" className="max-w-7xl mx-auto px-6 pt-8">
        <AnimatePresence mode="wait">
          
          {/* TAB 0: DISCOVERY */}
          {activeTab === 0 && (
            <motion.div key="discovery" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="grid grid-cols-1 lg:grid-cols-12 gap-8 h-[calc(100vh-140px)]">
               <div className="lg:col-span-4 flex flex-col gap-6">
                  <div className="bg-[#161616] border border-white/5 p-6 rounded-3xl shadow-xl shadow-black/5">
                    <h2 className="text-2xl font-bold mb-2">Data Ingestion</h2>
                    <p className="text-gray-400 text-sm mb-6">Upload observational data (CSV) to map causal structure.</p>
                    <div className="grid grid-cols-2 gap-3 mb-4">
                        <label className="flex flex-col items-center justify-center gap-2 p-4 border border-dashed border-white/20 rounded-xl hover:bg-white/5 cursor-pointer transition">
                            <UploadCloud className="text-brand-500" /><span className="text-xs font-bold text-gray-400">From PC</span><input type="file" className="hidden" accept=".csv" onChange={handleFileUpload} />
                        </label>
                        <button className="flex flex-col items-center justify-center gap-2 p-4 border border-dashed border-white/20 rounded-xl hover:bg-white/5 cursor-not-allowed opacity-50" title="Requires API Key">
                            <HardDrive className="text-yellow-500" /><span className="text-xs font-bold text-gray-400">Google Drive</span>
                        </button>
                    </div>
                    {uploadMsg && <div className="mb-4 px-3 py-2 bg-brand-500/10 border border-brand-500/20 rounded-lg flex items-center gap-2"><CheckCircle2 size={16} className="text-brand-500" /><span className="text-xs text-brand-200 font-mono truncate">{uploadMsg}</span></div>}
                    <div className="mb-6 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-xl">
                        <div className="flex items-center gap-2 mb-1"><AlertTriangle size={16} className="text-yellow-500" /><span className="text-xs font-bold text-yellow-500 uppercase">Data Quality Warning</span></div>
                        <p className="text-[11px] text-yellow-200/70 leading-relaxed">Ensure data is <strong>clean</strong> and <strong>labeled</strong>. Garbage in = Garbage out.</p>
                    </div>
                    <div className="space-y-4 border-t border-white/10 pt-4">
                      <InputField label="Active Dataset" value={currentDataset.split('/').pop()} disabled />
                      <SelectField label="Discovery Algorithm" value={algoMethod} onChange={(e) => setAlgoMethod(e.target.value)} options={[{value: 'pc', label: 'PC (Constraint-Based)'}, {value: 'notears', label: 'NOTEARS (Score-Based)'}, {value: 'ges', label: 'GES (Greedy Search)'}]} />
                      <button onClick={handleDiscover} disabled={loading} className="w-full py-4 bg-brand-600 hover:bg-brand-500 text-white rounded-xl font-bold text-lg shadow-lg shadow-brand-500/30 transition-all hover:-translate-y-1 disabled:opacity-50 disabled:hover:translate-y-0 flex items-center justify-center gap-2">
                        {loading ? <RotateCcw className="animate-spin" /> : <Play size={20} fill="currentColor" />} Run Discovery
                      </button>
                    </div>
                    {edges.length > 0 && (
                      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-6 p-4 bg-green-900/20 border border-green-900 rounded-xl">
                        <div className="flex items-center gap-2 text-green-400 font-bold mb-2"><CheckCircle2 size={18} /> Analysis Complete</div>
                        <p className="text-sm text-green-300 mb-3">Found {edges.length} causal relationships.</p>
                        <button onClick={handleExplain} className="text-sm font-bold text-brand-600 hover:underline flex items-center gap-1">Ask AI to explain <ArrowRight size={14} /></button>
                        {explanation && <div className="mt-3 p-3 bg-black/20 rounded-lg text-sm leading-relaxed opacity-90">{explanation}</div>}
                      </motion.div>
                    )}
                  </div>
               </div>
               <div className="lg:col-span-8 h-full bg-[#161616] border border-white/5 rounded-3xl overflow-hidden shadow-2xl shadow-black/5 relative flex flex-col">
                  <div className="p-4 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
                     <span className="text-xs font-bold uppercase tracking-widest text-gray-400">Visualizer // Force-Directed</span>
                  </div>
                  <div ref={graphWrapperRef} className="flex-1 bg-[#050505] relative cursor-move">
                    {graphData.nodes.length > 0 ? (
                        <ForceGraph2D 
                          width={graphDimensions.w}
                          height={graphDimensions.h}
                          graphData={graphData}
                          nodeColor={() => "#00e5ff"}
                          linkColor={() => "rgba(255,255,255,0.2)"}
                          nodeRelSize={6}
                          linkDirectionalArrowLength={4}
                          linkDirectionalArrowRelPos={1}
                          backgroundColor="#050505"
                          nodeCanvasObject={(node, ctx, globalScale) => {
                            const label = node.name;
                            const fontSize = 14/globalScale;
                            ctx.font = `${fontSize}px Sans-Serif`;
                            ctx.fillStyle = '#00e5ff';
                            ctx.beginPath(); ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI, false); ctx.fill();
                            ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = 'white';
                            ctx.fillText(label, node.x, node.y + 10); 
                          }}
                        />
                    ) : (
                      <div className="absolute inset-0 flex items-center justify-center flex-col gap-4 text-gray-500">
                         <Network size={48} className="opacity-20" />
                         <p>Run discovery to render causal map</p>
                      </div>
                    )}
                  </div>
               </div>
            </motion.div>
          )}

          {/* TAB 1: TRAINING */}
          {activeTab === 1 && (
             <motion.div key="training" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="flex items-center justify-center h-[80vh]">
                <div className="bg-[#161616] border border-white/5 p-12 rounded-[2rem] shadow-2xl text-center max-w-2xl w-full">
                   <div className="w-20 h-20 bg-brand-500/10 rounded-full flex items-center justify-center mx-auto mb-6"><BrainCircuit size={40} className="text-brand-500" /></div>
                   <h2 className="text-4xl font-bold mb-4">Fit Structural Model</h2>
                   <p className="text-gray-400 mb-8 text-lg">Train neural networks to learn the non-linear equations governing your data.</p>
                   <div className="bg-black/20 p-6 rounded-2xl mb-8 text-left">
                      <label className="text-xs font-bold text-gray-400 uppercase mb-2 block">Training Epochs: {epochs}</label>
                      <input type="range" min="50" max="500" value={epochs} onChange={(e) => setEpochs(Number(e.target.value))} className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-brand-500" />
                      <div className="flex justify-between text-xs text-gray-400 mt-2"><span>Fast (50)</span><span>Deep (500)</span></div>
                   </div>
                   <button onClick={handleTrain} disabled={loading || edges.length === 0} className="w-full py-4 bg-brand-600 hover:bg-brand-500 text-white rounded-xl font-bold text-lg shadow-lg shadow-brand-500/30 transition-all hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed">{loading ? "Training Neural Networks..." : "Start Training Process"}</button>
                   {trainMsg && <div className="mt-6 flex items-center justify-center gap-2 text-green-500 font-medium bg-green-500/10 py-3 rounded-lg"><CheckCircle2 size={20} /> {trainMsg}</div>}
                </div>
             </motion.div>
          )}

          {/* TAB 2: ANALYSIS */}
          {activeTab === 2 && (
             <motion.div key="analysis" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="space-y-6">
                   <div className="bg-[#161616] border border-green-500/30 p-6 rounded-3xl shadow-xl relative overflow-hidden">
                      <div className="absolute top-0 right-0 p-3 opacity-10"><Target size={80} className="text-green-500" /></div>
                      <div className="relative z-10">
                          <div className="flex items-center gap-3 mb-4"><div className="p-2 bg-green-500/10 rounded-lg text-green-500"><Target size={20}/></div><div><h3 className="font-bold text-lg">Goal Seeker</h3><p className="text-xs text-gray-500">Reverse Optimization</p></div></div>
                          <div className="space-y-3">
                             <div className="grid grid-cols-2 gap-2">
                                <SelectField label="I want..." value={goalTarget} onChange={(e) => setGoalTarget(e.target.value)} options={allNodes.map(n => ({value: n, label: n}))} />
                                <InputField label="To Equal" value={goalValue} onChange={(e) => setGoalValue(e.target.value)} type="number" />
                             </div>
                             <SelectField label="By changing..." value={goalControl} onChange={(e) => setGoalControl(e.target.value)} options={allNodes.map(n => ({value: n, label: n}))} />
                             <button onClick={handleOptimize} className="w-full py-3 bg-green-600 hover:bg-green-500 text-white rounded-xl font-bold transition-all shadow-lg shadow-green-900/20">Find Strategy</button>
                          </div>
                          {optResult && <div className="mt-4 p-3 bg-green-500/10 border border-green-500/20 rounded-xl text-sm"><span className="text-green-400 font-bold">Success:</span> Set {goalControl} to <span className="text-white font-mono font-bold text-lg">{Number(optResult.suggested_value).toFixed(2)}</span></div>}
                      </div>
                   </div>
                   <div className="bg-[#161616] border border-white/5 p-6 rounded-3xl shadow-xl">
                      <div className="flex items-center gap-3 mb-6 pb-4 border-b border-white/5"><div className="p-2 bg-purple-500/10 rounded-lg text-purple-500"><GitPullRequest size={20}/></div><div><h3 className="font-bold text-lg">Counterfactuals</h3><p className="text-xs text-gray-500">Analyze specific past events</p></div></div>
                      <div className="space-y-6">
                        <div className="space-y-3">
                           <span className="text-xs font-bold text-blue-500 uppercase tracking-wider">1. The Context</span>
                           <div className="grid grid-cols-2 gap-2">
                              <SelectField value={obsNode1} onChange={(e) => setObsNode1(e.target.value)} options={allNodes.map(n => ({value: n, label: n}))} />
                              <InputField value={obsVal1} onChange={(e) => setObsVal1(e.target.value)} placeholder="Value" type="number" />
                           </div>
                           <div className="grid grid-cols-2 gap-2">
                              <SelectField value={obsNode2} onChange={(e) => setObsNode2(e.target.value)} options={[{value: '', label: '+ Add Var'}, ...allNodes.map(n => ({value: n, label: n}))]} />
                              <InputField value={obsVal2} onChange={(e) => setObsVal2(e.target.value)} placeholder="Value" type="number" disabled={!obsNode2} />
                           </div>
                        </div>
                        <div className="space-y-3"><span className="text-xs font-bold text-pink-500 uppercase tracking-wider">2. Intervention</span><div className="grid grid-cols-2 gap-2"><SelectField value={intNode} onChange={(e) => setIntNode(e.target.value)} options={allNodes.map(n => ({value: n, label: n}))} /><InputField value={intVal} onChange={(e) => setIntVal(e.target.value)} placeholder="New Value" type="number" /></div></div>
                        <button onClick={handleCounterfactual} className="w-full py-3 border border-purple-500/30 text-purple-500 hover:bg-purple-500 hover:text-white rounded-xl font-bold transition-all">Run Analysis</button>
                      </div>
                   </div>
                   <div className="bg-[#161616] border border-white/5 p-6 rounded-3xl shadow-xl">
                      <div className="flex items-center gap-3 mb-6 pb-4 border-b border-white/5"><div className="p-2 bg-blue-500/10 rounded-lg text-blue-500"><LineChart size={20}/></div><div><h3 className="font-bold text-lg">Future Simulation</h3><p className="text-xs text-gray-500">Monte Carlo Prediction</p></div></div>
                      <div className="space-y-4">
                         <SelectField label="Policy Lever" value={simNode} onChange={(e) => setSimNode(e.target.value)} options={allNodes.map(n => ({value: n, label: n}))} />
                         <InputField label="Target Value" value={simVal} onChange={(e) => setSimVal(e.target.value)} type="number" />
                         <button onClick={handleSimulate} className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold transition-all shadow-lg shadow-blue-500/20">Simulate Future</button>
                      </div>
                   </div>
                </div>
                <div className="lg:col-span-2 h-full min-h-[600px]">
                   <div className="bg-[#161616] border border-white/5 p-8 rounded-3xl shadow-xl h-full flex flex-col">
                      <h3 className="text-xl font-bold mb-6 flex items-center gap-2"><Activity className="text-brand-500" /> Intelligence Report</h3>
                      <div className="flex-1">
                        {!cfResult && simData.length === 0 && (
                           <div className="h-full flex flex-col items-center justify-center text-gray-400 opacity-50">
                              <BrainCircuit size={64} strokeWidth={1} className="mb-4"/><p className="text-lg font-medium">Ready for computation</p><p className="text-sm">Select inputs on the left to generate report.</p>
                           </div>
                        )}
                        {cfResult && (
                           <div className="mb-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
                              <div className="flex items-center gap-3 mb-4"><span className="bg-purple-500 text-white px-2 py-1 rounded text-xs font-bold">WHAT-IF</span><span className="text-sm text-gray-500">Causal Impact Assessment</span></div>
                              <div className="overflow-hidden rounded-xl border border-white/10"><table className="w-full text-sm text-left"><thead className="bg-white/5 text-gray-500 font-medium"><tr><th className="px-4 py-3">Variable</th><th className="px-4 py-3">Original</th><th className="px-4 py-3">Scenario</th><th className="px-4 py-3">Net Impact</th></tr></thead><tbody className="divide-y divide-white/5">{Object.keys(cfResult.delta).map(key => (<tr key={key}><td className="px-4 py-3 font-medium">{key}</td><td className="px-4 py-3 text-gray-500">{cfResult.original[key] !== null ? Number(cfResult.original[key]).toFixed(2) : "-"}</td><td className="px-4 py-3">{Number(cfResult.counterfactual[key]).toFixed(2)}</td><td className={`px-4 py-3 font-bold ${cfResult.delta[key] > 0 ? 'text-green-500' : (cfResult.delta[key] < 0 ? 'text-red-500' : 'text-gray-400')}`}>{cfResult.delta[key] ? (cfResult.delta[key] > 0 ? "+" : "") + Number(cfResult.delta[key]).toFixed(2) : "-"}</td></tr>))}</tbody></table></div>
                           </div>
                        )}
                        {simData.length > 0 && (
                           <div className="h-80 animate-in fade-in slide-in-from-bottom-8 duration-700 mt-8">
                              <div className="flex items-center gap-3 mb-4"><span className="bg-blue-500 text-white px-2 py-1 rounded text-xs font-bold">FORECAST</span><span className="text-sm text-gray-500">Mean Outcome + 95% Risk Range</span></div>
                              <ResponsiveContainer width="100%" height="100%"><BarChart data={simData}><CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} opacity={0.2} /><XAxis dataKey="name" stroke="#888" fontSize={12} tickLine={false} axisLine={false} /><YAxis stroke="#888" fontSize={12} tickLine={false} axisLine={false} /><Tooltip contentStyle={{ backgroundColor: '#1e1e1e', borderRadius: '8px', border: 'none' }} itemStyle={{ color: '#fff' }} /><Bar dataKey="value" fill="#00e5ff" radius={[4, 4, 0, 0]} barSize={50}><ErrorBar dataKey="error" width={4} strokeWidth={2} stroke="white" direction="y" /></Bar></BarChart></ResponsiveContainer>
                           </div>
                        )}
                      </div>
                      {/* HISTORY SIDEBAR */}
                      <div className="mt-12 pt-8 border-t border-white/5">
                          <div className="flex justify-between items-center mb-4">
                            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2"><History size={16} /> Recent Session History</h3>
                            <button onClick={handleClearHistory} className="text-xs text-red-500 hover:text-red-400 flex items-center gap-1 hover:bg-red-500/10 px-2 py-1 rounded transition"><Trash2 size={12} /> Clear</button>
                          </div>
                          <div className="space-y-2 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
                              {history.length === 0 ? (<p className="text-sm text-gray-600 italic">No history yet. Run an analysis to save results.</p>) : (
                                  history.map((h) => (<div key={h.id} className="p-3 bg-white/5 rounded-lg border border-white/5 hover:bg-white/10 transition group"><div className="flex justify-between items-center mb-1"><span className={`text-[10px] px-2 py-0.5 rounded uppercase font-bold ${h.type === 'counterfactual' ? 'bg-purple-500/20 text-purple-400' : 'bg-blue-500/20 text-blue-400'}`}>{h.type}</span><span className="text-[10px] text-gray-500 flex items-center gap-1"><Clock size={10} /> {h.timestamp}</span></div><div className="text-xs text-gray-400 truncate font-mono">{JSON.stringify(h.inputs).substring(0, 60)}...</div></div>))
                              )}
                          </div>
                      </div>
                   </div>
                </div>
             </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}