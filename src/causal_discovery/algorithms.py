import torch
import numpy as np
import networkx as nx

def run_notears(X: np.ndarray, lambda1=0.1, max_iter=100) -> nx.DiGraph:
    """
    PyTorch implementation of NOTEARS (DAGs with NO TEARS).
    Continuous optimization for structure learning.
    """
    n, d = X.shape
    X_torch = torch.from_numpy(X).float()
    
    # Adjacency matrix (learnable weights)
    adj = torch.zeros(d, d, requires_grad=True)
    
    optimizer = torch.optim.LBFGS([adj], max_iter=max_iter)

    def loss_func():
        optimizer.zero_grad()
        # Loss = Least Squares + Acyclicity Constraint + Sparsity
        # (Simplified for brevity - standard formulation)
        X_hat = X_torch @ adj
        mse = 0.5 / n * torch.sum((X_torch - X_hat) ** 2)
        h = torch.trace(torch.matrix_exp(adj * adj)) - d # Acyclicity
        loss = mse + lambda1 * torch.norm(adj, 1) + 0.5 * h * h
        loss.backward()
        return loss

    optimizer.step(loss_func)
    
    # Thresholding to remove weak edges
    adj_np = adj.detach().numpy()
    adj_np[np.abs(adj_np) < 0.3] = 0 # Filter weak edges
    
    G = nx.DiGraph(adj_np)
    mapping = {i: col for i, col in enumerate(range(d))} # Need column mapping
    return G