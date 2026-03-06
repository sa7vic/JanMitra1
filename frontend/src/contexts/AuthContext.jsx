import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../lib/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

const API_URL = API_BASE_URL;

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/auth/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error.response?.status);
      
      if (error.response?.status === 422 || error.response?.status === 401) {
        localStorage.removeItem('token');
        delete axios.defaults.headers.common['Authorization'];
        setUser(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      
      const response = await axios.post(`${API_URL}/api/auth/login`, {
        email,
        password,
      });
      
      const { token, user: userData } = response.data;
      
      if (!token) {
        throw new Error('No token received from server');
      }
      
      localStorage.setItem('token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setUser(userData);
      
      return userData;
    } catch (error) {
      console.error('Login error:', error.response?.data || error.message);
      throw error;
    }
  };

  const register = async (email, password, name, role = 'citizen') => {
    try {
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      
      const response = await axios.post(`${API_URL}/api/auth/register`, {
        email,
        password,
        name,
        role,
      });
      
      const { token, user: userData } = response.data;
      
      if (!token) {
        throw new Error('No token received from server');
      }
      
      localStorage.setItem('token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setUser(userData);
      
      return userData;
    } catch (error) {
      console.error('Register error:', error.response?.data || error.message);
      throw error;
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await axios.put(`${API_URL}/api/auth/profile`, profileData);
      setUser(response.data.user);
      return response.data.user;
    } catch (error) {
      console.error('Profile update error:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      login, 
      register, 
      logout,
      updateProfile,
      loading, 
      isAuthenticated: !!user 
    }}>
      {children}
    </AuthContext.Provider>
  );
};