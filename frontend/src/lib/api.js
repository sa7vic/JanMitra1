import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT from localStorage on every request when available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

export const getStats = async () => {
  const response = await api.get('/api/stats');
  return response.data;
};

export const askQuestion = async (question) => {
  const response = await api.post('/api/query', { question });
  return response.data;
};

export const getNews = async (limit = 20, category = null) => {
  const params = { limit };
  if (category) params.category = category;
  const response = await api.get('/api/news', { params });
  return response.data;
};

export const getEntities = async (limit = 100, type = null) => {
  const params = { limit };
  if (type) params.type = type;
  const response = await api.get('/api/entities', { params });
  return response.data;
};

export const getRelationships = async (limit = 200) => {
  const response = await api.get('/api/relationships', { params: { limit } });
  return response.data;
};

export const getKnowledgeGraph = async () => {
  const response = await api.get('/api/knowledge-graph');
  return response.data;
};

export const getPredictions = async (status = 'active') => {
  const response = await api.get('/api/predictions', { params: { status } });
  return response.data;
};

export const collectData = async () => {
  const response = await api.post('/api/collect-data');
  return response.data;
};

export const processArticles = async (limit = 10) => {
  const response = await api.post('/api/process-articles', { limit });
  return response.data;
};

/**
 * Submit a report, optionally including an image file.
 *
 * @param {object} reportData  - Report fields (report_type, title, description, etc.)
 * @param {File|null} photoFile - Optional image file to attach
 */
export const submitReport = async (reportData, photoFile = null) => {
  if (photoFile) {
    const fd = new FormData();
    Object.entries(reportData).forEach(([key, value]) => {
      fd.append(key, typeof value === 'object' ? JSON.stringify(value) : value);
    });
    fd.append('photo', photoFile);
    const response = await api.post('/api/reports', fd, {
      headers: { 'Content-Type': undefined },  // let browser set multipart boundary
    });
    return response.data;
  }
  const response = await api.post('/api/reports', reportData);
  return response.data;
};

/**
 * Upload or replace the photo for an already-created report.
 *
 * @param {number} reportId  - Existing report ID
 * @param {File} photoFile   - Image file
 */
export const uploadReportPhoto = async (reportId, photoFile) => {
  const fd = new FormData();
  fd.append('photo', photoFile);
  const response = await api.post(`/api/reports/${reportId}/upload-photo`, fd, {
    headers: { 'Content-Type': undefined },
  });
  return response.data;
};

export default api;