import numpy as np
import pandas as pd
import networkx as nx
import yaml
import argparse
import logging
from typing import Dict, Any, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CausalDataGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.n_nodes = config['n_nodes']
        self.edge_density = config['edge_density']
        self.is_linear = config.get('is_linear', True)
        self.noise_scale = config.get('noise_scale', 0.1)
        self.seed = config.get('seed', 42)
        self.graph = None
        self.adjacency_matrix = None
        
        np.random.seed(self.seed)

    def generate_dag(self) -> nx.DiGraph:
        """
        Generates a random Directed Acyclic Graph (DAG).
        """
        # Generate a random matrix
        G = nx.gnp_random_graph(self.n_nodes, self.edge_density, directed=True, seed=self.seed)
        
        # Make it a DAG by taking the upper triangular part (ensures no cycles)
        adjacency = nx.to_numpy_array(G)
        adjacency = np.triu(adjacency, k=1)
        
        # Shuffle nodes to avoid trivial ordering (node 0 -> node 1 -> ...)
        perm = np.random.permutation(self.n_nodes)
        adjacency = adjacency[perm, :][:, perm]
        
        self.adjacency_matrix = adjacency
        self.graph = nx.from_numpy_array(adjacency, create_using=nx.DiGraph)
        
        # Relabel nodes to X0, X1, ...
        mapping = {i: f"X{i}" for i in range(self.n_nodes)}
        self.graph = nx.relabel_nodes(self.graph, mapping)
        
        logger.info(f"Generated DAG with {self.graph.number_of_edges()} edges.")
        return self.graph

    def _structural_function(self, parents_values: np.ndarray) -> np.ndarray:
        """
        Applies a function to parent values to determine child value.
        """
        if parents_values.size == 0:
            return np.zeros(parents_values.shape[0]) if parents_values.ndim > 1 else 0.0
        
        # Linear combination of parents
        weights = np.random.uniform(0.5, 2.0, size=parents_values.shape[1])
        combined = np.dot(parents_values, weights)
        
        if self.is_linear:
            return combined
        else:
            # Non-linear transformation (e.g., tanh)
            return np.tanh(combined)

    def generate_data(self) -> pd.DataFrame:
        """
        Samples data from the SCM defined by the DAG.
        """
        if self.graph is None:
            self.generate_dag()
            
        n_samples = self.config['n_samples']
        data = pd.DataFrame(index=range(n_samples), columns=[f"X{i}" for i in range(self.n_nodes)])
        
        # Topological sort ensures we compute parents before children
        topo_order = list(nx.topological_sort(self.graph))
        
        for node in topo_order:
            parents = list(self.graph.predecessors(node))
            
            if not parents:
                # Root node: just noise
                values = np.random.normal(0, 1, n_samples)
            else:
                # Child node: function of parents + noise
                parent_values = data[parents].values
                effect = self._structural_function(parent_values)
                noise = np.random.normal(0, self.noise_scale, n_samples)
                values = effect + noise
                
            data[node] = values
            
        logger.info(f"Generated dataset with shape {data.shape}")
        return data

    def save_data(self, df: pd.DataFrame, path: str):
        df.to_csv(path, index=False)
        logger.info(f"Data saved to {path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True, help='Path to config yaml')
    parser.add_argument('--output', type=str, default='data/raw/sim_data.csv', help='Output path')
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    generator = CausalDataGenerator(config['simulation'])
    generator.generate_dag()
    df = generator.generate_data()
    generator.save_data(df, args.output)
    
    # Print edges for verification
    print("\nTrue Causal Graph Edges:")
    print(generator.graph.edges())