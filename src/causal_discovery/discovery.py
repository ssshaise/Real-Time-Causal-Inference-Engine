import networkx as nx
import pandas as pd
import numpy as np
import logging
import mlflow
from typing import Dict, Any, List
from causallearn.search.ConstraintBased.PC import pc
from causallearn.search.ScoreBased.GES import ges
from causallearn.utils.PCUtils.BackgroundKnowledge import BackgroundKnowledge 
from src.causal_discovery.algorithms import run_notears
from causallearn.search.PermutationBased.GRaSP import grasp

try:
    from src.llm.client import CausalLLM
except ImportError:
    logging.warning("Could not import CausalLLM from src.llm.client")
    class CausalLLM:
        def suggest_priors(self, domain, vars): return []

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CausalDiscoveryEngine:    
    def __init__(self, method: str = "pc", options: Dict[str, Any] = None):
        """
        Args:
            method: 'pc', 'notears', or 'ges'
            options: dictionary of parameters (e.g., {'alpha': 0.05})
        """
        self.method = method.lower()
        self.options = options or {}

    def run(self, data: pd.DataFrame, use_llm: bool = False, user_constraints: Dict = None) -> nx.DiGraph:
        """
        Main execution method supporting Ablation Mode (use_llm T/F).
        """
        logger.info(f"Running causal discovery using {self.method}...")
        
        # 1. GATHER CONSTRAINTS
        priors = []
        if use_llm:
            logger.info("🔍 Querying CausalLLM for priors...")
            try:
                # Instantiate YOUR class
                llm = CausalLLM()
                
                # Get domain context (passed from API, or default to generic)
                domain_context = self.options.get("domain", "general numerical dataset")
                
                # Call YOUR method
                priors = llm.suggest_priors(domain_context, data.columns.tolist())
                
                logger.info(f"LLM suggested {len(priors)} edges: {priors}")
            except Exception as e:
                logger.error(f"LLM failed, falling back to pure stats: {e}")
                priors = []
        else:
            logger.info("Ablation Mode: LLM Disabled. Pure statistical discovery.")

        # Merge User Constraints (User > LLM)
        final_constraints = self._merge_constraints(priors, user_constraints)

        # 2. MLFLOW LOGGING
        mlflow.set_experiment("RCIE_Discovery")
        with mlflow.start_run(nested=True):
            mlflow.log_param("method", self.method)
            mlflow.log_param("use_llm", use_llm)
            mlflow.log_param("constraints_count", len(final_constraints["required"]))
            
            # 3. RUN ALGORITHM
            if self.method == "grasp":
                G = self._run_grasp(data, final_constraints)
            elif self.method == "notears":
                G = self._run_notears(data, final_constraints)
            elif self.method == "ges":
                G = self._run_ges(data, final_constraints)
            elif self.method == "pc":
                G = self._run_pc(data, final_constraints)
            else:
                raise ValueError(f"Unknown method: {self.method}")
            
            return G

    def _merge_constraints(self, llm_priors: List, user_constraints: Dict) -> Dict:
        """Helper to unify constraints into a standard format."""
        merged = {"required": [], "forbidden": []}
        
        # Add LLM suggestions (assuming they are tuples like ('A', 'B'))
        if llm_priors:
            merged["required"].extend(llm_priors)
            
        # Add User constraints (overrides)
        if user_constraints:
            merged["required"].extend(user_constraints.get("required", []))
            merged["forbidden"].extend(user_constraints.get("forbidden", []))
            
        return merged

    def _run_notears(self, data: pd.DataFrame, constraints: Dict) -> nx.DiGraph:
        """Score-based optimization using PyTorch"""
        # Normalize data
        data_norm = (data - data.mean()) / data.std()
        data_np = data_norm.fillna(0).values
        
        G_int = run_notears(data_np)
        
        G = nx.DiGraph()
        labels = data.columns.tolist()
        G.add_nodes_from(labels)
        
        for i, j in G_int.edges():
            source, target = labels[i], labels[j]
            # Simple Constraint Check: Don't add if forbidden
            if (source, target) not in constraints["forbidden"]:
                G.add_edge(source, target)
        
        # Force required edges
        for u, v in constraints["required"]:
            if u in labels and v in labels:
                G.add_edge(u, v)
                
        return G

    def _run_ges(self, data: pd.DataFrame, constraints: Dict) -> nx.DiGraph:
        """Greedy Equivalence Search (Score-based)"""
        data_np = data.values
        labels = data.columns.tolist()
        
        record = ges(data_np)
        adj_matrix = record['G'].graph
        
        G = nx.DiGraph()
        G.add_nodes_from(labels)
        
        n = len(labels)
        for i in range(n):
            for j in range(n):
                source, target = labels[j], labels[i]
                if adj_matrix[i, j] == 2 and adj_matrix[j, i] == 1:
                     if (source, target) not in constraints["forbidden"]:
                        G.add_edge(source, target)
                elif adj_matrix[i, j] == -1 and adj_matrix[j, i] == 1:
                     if (source, target) not in constraints["forbidden"]:
                        G.add_edge(source, target)
        
        # Force required edges
        for u, v in constraints["required"]:
            if u in labels and v in labels:
                G.add_edge(u, v)

        return G

    def _run_pc(self, data: pd.DataFrame, constraints: Dict) -> nx.DiGraph:
        """Peter-Clark (Constraint-based)"""
        data_np = data.to_numpy()
        labels = data.columns.tolist()
        
        # Setup Background Knowledge for PC
        bk = BackgroundKnowledge()
        
        # Add constraints directly to PC's logic
        for u, v in constraints["forbidden"]:
            if u in labels and v in labels:
                node_i, node_j = labels.index(u), labels.index(v)
                bk.add_forbidden_by_node(data.columns[node_i], data.columns[node_j])

        for u, v in constraints["required"]:
            if u in labels and v in labels:
                node_i, node_j = labels.index(u), labels.index(v)
                bk.add_required_by_node(data.columns[node_i], data.columns[node_j])

        alpha = self.options.get("alpha", 0.05)
        
        # Pass 'bk' to PC
        cg = pc(data_np, alpha, "fisherz", True, 0, -1, background_knowledge=bk)
        
        adj_matrix = cg.G.graph
        G = nx.DiGraph()
        G.add_nodes_from(labels)
        
        n = len(labels)
        for i in range(n):
            for j in range(n):
                if adj_matrix[i, j] == 1 and adj_matrix[j, i] == -1:
                    G.add_edge(labels[j], labels[i])
                    
        return G
    
    def _run_grasp(self, data: pd.DataFrame, constraints: Dict) -> nx.DiGraph:
        print("🚩 DEBUG: Starting GRaSP...")
        
        # 1. CLEANING
        # Remove non-numeric
        data_clean = data.select_dtypes(include=[np.number])
        print(f"🚩 DEBUG: Numeric shape: {data_clean.shape}")

        # Remove constant columns (Standard Deviation = 0)
        # GRaSP crashes if a column has the same value for every row
        data_clean = data_clean.loc[:, data_clean.std() > 0]
        print(f"🚩 DEBUG: Shape after dropping constants: {data_clean.shape}")

        if data_clean.shape[1] < 2:
            raise ValueError("Dataset has fewer than 2 valid columns after cleaning.")

        # 2. NORMALIZATION
        # Force float64 (GRaSP is strict about types)
        data_norm = (data_clean - data_clean.mean()) / data_clean.std()
        data_np = data_norm.fillna(0).values.astype(np.float64)
        print("🚩 DEBUG: Data normalized and cast to float64.")

        labels = data_clean.columns.tolist()

        # 3. RUN ALGORITHM
        try:
            print("🚩 DEBUG: Calling causallearn.grasp()...")
            # We explicitly ask for the 'local_score_BIC' which is robust
            from causallearn.search.PermutationBased.GRaSP import grasp
            G_grasp = grasp(data_np)
            print("🚩 DEBUG: GRaSP finished successfully.")
        except Exception as e:
            # THIS IS THE IMPORTANT PART
            import traceback
            print(f"❌ CRITICAL GRaSP ERROR: {e}")
            traceback.print_exc() # Forces full error stack to terminal
            raise ValueError(f"GRaSP Algorithm Crash: {str(e)}")

        # 4. PARSE OUTPUT
        try:
            adj_matrix = G_grasp.graph
            G = nx.DiGraph()
            G.add_nodes_from(labels)
            
            n = len(labels)
            for i in range(n):
                for j in range(n):
                    # -1 -> 1 implies i -> j
                    if adj_matrix[i, j] == 1 and adj_matrix[j, i] == -1:
                        source, target = labels[j], labels[i]
                        if (source, target) not in constraints["forbidden"]:
                            G.add_edge(source, target)
            
            # Apply Required
            for u, v in constraints["required"]:
                if u in labels and v in labels:
                    if not G.has_edge(u, v):
                        G.add_edge(u, v)
            
            print(f"🚩 DEBUG: Graph built with {G.number_of_edges()} edges.")
            return G
            
        except Exception as e:
            print(f"❌ Error parsing GRaSP output: {e}")
            raise e

# --- THE FUNCTION YOUR API EXPECTS ---
def discover_causal_graph(dataset: pd.DataFrame, method: str = "pc", use_llm: bool = True, user_constraints: Dict = None, domain: str = None) -> nx.DiGraph:
    """
    Wrapper function that API calls. 
    It instantiates the engine and runs the discovery pipeline.
    """
    options = {"domain": domain} if domain else {}
    engine = CausalDiscoveryEngine(method=method)
    return engine.run(dataset, use_llm=use_llm, user_constraints=user_constraints)

if __name__ == "__main__":
    # Quick test
    df = pd.DataFrame({
        'X': np.random.rand(100), 
        'Y': np.random.rand(100)
    })
    df['Z'] = df['X'] + df['Y'] + np.random.normal(0, 0.1, 100)
    
    # Test Ablation Mode
    print("Running WITHOUT LLM:")
    g_base = discover_causal_graph(df, method="pc", use_llm=False)
    print(f"Edges: {g_base.edges()}")
    
    print("\nRunning WITH LLM (Simulated):")
    g_llm = discover_causal_graph(df, method="pc", use_llm=True)
    print(f"Edges: {g_llm.edges()}")