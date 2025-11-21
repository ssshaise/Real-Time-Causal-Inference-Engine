## Real-Time Causal Inference Engine (RCIE)
A production-ready engine for causal discovery, structural causal modeling, and real-time counterfactual reasoning.

## Overview
The Real-Time Causal Inference Engine (RCIE) is an end-to-end system designed to help analysts, ML engineers, and decision-makers answer “What causes what?” and “What happens if we intervene?” using principled causal inference.

Unlike classical ML models that only estimate correlations or predictions, RCIE provides:

1. Causal Discovery (NOTEARS, PC, GES, DAG-GNN ensemble)
2. Structural Equation Modeling (Neural SEMs, GAMs, GPS)
3. Counterfactual & Interventional Reasoning using Pearl’s 3-step method
4. LLM-augmented prior extraction for domain-aware causal graph refinement
5. REST API + Interactive UI for real-time causal queries
6. Dockerized deployment & reproducible benchmark notebooks (ACIC, IHDP)

RCIE is built for high-stakes decision-making, where explainability, auditability, and provable causality matter more than raw prediction accuracy. 

## Why This Matters
**Modern businesses run on questions predictive ML cannot answer:**

“Will increasing marketing spend actually reduce churn?”<br>

“Which factors cause conversion, not just correlate with it?”<br>

“What is the effect of discounting price by 10%?”<br>

“What would have happened if we had not launched feature X?”<br>

LLMs are strong at summarization but cannot perform mathematically grounded causal inference.<br>

**RCIE fills this gap by combining:**<br>
Statistical rigor + modern deep learning + LLM-based domain extraction + full-stack deployability. 

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
**1. Causal Discovery**
 NOTEARS (continuous optimization)<br>
 PC Algorithm (constraint-based)<br>
 GES (score-based)<br>
 DAG-GNN (deep learning–based)<br>
 Ensemble support with LLM-extracted priors

**2. Structural Equation Modeling**
 Neural Structural Equation Models (PyTorch)<br>
 Generalized Additive Models (GAMs)<br>
 Gaussian Process Models<

**3. Counterfactual & Intervention Engine**
 Implements Pearl’s abduction → action → prediction pipeline for hypothetical “what if” outcomes.

**5. API + Frontend**
 FastAPI for /discover, /counterfactual, /intervene endpoints<br>
 Lightweight UI for interactive graph visualization

**6. Fully Dockerized Deployment**
 Reproducible, portable, platform-independent. 

## Benchmarks & Evaluation

RCIE includes reproducible notebooks and pipelines:<br>
 ACIC 2016 causal benchmark tasks<br>
 IHDP semi-synthetic treatment effect prediction<br>
 Synthetic DAG generation for stress-testing<br>

## Metrics:

Structural Hamming Distance (SHD)<br>
Expected Treatment Effect (ATE / CATE)<br>
Counterfactual error<br>
Reconstruction accuracy<br>

## Tech Stack 

1. Backend: Python, PyTorch, sklearn, numpy, networkx
2. Causal Libraries: dowhy, causal-learn, causalml, torch-SEM
3. API: FastAPI, Uvicorn
4. Frontend: React / Next.js UI (lightweight)
5. Infra: Docker, MLflow for tracking, notebooks for reproducibility
6. Vector stores: for LLM contextual grounding

## Getting Started

1. Clone

```git clone https://github.com/username/Real-Time-Causal-Inference-Engine.git
cd Real-Time-Causal-Inference-Engine'
```

2. Start with Docker
```
docker compose up --build
```
Backend → http://localhost:8000
Frontend → http://localhost:3000

3. Run API directly (dev mode)
```
uvicorn rcie.api:app --reload --port 8000
```
4. Try an example query
```
curl -X POST "http://localhost:8000/counterfactual" \
  -H "Content-Type: application/json" \
  -d '{"variable": "price", "do": 10, "units": [1,2,3]}'
```
## Contributing

**Open to PRs! Areas to help with:**

new causal discovery algorithms<br>
performance optimization<br>
frontend UI improvements<br>
benchmark suite expansion

## Authors & Maintainers

Ruchir Srivastava – ML, NLP, Causal Engineering<br>
Collaborators & community contributors listed in repo.

## ⭐ If this project helped you, consider giving a star!