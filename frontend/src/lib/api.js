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

export async function checkModels(baseUrl, apiKey) {
    const response = await api.post('/settings/check-models', {
        base_url: baseUrl,
        api_key: apiKey
    });
    return response.data.models;
}

// Upload API
export async function uploadFile(file, sheetName, columnName) {
    const formData = new FormData();
    formData.append('file', file);
    if (sheetName) formData.append('sheet_name', sheetName);
    if (columnName) formData.append('column_name', columnName);

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

// Classification API with SSE progress
export async function classifyFileWithProgress(data, onProgress) {
    return new Promise((resolve, reject) => {
        // Use fetch for SSE since axios doesn't support it well
        fetch(`${API_BASE_URL}/classify/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                function processStream({ done, value }) {
                    if (done) {
                        return;
                    }

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop() || '';

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));

                                if (data.type === 'progress') {
                                    onProgress({
                                        current: data.current,
                                        total: data.total
                                    });
                                } else if (data.type === 'complete') {
                                    resolve({
                                        history_id: data.history_id,
                                        filename: data.filename,
                                        status: data.status,
                                        total_rows: data.total_rows,
                                        processed_rows: data.processed_rows,
                                        failed_rows: data.failed_rows,
                                        result_path: data.result_path,
                                        message: data.message
                                    });
                                } else if (data.type === 'error') {
                                    reject(new Error(data.message));
                                }
                            } catch (e) {
                                console.error('Error parsing SSE data:', e);
                            }
                        }
                    }

                    return reader.read().then(processStream);
                }

                return reader.read().then(processStream);
            })
            .catch(reject);
    });
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
