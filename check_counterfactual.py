# check_counterfactual.py
import pandas as pd
import numpy as np
import logging
from src.ingestion.generator import CausalDataGenerator
from src.causal_discovery.discovery import CausalDiscoveryEngine
from src.scm.estimator import CausalSCM
from src.counterfactuals.engine import CounterfactualEngine

logging.basicConfig(level=logging.WARNING)
print("1. Generating Data (X0 -> X1 -> X2)...")

config = {
    'n_samples': 1000,
    'n_nodes': 3,
    'edge_density': 0.5,
    'is_linear': True, 
    'noise_scale': 0.1,
    'seed': 42
}
gen = CausalDataGenerator(config)
gen.generate_dag()
df = gen.generate_data()
print(f"   True Edges: {gen.graph.edges()}")

print("\n2. Discovering Graph...")
dag = gen.graph 

print("\n3. Fitting SCM...")
scm = CausalSCM(dag)
scm.fit(df, epochs=300)

print("\n4. Running Counterfactual...")
cf_engine = CounterfactualEngine(scm)

obs = df.iloc[0]
print(f"   Observation:\n{obs}")

target_node = list(dag.nodes)[0] 
original_val = obs[target_node]
new_val = original_val + 2.0 

intervention = {target_node: new_val}
print(f"   Intervention: Set {target_node} = {new_val:.4f}")

cf_result = cf_engine.estimate_counterfactual(obs, intervention)

print("\n--- RESULT ---")
print(f"Original {target_node}: {original_val:.4f}")
print(f"New      {target_node}: {cf_result[target_node]:.4f} (Should match intervention)")

children = list(dag.successors(target_node))
if children:
    child = children[0]
    print(f"Child {child} Original: {obs[child]:.4f}")
    print(f"Child {child} Counterfactual: {cf_result[child]:.4f}")
    print("   (Value should have changed due to causal link)")
else:
    print("   (Target node had no children, so no downstream changes expected)")