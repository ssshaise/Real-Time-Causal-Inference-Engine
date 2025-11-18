# check_llm.py
import networkx as nx
import logging
from src.llm.client import CausalLLM

logging.basicConfig(level=logging.INFO)

def run_check():
    print("1. Initializing Gemini Client...")

    llm = CausalLLM(model_name="gemini-2.5-flash")

    print("\n2. Testing Graph Explanation...")
    g = nx.DiGraph()
    g.add_edges_from([
        ("Marketing_Spend", "Website_Visits"),
        ("Website_Visits", "Sales"),
        ("Competitor_Price", "Sales")
    ])

    context = "Retail E-Commerce Business"
    print(f"   Sending graph with {len(g.edges())} edges to Gemini...")
    explanation = llm.explain_graph(g, context)

    print(f"\n--- Graph Explanation ({context}) ---")
    print(explanation)
    print("-------------------------------------")

    print("\n3. Testing Prior Suggestion...")
    domain = "Fitness Tracker Analysis"
    variables = ["Steps_Taken", "Calories_Burned", "Heart_Rate", "Hours_Slept", "Fatigue_Level"]

    print(f"   Asking Gemini to find causal links between: {variables}")
    priors = llm.suggest_priors(domain, variables)
    
    print(f"\n--- Suggested Priors for {domain} ---")
    if priors:
        for edge in priors:
            print(f"   [+] {edge[0]} -> {edge[1]}")
    else:
        print("   [-] No priors returned (or error occurred).")

if __name__ == "__main__":
    run_check()