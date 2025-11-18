# src/llm/client.py
import os
import json
import logging
import networkx as nx
from typing import List, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class CausalLLM:
    def __init__(self, model_name: str = "gemini-2.5-pro"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        self.model = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini Client initialized with model: {self.model_name}")
            except ImportError:
                logger.warning("google-generativeai library not installed. Run `pip install google-generativeai`.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
        else:
            logger.warning("No GEMINI_API_KEY found in .env. Running in MOCK mode.")

    def explain_graph(self, graph: nx.DiGraph, context: str = "generic system") -> str:
        """
        Generates a natural language explanation of the causal graph.
        """
        edges = list(graph.edges())
        if not edges:
            return "The causal graph is empty, so there are no relationships to explain."

        prompt = f"""
        You are an expert Causal Inference Scientist. 
        I have a Causal Bayesian Network (DAG) representing a {context}.
        
        Here are the directed edges (Cause -> Effect):
        {edges}
        
        Please provide a short, cohesive narrative explaining these relationships. 
        Focus on the downstream impact of the root causes. Keep it under 150 words.
        """

        if not self.model:
            return f"[MOCK GEMINI RESPONSE]: Based on edges {edges}, changes in parents will affect children..."

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini call failed: {e}")
            return "Error generating explanation."

    def suggest_priors(self, domain_description: str, variables: List[str]) -> List[Tuple[str, str]]:
        """
        Asks Gemini to suggest likely causal edges based on domain knowledge.
        Returns a list of tuples: [('Cause', 'Effect'), ...]
        """
        prompt = f"""
        I am building a causal model for the following domain: "{domain_description}".
        The available variables are: {variables}.
        
        Based on common sense and domain knowledge, which variables likely cause others?
        
        IMPORTANT: Return your answer ONLY as a raw JSON list of lists, like this: 
        [["VarA", "VarB"], ["VarB", "VarC"]]
        
        Do not include markdown formatting (like ```json), explanations, or extra text. Just the JSON string.
        """

        if not self.model:
            # Mock response
            if len(variables) >= 2:
                return [(variables[0], variables[1])]
            return []

        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            # Clean up if the model adds markdown blocks despite instructions
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                if content.endswith("```"):
                    content = content[:-3]
            
            edges_list = json.loads(content)
            # Convert list of lists to list of tuples
            return [tuple(edge) for edge in edges_list]
            
        except json.JSONDecodeError:
            logger.error("Gemini did not return valid JSON.")
            return []
        except Exception as e:
            logger.error(f"Gemini prior extraction failed: {e}")
            return []

# Unit Test if run directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    llm = CausalLLM()
    
    # Test Explanation
    g = nx.DiGraph()
    g.add_edge("Rain", "Wet_Grass")
    print("\n--- Explanation Test ---")
    print(llm.explain_graph(g, "Weather System"))
    
    # Test Priors
    print("\n--- Prior Suggestion Test ---")
    priors = llm.suggest_priors("Car Mechanics", ["Engine_Temp", "Oil_Level", "Car_Speed"])
    print(priors)