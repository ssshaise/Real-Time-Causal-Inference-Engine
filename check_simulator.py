import pandas as pd
import numpy as np
import logging
from src.ingestion.generator import CausalDataGenerator
from src.scm.estimator import CausalSCM
from src.simulator.simulator import CausalSimulator

logging.basicConfig(level=logging.WARNING)

print("1. Generating Data (X0 -> X1)...")
config = {
    'n_samples': 2000,
    'n_nodes': 2,
    'edge_density': 1.0, 
    'is_linear': True,   
    'noise_scale': 0.1,
    'seed': 42
}
gen = CausalDataGenerator(config)
gen.generate_dag()
if not gen.graph.has_edge('X0', 'X1'):
    print("   (Re-rolling graph to ensure X0->X1 edge...)")
    import networkx as nx
    gen.graph = nx.DiGraph()
    gen.graph.add_edge('X0', 'X1')

df = gen.generate_data()
print(f"   True Edges: {gen.graph.edges()}")

print("\n2. Fitting SCM...")
scm = CausalSCM(gen.graph)
scm.fit(df, epochs=200)

print("\n3. Running Simulation...")
sim = CausalSimulator(scm)

print("   Simulating do(X0 = -2.0)...")
df_low = sim.run_do_query({'X0': -2.0}, n_samples=1000)
mean_y_low = df_low['X1'].mean()

print("   Simulating do(X0 = +2.0)...")
df_high = sim.run_do_query({'X0': 2.0}, n_samples=1000)
mean_y_high = df_high['X1'].mean()

print(f"\n--- RESULTS ---")
print(f"Mean Y | do(X=-2): {mean_y_low:.4f}")
print(f"Mean Y | do(X=+2): {mean_y_high:.4f}")

uplift = mean_y_high - mean_y_low
print(f"Estimated Uplift (Effect of X): {uplift:.4f}")

if uplift > 0.1 or uplift < -0.1:
    print("SUCCESS: The intervention on X0 clearly changed X1.")
else:
    print("WARNING: Little to no effect observed. SCM might not have converged or link is weak.")