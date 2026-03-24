import axios from 'axios';

//const API_URL = (import.meta.env.VITE_API_URL || "https://ssshaise-rcie.hf.space").replace(/\/$/, "");
const API_URL = "http://127.0.0.1:8000";

type Edge = string[];

export const api = {
    // --- CORE FUNCTIONS ---

    discover: async (
        datasetPath: string, method: string,
        useLLM: boolean = true,         
        domain: string = "general",     
        userConstraints: any = {}
    ) => {
        try {
            const res = await axios.post(`${API_URL}/discover`, 
                { dataset_path: datasetPath, method, use_llm: useLLM, domain: domain, user_constraints: userConstraints }
            );
            return res.data;
        } catch (error) {
            console.error("Discovery API Error:", error);
            throw error; // Re-throw so the UI can show a notification
        }
    },

    explain: async (edges: Edge[]) => {
        try {
            const res = await axios.post(`${API_URL}/explain`, { edges, context: "System Simulation" });
            return res.data;
        } catch (error) {
            console.error("Explanation API Error:", error);
            return { narrative: "Could not generate explanation at this time." }; // Fallback
        }
    },

    fitSCM: async (datasetPath: string, edges: Edge[], epochs: number) => {
        const res = await axios.post(`${API_URL}/fit_scm`, { 
            dataset_path: datasetPath, 
            dag_edges: edges, 
            epochs 
        });
        return res.data;
    },

    counterfactual: async (obs: any, intervention: any, edges: Edge[], datasetPath: string) => {
        const res = await axios.post(`${API_URL}/counterfactual`, {
            observation: obs,
            intervention: intervention,
            dag_edges: edges,
            dataset_path: datasetPath
        });
        return res.data;
    },

    simulate: async (intervention: any, edges: Edge[], datasetPath: string) => {
        const res = await axios.post(`${API_URL}/simulate`, {
            intervention: intervention,
            n_samples: 1000,
            dag_edges: edges,
            dataset_path: datasetPath
        });
        return res.data;
    },

    optimize: async (targetNode: string, targetValue: number, controlNode: string, edges: Edge[], datasetPath: string) => {
        const res = await axios.post(`${API_URL}/optimize`, {
            target_node: targetNode,
            target_value: targetValue,
            control_node: controlNode,
            dag_edges: edges,
            dataset_path: datasetPath
        });
        return res.data;
    },

    // --- FILE UPLOAD ---
    
    uploadDataset: async (file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        
        // Axios automatically sets Content-Type to multipart/form-data for FormData
        const res = await axios.post(`${API_URL}/upload`, formData);
        return res.data;
    },

    // --- HISTORY ---

    saveHistory: async (email: string, type: string, inputs: any, results: any) => {
        await axios.post(`${API_URL}/history/save`, { email, type, inputs, results });
    },

    getHistory: async (email: string) => {
        const res = await axios.get(`${API_URL}/history/${email}`);
        return res.data;
    },

    clearHistory: async (email: string) => {
        await axios.delete(`${API_URL}/history/${email}`);
    }
};