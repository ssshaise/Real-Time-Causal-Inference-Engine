import pandas as pd
import numpy as np
import torch
import networkx as nx
import logging
from typing import Dict, List, Optional
from src.scm.estimator import CausalSCM

logger = logging.getLogger(__name__)

class CausalSimulator:
    def __init__(self, scm: CausalSCM):
        self.scm = scm
        if not scm.is_fitted:
            raise ValueError("SCM must be fitted before running simulations.")

    def run_do_query(self, 
                     interventions: Dict[str, float], 
                     n_samples: int = 1000) -> pd.DataFrame:
        """
        Simulates the effect of interventions do(X=x) on the system.
        Returns a DataFrame of simulated samples for all nodes.
        """
        # 1. Prepare empty container for samples (in normalized space)
        # We use the topo order to generate data sequentially
        topo_order = list(nx.topological_sort(self.scm.graph))
        
        # Store normalized values here
        sim_data = {node: np.zeros(n_samples) for node in topo_order}
        
        # Pre-calculate normalized intervention values
        norm_interventions = {}
        for node, val in interventions.items():
            mean = self.scm.data_stats['mean'][node]
            std = self.scm.data_stats['std'][node]
            norm_interventions[node] = (val - mean) / std

        # 2. Generate samples traversing the graph
        for node in topo_order:
            # CASE A: Node is intervened on
            if node in norm_interventions:
                sim_data[node] = np.full(n_samples, norm_interventions[node])
                continue
            
            # CASE B: Node is determined by parents
            parents = list(self.scm.graph.predecessors(node))
            
            if not parents:
                # Root node: sample from standard normal (since we work in normalized space)
                sim_data[node] = np.random.normal(0, 1, n_samples)
            else:
                # Construct input matrix for the neural net
                # Stack parent arrays into shape (n_samples, n_parents)
                parent_vals = np.stack([sim_data[p] for p in parents], axis=1)
                
                # Predict structural part
                model = self.scm.models[node]
                with torch.no_grad():
                    # Convert to tensor
                    X_tensor = torch.tensor(parent_vals, dtype=torch.float32)
                    # Predict
                    effect = model(X_tensor).numpy().flatten()
                
                # Add stochastic noise
                # In a real SCM, we might learn the variance. Here we assume unit noise for normalized data.
                noise = np.random.normal(0, 1, n_samples)
                sim_data[node] = effect + noise

        # 3. De-normalize everything back to original scale
        df_sim = pd.DataFrame(sim_data)
        for node in df_sim.columns:
            mean = self.scm.data_stats['mean'][node]
            std = self.scm.data_stats['std'][node]
            df_sim[node] = df_sim[node] * std + mean
            
        return df_sim

    def compute_uplift(self, 
                       control: Dict[str, float], 
                       treatment: Dict[str, float], 
                       target: str,
                       n_samples: int = 2000) -> float:
        """
        Calculates the Average Treatment Effect (ATE) on a target variable
        between two intervention sets.
        """
        df_control = self.run_do_query(control, n_samples)
        df_treatment = self.run_do_query(treatment, n_samples)
        
        mean_control = df_control[target].mean()
        mean_treated = df_treatment[target].mean()
        
        return mean_treated - mean_control