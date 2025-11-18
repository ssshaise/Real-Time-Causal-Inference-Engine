# Real-Time Causal Inference Engine (RCIE)
A research-grade system for causal discovery, SCM estimation, counterfactual
reasoning, and intervention simulation.  Integrates LLMs for domain priors and
produces natural-language causal explanations. 

## Features
* Causal discovery (NOTEARS, PC, GES, DAG-GNN ensemble) 
* Structural equation estimation (NNs, GPS, GAMs) 
* Counterfactual and interventional queries (Pearl's 3-step method) 
* LLM-augmented causal prior extraction 
* Interactive demo UI and REST API 

## Quickstart
1.  Clone repo 
2.  `docker compose up --build` 
3.  `cd src && uvicorn api.main:app --reload` 
4.  Open http://localhost:3000 (frontend) or http://localhost:8000/docs (API docs) 

## Examples
* Run notebooks in `/notebooks` for synthetic-data validation 
* `python src/ingestion/generator.py --config configs/sim1.yaml` to create test DAGs 

## Evaluation
* Use ACIC and IHDP benchmarks (notebooks included) 
* Unit tests validate correctness of counterfactual engine 

## Contributors
* Your Name 

## License
MIT 