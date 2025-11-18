# src/counterfactuals/engine.py
import numpy as np
import pandas as pd
import networkx as nx
import torch
import logging
from src.scm.estimator import CausalSCM

logger = logging.getLogger(__name__)

class CounterfactualEngine:
    def __init__(self, scm: CausalSCM):
        self.scm = scm
        if not scm.is_fitted:
            raise ValueError("SCM must be fitted before running counterfactuals.")

    def _abduct_noise(self, observation: pd.Series) -> pd.Series:
        """
        Step 1: Abduction. 
        Infer noise (U) from observed data. If an observation is missing, assume U=0 (Average case).
        """
        noise = {}
        
        # 1. Create a full observation vector, filling missing values with NaN
        full_obs = pd.Series(index=self.scm.graph.nodes(), dtype=float)
        full_obs.update(observation)
        
        # 2. Normalize (NaNs remain NaN)
        obs_norm = (full_obs - self.scm.data_stats['mean']) / self.scm.data_stats['std']
        
        for node in self.scm.graph.nodes():
            parents = list(self.scm.graph.predecessors(node))
            
            # Predict what the node *should* be based on parents
            if not parents:
                pred_val = 0.0 
            else:
                # If any parent is missing (NaN), we can't predict precisely, so assume mean input (0.0)
                parent_vals = obs_norm[parents].fillna(0.0).values.astype(np.float32)
                model = self.scm.models[node]
                with torch.no_grad():
                    pred_tensor = model(torch.tensor(parent_vals, dtype=torch.float32))
                    pred_val = pred_tensor.item()
            
            # Calculate Noise (Residual)
            # If we observed the node, Noise = Actual - Predicted
            if not pd.isna(obs_norm[node]):
                noise[node] = obs_norm[node] - pred_val
            else:
                # If we didn't observe it, assume it was acting "normally" (Zero noise)
                noise[node] = 0.0
            
        return pd.Series(noise)

    def estimate_counterfactual(self, 
                                observation: pd.Series, 
                                intervention: dict) -> pd.Series:
        # 1. Abduction
        u_noise = self._abduct_noise(observation)
        
        # 2. Action (Modify graph)
        # Start state: Use observation if available, otherwise use Mean (0.0 normalized)
        current_state = pd.Series(index=self.scm.graph.nodes(), dtype=float)
        full_obs = pd.Series(index=self.scm.graph.nodes(), dtype=float)
        full_obs.update(observation)
        
        # Normalize start state
        current_state = (full_obs - self.scm.data_stats['mean']) / self.scm.data_stats['std']
        current_state = current_state.fillna(0.0) # Fill unknown starts with Mean
        
        # Apply Intervention
        for node, value in intervention.items():
            norm_val = (value - self.scm.data_stats['mean'][node]) / self.scm.data_stats['std'][node]
            current_state[node] = norm_val

        # 3. Prediction (Propagate)
        topo_order = list(nx.topological_sort(self.scm.graph))
        
        for node in topo_order:
            if node in intervention:
                continue
                
            parents = list(self.scm.graph.predecessors(node))
            if not parents:
                # If root node & not intervened, it keeps its original value (observed or mean)
                continue
            
            parent_vals = current_state[parents].values.astype(np.float32)
            model = self.scm.models[node]
            
            with torch.no_grad():
                pred_effect = model(torch.tensor(parent_vals, dtype=torch.float32)).item()
            
            # New Value = Predicted Effect + Old Noise
            current_state[node] = pred_effect + u_noise[node]

        # De-normalize
        result = current_state * self.scm.data_stats['std'] + self.scm.data_stats['mean']
        return result