# [cite_start]Real-Time Causal Inference Engine (RCIE) [cite: 185]
A research-grade system for causal discovery, SCM estimation, counterfactual
[cite_start]reasoning, and intervention simulation. [cite: 186] Integrates LLMs for domain priors and
[cite_start]produces natural-language causal explanations. [cite: 187]

## Features
* [cite_start]Causal discovery (NOTEARS, PC, GES, DAG-GNN ensemble) [cite: 189]
* [cite_start]Structural equation estimation (NNs, GPS, GAMs) [cite: 190]
* [cite_start]Counterfactual and interventional queries (Pearl's 3-step method) [cite: 191]
* [cite_start]LLM-augmented causal prior extraction [cite: 192]
* [cite_start]Interactive demo UI and REST API [cite: 193]

## Quickstart
1.  [cite_start]Clone repo [cite: 196]
2.  [cite_start]`docker compose up --build` [cite: 197]
3.  [cite_start]`cd src && uvicorn api.main:app --reload` [cite: 198]
4.  [cite_start]Open http://localhost:3000 (frontend) or http://localhost:8000/docs (API docs) [cite: 199]

## Examples
* [cite_start]Run notebooks in `/notebooks` for synthetic-data validation [cite: 201]
* [cite_start]`python src/ingestion/generator.py --config configs/sim1.yaml` to create test DAGs [cite: 202]

## Evaluation
* [cite_start]Use ACIC and IHDP benchmarks (notebooks included) [cite: 204]
* [cite_start]Unit tests validate correctness of counterfactual engine [cite: 205]

## Contributors
* [cite_start]Your Name [cite: 207]

## License
[cite_start]MIT [cite: 209]