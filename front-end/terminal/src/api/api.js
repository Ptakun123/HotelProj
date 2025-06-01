import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000',
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  console.log('[API] token from storage:', token);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  console.log('[API] final headers:', config.headers);
  return config;
});

export default api;