# src/api/schemas.py
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union

#Request Models

class OptimizeRequest(BaseModel):
    target_node: str          
    target_value: float       
    control_node: str        
    dataset_path: str
    dag_edges: List[List[str]]

class OptimizeResponse(BaseModel):
    suggested_value: float
    predicted_outcome: float
    message: str
    
class UserAuth(BaseModel):
    email: str
    password: str
    full_name: str = "User"

class HistoryItem(BaseModel):
    email: str
    type: str 
    inputs: Dict[str, Any]
    results: Dict[str, Any]

# Simulation Response
class SimulationResponse(BaseModel):
    mean_outcomes: Dict[str, Optional[float]]
    lower_ci: Dict[str, Optional[float]] = {} 
    upper_ci: Dict[str, Optional[float]] = {}

class DiscoveryRequest(BaseModel):
    dataset_path: str 
    method: str = "pc"
    options: Optional[Dict[str, Any]] = {}

class FitSCMRequest(BaseModel):
    dataset_path: str
    dag_edges: List[List[str]]
    epochs: int = 100

class CounterfactualRequest(BaseModel):
    observation: Dict[str, float] 
    intervention: Dict[str, float]
    dataset_path: str
    dag_edges: List[List[str]]

class SimulationRequest(BaseModel):
    intervention: Dict[str, float]
    n_samples: int = 1000
    dataset_path: str
    dag_edges: List[List[str]]

class ExplanationRequest(BaseModel):
    edges: List[List[str]]
    context: str = "generic system"

#Response Models

class GraphResponse(BaseModel):
    edges: List[List[str]]
    nodes: List[str]
    method: str

class SCMStatusResponse(BaseModel):
    status: str
    message: str

class CounterfactualResponse(BaseModel):
    original: Dict[str, Optional[float]] 
    counterfactual: Dict[str, Optional[float]]
    delta: Dict[str, Optional[float]]

class SimulationResponse(BaseModel):
    mean_outcomes: Dict[str, Optional[float]]
    uplift: Optional[float] = None

class ExplanationResponse(BaseModel):
    narrative: str