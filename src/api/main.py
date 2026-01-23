# src/api/main.py
import pandas as pd
import networkx as nx
import logging
import math
import numpy as np
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File 
import shutil
from pydantic import BaseModel
from src.utils.auth_db import create_user, verify_user, save_history, get_history, delete_history
from src.causal_discovery.discovery import CausalDiscoveryEngine
from src.scm.estimator import CausalSCM
from src.counterfactuals.engine import CounterfactualEngine
from src.simulator.simulator import CausalSimulator
from src.llm.client import CausalLLM
from src.api.schemas import *
from src.utils.db import Database 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(title="RCIE System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "data/models/latest_model.pkl"

def load_active_model():
    """Try to load the model from disk and FIX it if it's broken."""
    if os.path.exists(MODEL_PATH):
        try:
            model = CausalSCM.load(MODEL_PATH)
            model.graph = make_acyclic(model.graph)
            logger.info("Model loaded and sanitized (cycles removed).")
            return model
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return None
    return None

ACTIVE_MODEL = load_active_model()

def make_acyclic(g: nx.DiGraph) -> nx.DiGraph:
    """
    Detects cycles and removes the back-edge to ensure DAG properties.
    Required for SCM and Counterfactual math.
    """
    g_copy = g.copy()
    while not nx.is_directed_acyclic_graph(g_copy):
        try:
            # Find a cycle (e.g., A -> B -> A)
            cycle = nx.find_cycle(g_copy)
            # Heuristic: Remove the last edge in the cycle sequence
            source, target = cycle[-1][0], cycle[-1][1]
            g_copy.remove_edge(source, target)
            logger.warning(f"Cycle detected! Removed edge {source} -> {target} to enforce DAG.")
        except Exception as e:
            logger.warning(f"Cycle removal error: {e}")
            break
    return g_copy

#SANITIZER
def sanitize_value(v):
    if v is None: return None
    try:
        if np.isnan(v) or np.isinf(v): return None
    except: pass
    if isinstance(v, (np.float32, np.float64)): return float(v)
    if isinstance(v, (np.int32, np.int64)): return int(v)
    return v

def sanitize_dict(d):
    return {k: sanitize_value(v) for k, v in d.items()}

# ENDPOINTS 

@app.get("/")
def read_root():
    status = "Model Loaded" if ACTIVE_MODEL else "No Model Trained"
    return {"status": "Online", "model_status": status}

@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    try:
        file_location = f"data/raw/{file.filename}"
        
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
            
        return {"status": "success", "filename": file_location, "message": "File uploaded successfully"}
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/history/{email}")
def clear_user_history(email: str):
    delete_history(email)
    return {"status": "cleared"}

@app.post("/auth/signup")
def signup(user: UserAuth):
    success = create_user(user.email, user.password, user.full_name)
    if not success:
        raise HTTPException(status_code=400, detail="Email already exists")
    return {"status": "success"}

@app.post("/auth/login")
def login(user: UserAuth):
    if verify_user(user.email, user.password):
        return {"status": "success", "email": user.email, "token": "fake-jwt-token-123"} 
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/history/save")
def save_analysis_history(item: HistoryItem):
    save_history(item.email, item.type, item.inputs, item.results)
    return {"status": "saved"}

@app.get("/history/{email}")
def get_user_history(email: str):
    return get_history(email)

@app.post("/discover", response_model=GraphResponse)
def discover_graph(req: DiscoveryRequest):
    try:
        try:
            db = Database()
            df = db.get_data("events")
        except Exception: 
            df = pd.read_csv(req.dataset_path)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset not found")

    engine = CausalDiscoveryEngine(method=req.method, options=req.options)
    try:
        graph = engine.run(df)
        
        graph = make_acyclic(graph)
        
        edges = [list(e) for e in graph.edges()]
        nodes = df.columns.tolist()
        return {"edges": edges, "nodes": nodes, "method": req.method}
    except Exception as e:
        logger.error(f"Discovery failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fit_scm", response_model=SCMStatusResponse)
def fit_scm(req: FitSCMRequest):
    global ACTIVE_MODEL
    try:
        try:
            db = Database()
            df = db.get_data("events")
        except Exception:
            df = pd.read_csv(req.dataset_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset not found")

    g = nx.DiGraph()
    for edge in req.dag_edges:
        g.add_edge(edge[0], edge[1])

    g = make_acyclic(g)
    
    scm = CausalSCM(g)
    scm.fit(df, epochs=req.epochs)
    
    scm.save(MODEL_PATH)
    ACTIVE_MODEL = scm
    
    return {"status": "success", "message": f"SCM trained on {len(g.edges())} edges and saved."}

@app.post("/counterfactual", response_model=CounterfactualResponse)
def query_counterfactual(req: CounterfactualRequest):
    global ACTIVE_MODEL
    if not ACTIVE_MODEL:
        ACTIVE_MODEL = load_active_model()
        
    if not ACTIVE_MODEL:
        try:
            try:
                db = Database()
                df = db.get_data("events")
            except Exception:
                df = pd.read_csv(req.dataset_path)
                
            g = nx.DiGraph()
            for edge in req.dag_edges:
                g.add_edge(edge[0], edge[1])
            
            g = make_acyclic(g)
            
            scm = CausalSCM(g)
            scm.fit(df, epochs=50)
            scm.save(MODEL_PATH)
            ACTIVE_MODEL = scm
        except Exception as e:
             raise HTTPException(status_code=400, detail=f"Model not trained and auto-train failed: {str(e)}")

    cf_engine = CounterfactualEngine(ACTIVE_MODEL)
    obs_series = pd.Series(req.observation)
    
    try:
        cf_result = cf_engine.estimate_counterfactual(obs_series, req.intervention)
        delta = {k: cf_result[k] - obs_series.get(k, 0) for k in cf_result.index}
        
        return {
            "original": sanitize_dict(req.observation),
            "counterfactual": sanitize_dict(cf_result.to_dict()),
            "delta": sanitize_dict(delta)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Math Error: {str(e)}")
    
@app.post("/optimize", response_model=OptimizeResponse)
def optimize_target(req: OptimizeRequest):
    global ACTIVE_MODEL
    if not ACTIVE_MODEL:
        ACTIVE_MODEL = load_active_model()
    
    if not ACTIVE_MODEL:
         raise HTTPException(status_code=400, detail="Model not trained.")

    try:
        try:
            db = Database()
            df = db.get_data("events")
        except Exception:
            df = pd.read_csv(req.dataset_path)
            
        min_val = df[req.control_node].min()
        max_val = df[req.control_node].max()
    except Exception:
        min_val, max_val = 0.0, 1.0 

    candidates = np.linspace(min_val, max_val,  50)
    best_diff = float('inf')
    best_val = candidates[0]
    best_pred = 0.0
    
    sim = CausalSimulator(ACTIVE_MODEL)
    
    for val in candidates:
        # Runs a mini-simulation for this value
        # We use a smaller sample size (n=100) for speed during search
        df_sim = sim.run_do_query({req.control_node: val}, n_samples=100)
        pred = df_sim[req.target_node].mean()
        
        diff = abs(pred - req.target_value)
        if diff < best_diff:
            best_diff = diff
            best_val = val
            best_pred = pred

    return {
        "suggested_value": sanitize_value(best_val),
        "predicted_outcome": sanitize_value(best_pred),
        "message": f"Optimal {req.control_node} found."
    }

@app.post("/simulate", response_model=SimulationResponse)
def run_simulation(req: SimulationRequest):
    global ACTIVE_MODEL
    if not ACTIVE_MODEL:
        ACTIVE_MODEL = load_active_model()
    
    if not ACTIVE_MODEL:
         raise HTTPException(status_code=400, detail="Model not trained. Please go to Tab 2 and train first.")
        
    sim = CausalSimulator(ACTIVE_MODEL)
    try:
        df_sim = sim.run_do_query(req.intervention, n_samples=req.n_samples)
        
        means = df_sim.mean().to_dict()
        
        lower = df_sim.quantile(0.05).to_dict()
        upper = df_sim.quantile(0.95).to_dict()
        
        return {
            "mean_outcomes": sanitize_dict(means),
            "lower_ci": sanitize_dict(lower),
            "upper_ci": sanitize_dict(upper)
        }
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        raise HTTPException(status_code=500, detail=f"Sim Error: {str(e)}")

@app.post("/explain", response_model=ExplanationResponse)
def explain_graph_endpoint(req: ExplanationRequest):
    llm = CausalLLM(model_name="gemini-2.5-flash")
    g = nx.DiGraph()
    for edge in req.edges:
        g.add_edge(edge[0], edge[1])
    text = llm.explain_graph(g, context=req.context)
    return {"narrative": text}
