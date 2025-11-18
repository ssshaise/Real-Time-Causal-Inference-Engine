from prefect import flow, task
from src.utils.db import Database
from src.causal_discovery.discovery import CausalDiscoveryEngine
from src.scm.estimator import CausalSCM

@task
def load_data():
    db = Database()
    return db.get_data("events")

@task
def discover_structure(df):
    engine = CausalDiscoveryEngine(method="pc")
    return engine.run(df)

@task
def train_model(df, graph):
    scm = CausalSCM(graph)
    scm.fit(df, epochs=100)
    scm.save("data/models/automated_model.pkl")
    return scm

@flow(name="RCIE Retraining Loop")
def main_pipeline():
    data = load_data()
    
    graph = discover_structure(data)
    
    model = train_model(data, graph)
    
    print("Pipeline Complete. Model updated.")

if __name__ == "__main__":
    main_pipeline()