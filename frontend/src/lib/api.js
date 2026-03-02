import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
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

export default api;