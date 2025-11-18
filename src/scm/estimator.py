# src/scm/estimator.py
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import networkx as nx
import numpy as np
import logging
import pickle
import os
import mlflow
from typing import Dict

logger = logging.getLogger(__name__)

class NodeEstimator(nn.Module):
    """
    A simple MLP (Neural Net) to predict a child node from its parents.
    """
    def __init__(self, n_inputs: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_inputs, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        )
        
    def forward(self, x):
        return self.net(x)

class CausalSCM:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
        self.models: Dict[str, NodeEstimator] = {}
        self.is_fitted = False
        self.data_stats = {}

    def fit(self, data: pd.DataFrame, epochs=100, lr=0.01):
        """
        Trains the SCM and logs the run to MLflow.
        """
        logger.info("Fitting SCM with MLflow tracking...")
        
        # 1. Setup MLflow Experiment
        mlflow.set_experiment("RCIE_Causal_Training")
        
        with mlflow.start_run():
            # Log Parameters (What settings did we use?)
            mlflow.log_param("epochs", epochs)
            mlflow.log_param("lr", lr)
            mlflow.log_param("num_nodes", len(self.graph.nodes()))
            mlflow.log_param("num_edges", len(self.graph.edges()))

            # 2. Calculate Safe Statistics (Prevent Division by Zero)
            self.data_stats = {
                'mean': data.mean(),
                'std': data.std().replace(0, 1.0) 
            }
            
            # Normalize data (Z-Score)
            data_norm = (data - self.data_stats['mean']) / self.data_stats['std']
            
            total_loss = 0.0
            
            # 3. Train a Neural Net for each node
            for node in self.graph.nodes():
                parents = list(self.graph.predecessors(node))
                if not parents:
                    continue
                    
                # Prepare tensors (fill NaNs with 0 to prevent crashes)
                X = torch.tensor(data_norm[parents].fillna(0).values, dtype=torch.float32)
                y = torch.tensor(data_norm[[node]].fillna(0).values, dtype=torch.float32)
                
                model = NodeEstimator(len(parents))
                optimizer = optim.Adam(model.parameters(), lr=lr)
                criterion = nn.MSELoss()
                
                # Training Loop
                for _ in range(epochs):
                    optimizer.zero_grad()
                    preds = model(X)
                    loss = criterion(preds, y)
                    loss.backward()
                    optimizer.step()
                    
                # Accumulate loss for logging
                final_loss = loss.item()
                total_loss += final_loss
                self.models[node] = model
            
            self.is_fitted = True
            
            # 4. Log Metrics & Artifacts to MLflow
            avg_loss = total_loss / max(1, len(self.models))
            mlflow.log_metric("avg_mse_loss", avg_loss)
            
            # Save a temp copy to upload to MLflow Registry
            os.makedirs("data/temp", exist_ok=True)
            temp_path = "data/temp/model_artifact.pkl"
            with open(temp_path, 'wb') as f:
                pickle.dump(self, f)
            
            mlflow.log_artifact(temp_path, artifact_path="model")
            logger.info(f"Training complete. Loss: {avg_loss:.4f}. Logged to MLflow.")

    def predict_node(self, node: str, parent_values: pd.DataFrame) -> np.ndarray:
        """
        Predicts a specific node's value given parent values using the learned SCM.
        """
        if node not in self.models:
            # If root or not fitted, sample from marginal distribution
            n = len(parent_values)
            return np.random.normal(
                self.data_stats['mean'][node], 
                self.data_stats['std'][node], 
                n
            )
            
        model = self.models[node]
        parents = list(self.graph.predecessors(node))
        
        # Normalize inputs
        inputs = (parent_values[parents] - self.data_stats['mean'][parents]) / self.data_stats['std'][parents]
        inputs = inputs.fillna(0) # Safety fill
        
        with torch.no_grad():
            X_tensor = torch.tensor(inputs.values, dtype=torch.float32)
            preds_norm = model(X_tensor).numpy().flatten()
            
        # De-normalize outputs
        preds = preds_norm * self.data_stats['std'][node] + self.data_stats['mean'][node]
        return preds

    def save(self, path: str):
        """Serialize the entire SCM object to disk (Persistence)."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self, f)
        logger.info(f"Model saved to {path}")

    @staticmethod
    def load(path: str):
        """Load SCM object from disk."""
        with open(path, 'rb') as f:
            return pickle.load(f)

# Unit test
if __name__ == "__main__":
    # Mock graph
    g = nx.DiGraph()
    g.add_edge("A", "B")
    
    # Mock data
    df = pd.DataFrame({
        'A': np.random.rand(100), 
        'B': np.random.rand(100)
    })
    
    scm = CausalSCM(g)
    scm.fit(df, epochs=10)
    print("Unit Test Passed.")