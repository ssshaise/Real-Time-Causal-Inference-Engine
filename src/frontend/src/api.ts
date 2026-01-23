import axios from 'axios';

// 1. Better URL handling (removes accidental double slashes)
const API_URL = (import.meta.env.VITE_API_URL || "https://ssshaise-rcie.hf.space").replace(/\/$/, "");

type Edge = string[];

// Helper to get token (if you implement protected routes later)
const getAuthHeaders = () => {
    const token = localStorage.getItem("token");
    return token ? { Authorization: `Bearer ${token}` } : {};
};

export const api = {
    // --- CORE FUNCTIONS ---

    discover: async (datasetPath: string, method: string) => {
        try {
            const res = await axios.post(`${API_URL}/discover`, 
                { dataset_path: datasetPath, method },
                { headers: getAuthHeaders() }
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

    // --- AUTHENTICATION ---

    login: async (email: string, password: string) => {
        try {
            const res = await axios.post(`${API_URL}/auth/login`, { email, password });
            // Automatically save token on success
            if (res.data.token) {
                localStorage.setItem("token", res.data.token);
                localStorage.setItem("userEmail", email);
            }
            return res.data;
        } catch (error) {
            throw new Error("Invalid email or password");
        }
    },

    signup: async (email: string, password: string, name: string) => {
        const res = await axios.post(`${API_URL}/auth/signup`, { email, password, full_name: name });
        return res.data;
    },

    logout: () => {
        localStorage.removeItem("token");
        localStorage.removeItem("userEmail");
        window.location.reload();
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