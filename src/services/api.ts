import axios from 'axios';
import type { PipelineConfig } from '../stores/workflows';

const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

export interface RunWorkflowPayload {
    fileName: string;
    targetCol: string;
    config: PipelineConfig;
}

export default {
    // Generic fetch for dataset headers (ranges, etc)
    async fetchDatasetHeaders(url: string) {
        // If it's a full URL (Firebase Storage), we use it directly.
        // However, if we want to proxy or standardise, we can do it here.
        // For now, we keep the direct call but wrapped.
        if (!url) return [];

        // We create a temp instance without base URL for external links
        const response = await axios.get(url, {
            headers: { Range: 'bytes=0-1024' }
        });

        const text = response.data;
        const lines = text.split('\n').map((l: string) => l.trim()).filter((l: string) => l);
        if (lines.length > 0) {
            return (lines[0] || '').split(',').map((h: string) => h.trim());
        }
        return [];
    },

    async runWorkflow(payload: FormData) {
        // NOTE: FormData acts differently, so we let browser set Content-Type
        const response = await apiClient.post('/run', payload, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    }
};
