## Real-Time Causal Inference Engine (RCIE)
A production-ready engine for causal discovery, structural causal modeling, and real-time counterfactual reasoning.

## Overview
The Real-Time Causal Inference Engine (RCIE) is an end-to-end system designed to help analysts, ML engineers, and decision-makers answer “What causes what?” and “What happens if we intervene?” using principled causal inference.

Unlike classical ML models that only estimate correlations or predictions, RCIE provides:

✔ Causal Discovery (NOTEARS, PC, GES, DAG-GNN ensemble)
✔ Structural Equation Modeling (Neural SEMs, GAMs, GPS)
✔ Counterfactual & Interventional Reasoning using Pearl’s 3-step method
✔ LLM-augmented prior extraction for domain-aware causal graph refinement
✔ REST API + Interactive UI for real-time causal queries
✔ Dockerized deployment & reproducible benchmark notebooks (ACIC, IHDP)

RCIE is built for high-stakes decision-making, where explainability, auditability, and provable causality matter more than raw prediction accuracy. 

## Why This Matters
Modern businesses run on questions predictive ML cannot answer:

“Will increasing marketing spend actually reduce churn?”

“Which factors cause conversion, not just correlate with it?”

“What is the effect of discounting price by 10%?”

“What would have happened if we had not launched feature X?”

LLMs are strong at summarization but cannot perform mathematically grounded causal inference.

RCIE fills this gap by combining:
statistical rigor + modern deep learning + LLM-based domain extraction + full-stack deployability. 

## Architecture

               ┌────────────────────┐
               │   Data Ingestion    │
               │ (CSV, DB, API, etc) │
               └─────────┬──────────┘
                         │
                ┌────────▼─────────┐
                │  Causal Discovery │
                │  PC / NOTEARS /   │
                │  GES / DAG-GNN    │
                └────────┬─────────┘
                         │
       ┌─────────────────▼────────────────┐
       │    Structural Equation Models    │
       │ (Neural SEMs, GAMs, GPS Models) │
       └─────────────────┬────────────────┘
                         │
                ┌────────▼─────────┐
                │ Counterfactual    │
                │ & Interventional  │
                │    Engine         │
                └────────┬─────────┘
                         │
                ┌────────▼─────────┐
                │   API Layer      │
                │  (FastAPI / REST)│
                └────────┬─────────┘
                         │
         ┌───────────────▼────────────────┐
         │   Interactive Frontend (UI)    │
         │  Real-time "What-if" queries   │
         └────────────────────────────────┘
 

## Key Features
1. Causal Discovery

NOTEARS (continuous optimization)

PC Algorithm (constraint-based)

GES (score-based)

DAG-GNN (deep learning–based)

Ensemble support with LLM-extracted priors

2. Structural Equation Modeling

Neural Structural Equation Models (PyTorch)

Generalized Additive Models (GAMs)

Gaussian Process Models

3. Counterfactual & Intervention Engine

Implements Pearl’s abduction → action → prediction pipeline for hypothetical “what if” outcomes.

4. LLM-Augmented Priors

Optional: use GPT-style LLMs to propose domain priors (soft constraints).

5. API + Frontend

FastAPI for /discover, /counterfactual, /intervene endpoints

Lightweight UI for interactive graph visualization

6. Fully Dockerized Deployment

Reproducible, portable, platform-independent. 

## Benchmarks & Evaluation

RCIE includes reproducible notebooks and pipelines:

ACIC 2016 causal benchmark tasks

IHDP semi-synthetic treatment effect prediction

Synthetic DAG generation for stress-testing

Metrics:

Structural Hamming Distance (SHD)

Expected Treatment Effect (ATE / CATE)

Counterfactual error

Reconstruction accuracy

## Tech Stack 

Backend: Python, PyTorch, sklearn, numpy, networkx
Causal Libraries: dowhy, causal-learn, causalml, torch-SEM
API: FastAPI, Uvicorn
Frontend: React / Next.js UI (lightweight)
Infra: Docker, MLflow for tracking, notebooks for reproducibility
Vector stores (optional): for LLM contextual grounding

## Getting Started

1. Clone
git clone https://github.com/username/Real-Time-Causal-Inference-Engine.git
cd Real-Time-Causal-Inference-Engine

2. Start with Docker

docker compose up --build

Backend → http://localhost:8000

Frontend → http://localhost:3000

3. Run API directly (dev mode)

uvicorn rcie.api:app --reload --port 8000

4. Try an example query

curl -X POST "http://localhost:8000/counterfactual" \
  -H "Content-Type: application/json" \
  -d '{"variable": "price", "do": 10, "units": [1,2,3]}'

## Contributing

Open to PRs! Areas to help with:

new causal discovery algorithms

performance optimization

frontend UI improvements

benchmark suite expansion

## Authors & Maintainers

Ruchir Srivastava – ML, NLP, Causal Engineering

Collaborators & community contributors listed in repo.

⭐ If this project helped you, consider giving a star!