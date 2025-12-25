import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Settings API
export async function getSettings() {
    const response = await api.get('/settings');
    return response.data;
}

export async function updateSettings(settings) {
    const response = await api.put('/settings', settings);
    return response.data;
}

// Upload API
export async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    });
    return response.data;
}

// Classification API
export async function classifyFile(data) {
    const response = await api.post('/classify', data);
    return response.data;
}

export async function downloadResult(historyId) {
    const response = await api.get(`/classify/${historyId}/download`, {
        responseType: 'blob'
    });

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `classified_result_${historyId}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
}

// History API
export async function getHistory() {
    const response = await api.get('/history');
    return response.data;
}

export async function getHistoryById(historyId) {
    const response = await api.get(`/history/${historyId}`);
    return response.data;
}
