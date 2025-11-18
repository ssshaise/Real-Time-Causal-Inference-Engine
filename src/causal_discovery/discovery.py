# src/causal_discovery/discovery.py
import networkx as nx
import pandas as pd
import numpy as np
import logging
import mlflow
from typing import Dict, Any
from causallearn.search.ConstraintBased.PC import pc
from causallearn.search.ScoreBased.GES import ges
from src.causal_discovery.algorithms import run_notears

# Configure logging
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

    def run(self, data: pd.DataFrame) -> nx.DiGraph:
        logger.info(f"Running causal discovery using {self.method}...")
        
        mlflow.set_experiment("RCIE_Discovery")
        with mlflow.start_run(nested=True):
            mlflow.log_param("method", self.method)
            mlflow.log_param("num_samples", len(data))
            
            if self.method == "notears":
                G = self._run_notears(data)
            elif self.method == "ges":
                G = self._run_ges(data)
            elif self.method == "pc":
                G = self._run_pc(data)
            else:
                raise ValueError(f"Unknown method: {self.method}")
            
            # Log results
            num_edges = G.number_of_edges()
            mlflow.log_metric("num_edges_found", num_edges)
            logger.info(f"Discovery complete. Found {num_edges} edges.")
            
            return G

    def _run_notears(self, data: pd.DataFrame) -> nx.DiGraph:
        """Score-based optimization using PyTorch"""
        # Normalize data for better optimization
        data_norm = (data - data.mean()) / data.std()
        data_np = data_norm.fillna(0).values
        
        G_int = run_notears(data_np)
        
        # Remap integer indices back to column names
        G = nx.DiGraph()
        labels = data.columns.tolist()
        G.add_nodes_from(labels)
        
        for i, j in G_int.edges():
            # NOTEARS returns A[i,j] != 0 implies i -> j
            G.add_edge(labels[i], labels[j])
            
        return G

    def _run_ges(self, data: pd.DataFrame) -> nx.DiGraph:
        """Greedy Equivalence Search (Score-based)"""
        data_np = data.values
        labels = data.columns.tolist()
        
        # Returns: {'G': GeneralGraph, 'score': float}
        record = ges(data_np)
        adj_matrix = record['G'].graph
        
        G = nx.DiGraph()
        G.add_nodes_from(labels)
        
        # Parse causal-learn GES adjacency matrix
        # 1: tail (-), 2: arrowhead (>)
        # edge i -> j means graph[j, i] == 1 and graph[i, j] == 2
        n = len(labels)
        for i in range(n):
            for j in range(n):
                if adj_matrix[i, j] == 2 and adj_matrix[j, i] == 1:
                     G.add_edge(labels[j], labels[i])
                elif adj_matrix[i, j] == -1 and adj_matrix[j, i] == 1:
                     G.add_edge(labels[j], labels[i])
                     
        return G

    def _run_pc(self, data: pd.DataFrame) -> nx.DiGraph:
        """Peter-Clark (Constraint-based)"""
        data_np = data.to_numpy()
        labels = data.columns.tolist()
        
        # 0.05 is default alpha
        alpha = self.options.get("alpha", 0.05)
        cg = pc(data_np, alpha, "fisherz", True, 0, -1)
        
        # Parse adjacency
        adj_matrix = cg.G.graph
        G = nx.DiGraph()
        G.add_nodes_from(labels)
        
        n = len(labels)
        for i in range(n):
            for j in range(n):
                # -1 -> 1 implies i -> j
                if adj_matrix[i, j] == 1 and adj_matrix[j, i] == -1:
                    G.add_edge(labels[j], labels[i])
                    
        return G

if __name__ == "__main__":
    # Quick test
    df = pd.DataFrame({
        'X': np.random.rand(100), 
        'Y': np.random.rand(100)
    })
    # Z = X + Y
    df['Z'] = df['X'] + df['Y'] + np.random.normal(0, 0.1, 100)
    
    engine = CausalDiscoveryEngine(method="notears")
    g = engine.run(df)
    print(f"Edges found: {g.edges()}")