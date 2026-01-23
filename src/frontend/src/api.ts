import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || "https://ssshaise-rcie.hf.space";

type Edge = string[];

export const api = {
    // CORE FUNCTIONS 
    discover: async (datasetPath: string, method: string) => {
        const res = await axios.post(`${API_URL}/discover`, { dataset_path: datasetPath, method });
        return res.data;
    },
    explain: async (edges: Edge[]) => {
        const res = await axios.post(`${API_URL}/explain`, { edges, context: "System Simulation" });
        return res.data;
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
    uploadDataset: async (file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        
        const res = await axios.post(`${API_URL}/upload`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return res.data;
    },
    

    login: async (email: string, password: string) => {
        const res = await axios.post(`${API_URL}/auth/login`, { email, password, full_name: "User" });
        return res.data;
    },
    signup: async (email: string, password: string, name: string) => {
        const res = await axios.post(`${API_URL}/auth/signup`, { email, password, full_name: name });
        return res.data;
    },

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