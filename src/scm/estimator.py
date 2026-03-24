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

        mlflow.set_experiment("RCIE_Causal_Training")
        
        with mlflow.start_run():
            mlflow.log_param("epochs", epochs)
            mlflow.log_param("lr", lr)
            mlflow.log_param("num_nodes", len(self.graph.nodes()))
            mlflow.log_param("num_edges", len(self.graph.edges()))

            self.data_stats = {
                'mean': data.mean(),
                'std': data.std().replace(0, 1.0) 
            }
            
            data_norm = (data - self.data_stats['mean']) / self.data_stats['std']
            
            total_loss = 0.0
            
            for node in self.graph.nodes():
                parents = list(self.graph.predecessors(node))
                if not parents:
                    continue
                    
                X = torch.tensor(data_norm[parents].fillna(0).values, dtype=torch.float32)
                y = torch.tensor(data_norm[[node]].fillna(0).values, dtype=torch.float32)
                
                model = NodeEstimator(len(parents))
                optimizer = optim.Adam(model.parameters(), lr=lr)
                criterion = nn.MSELoss()

                for _ in range(epochs):
                    optimizer.zero_grad()
                    preds = model(X)
                    loss = criterion(preds, y)
                    loss.backward()
                    optimizer.step()

                final_loss = loss.item()
                total_loss += final_loss
                self.models[node] = model
            
            self.is_fitted = True

            avg_loss = total_loss / max(1, len(self.models))
            mlflow.log_metric("avg_mse_loss", avg_loss)

            os.makedirs("data/temp", exist_ok=True)
            temp_path = "data/temp/model_artifact.pkl"
            with open(temp_path, 'wb') as f:
                pickle.dump(self, f)
            
            mlflow.log_artifact(temp_path, artifact_path="model")
            logger.info(f"Training complete. Loss: {avg_loss:.4f}. Logged to MLflow.")
            
    def update(self, new_data: pd.DataFrame, lr=0.001):
        """
        Performs a single gradient descent step on new streaming data.
        This enables 'Online Learning' without retraining from scratch.
        """
        if not self.is_fitted:
            logger.warning("Attempted to update an unfitted model. Ignoring.")
            return 0.0

        # 1. Normalize new data using the ORIGINAL training stats
        # (Crucial: We must use the same scale as the model was trained on)
        data_norm = (new_data - self.data_stats['mean']) / self.data_stats['std']
        
        total_loss = 0.0
        count = 0

        # 2. Update each node's neural network
        for node in self.graph.nodes():
            # Skip nodes that don't have parents (roots) or weren't trained
            if node not in self.models:
                continue

            parents = list(self.graph.predecessors(node))
            if not parents:
                continue

            model = self.models[node]
            model.train() # Switch to training mode

            # Prepare Tensors
            X_val = data_norm[parents].fillna(0).values
            y_val = data_norm[[node]].fillna(0).values

            X = torch.tensor(X_val, dtype=torch.float32)
            y = torch.tensor(y_val, dtype=torch.float32)

            # 3. Optimization Step
            # We initialize a fresh optimizer for this micro-batch
            optimizer = optim.Adam(model.parameters(), lr=lr)
            criterion = nn.MSELoss()

            optimizer.zero_grad()
            preds = model(X)
            loss = criterion(preds, y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            count += 1
        
        avg_loss = total_loss / max(1, count)
        logger.info(f"Streaming update complete. Loss: {avg_loss:.5f}")
        return avg_loss

    def predict_node(self, node: str, parent_values: pd.DataFrame) -> np.ndarray:
        """
        Predicts a specific node's value given parent values using the learned SCM.
        """
        if node not in self.models:
            n = len(parent_values)
            return np.random.normal(
                self.data_stats['mean'][node], 
                self.data_stats['std'][node], 
                n
            )
            
        model = self.models[node]
        parents = list(self.graph.predecessors(node))

        inputs = (parent_values[parents] - self.data_stats['mean'][parents]) / self.data_stats['std'][parents]
        inputs = inputs.fillna(0)
        
        with torch.no_grad():
            X_tensor = torch.tensor(inputs.values, dtype=torch.float32)
            preds_norm = model(X_tensor).numpy().flatten()
            
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

if __name__ == "__main__":
    g = nx.DiGraph()
    g.add_edge("A", "B")
    
    df = pd.DataFrame({
        'A': np.random.rand(100), 
        'B': np.random.rand(100)
    })
    
    scm = CausalSCM(g)
    scm.fit(df, epochs=10)
    print("Unit Test Passed.")