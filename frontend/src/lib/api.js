import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const locationCache = {
  states: null,
  districts: new Map(),
  cities: new Map(),
};

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

export const getStates = async () => {
  if (locationCache.states) {
    return locationCache.states;
  }
  const response = await api.get('/api/locations/states');
  locationCache.states = response.data.states || [];
  return locationCache.states;
};

export const getDistricts = async (state) => {
  if (!state) return [];
  if (locationCache.districts.has(state)) {
    return locationCache.districts.get(state);
  }
  const response = await api.get('/api/locations/districts', { params: { state } });
  const districts = response.data.districts || [];
  locationCache.districts.set(state, districts);
  return districts;
};

export const getCities = async (state, district) => {
  if (!state || !district) return [];
  const key = `${state}::${district}`;
  if (locationCache.cities.has(key)) {
    return locationCache.cities.get(key);
  }
  const response = await api.get('/api/locations/cities', {
    params: { state, district },
  });
  const cities = response.data.cities || [];
  locationCache.cities.set(key, cities);
  return cities;
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

export const getGraphSubgraph = async (limitNodes = 120, limitEdges = 240) => {
  const response = await api.get('/api/graph/subgraph', {
    params: { limit_nodes: limitNodes, limit_edges: limitEdges },
  });
  return response.data;
};

export const queryGraphNaturalLanguage = async (query, maxDepth = 4) => {
  const response = await api.post('/api/graph/query', {
    query,
    max_depth: maxDepth,
  });
  return response.data;
};

export const getGraphPath = async (source, target, maxDepth = 5) => {
  const response = await api.get('/api/graph/path', {
    params: { source, target, max_depth: maxDepth },
  });
  return response.data;
};

export const getGraphNeighbors = async (
  entity,
  depth = 1,
  direction = 'both',
  limitNodes = 250
) => {
  const response = await api.get('/api/graph/neighbors', {
    params: {
      entity,
      depth,
      direction,
      limit_nodes: limitNodes,
    },
  });
  return response.data;
};

export const searchGraphEntities = async (q, limit = 10) => {
  const response = await api.get('/api/graph/search', {
    params: { q, limit },
  });
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

export const getGovernmentReports = async (params = {}) => {
  const response = await api.get('/api/government/reports', { params });
  return response.data;
};

export const getGovernmentReportMapData = async (params = {}) => {
  const response = await api.get('/api/government/reports/map-data', { params });
  return response.data;
};

export const getGovernmentReportGeoAnalytics = async (params = {}) => {
  const response = await api.get('/api/government/reports/geo/analytics', { params });
  return response.data;
};

export const getGovernmentReportNearby = async (params = {}) => {
  const response = await api.get('/api/government/reports/geo/nearby', { params });
  return response.data;
};

export const geocodeAddress = async (query, limit = 5) => {
  const response = await api.post('/api/geocode', { query, limit });
  return response.data;
};

export const reverseGeocode = async (latitude, longitude) => {
  const response = await api.get('/api/reverse-geocode', {
    params: { latitude, longitude },
  });
  return response.data;
};

export const getReportDetail = async (reportId) => {
  const response = await api.get(`/api/reports/${reportId}`);
  return response.data;
};

export const getEligibleAssignees = async (reportId) => {
  const response = await api.get(`/api/government/reports/${reportId}/eligible-assignees`);
  return response.data;
};

export const assignGovernmentReport = async (reportId, payload) => {
  const response = await api.post(`/api/government/reports/${reportId}/assign`, payload);
  return response.data;
};

export const updateGovernmentReportStatus = async (reportId, status) => {
  const response = await api.post(`/api/government/reports/${reportId}/status`, { status });
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