# check_discovery.py
import pandas as pd
import networkx as nx
from src.causal_discovery.discovery import CausalDiscoveryEngine

# 1. Load the data
try:
    df = pd.read_csv("data/raw/sim_data.csv")
    print(f"Data loaded: {df.shape}")
except FileNotFoundError:
    print("Error: data/raw/sim_data.csv not found.")
    exit()

# 2. Run Discovery (PC Only)
print("\n--- Running PC Algorithm ---")
try:
    engine_pc = CausalDiscoveryEngine(method="pc")
    g_pc = engine_pc.run(df)
    print(f"PC found {len(g_pc.edges())} edges:")
    print(g_pc.edges())
except Exception as e:
    print(f"PC Failed: {e}")

# 3. Attempt NOTEARS (will warn if missing)
print("\n--- Attempting NOTEARS ---")
try:
    engine_nt = CausalDiscoveryEngine(method="notears")
    g_nt = engine_nt.run(df)
    print(f"NOTEARS found {len(g_nt.edges())} edges.")
except ImportError as e:
    print(f"Skipped NOTEARS: {e}")
except Exception as e:
    print(f"NOTEARS Failed: {e}")