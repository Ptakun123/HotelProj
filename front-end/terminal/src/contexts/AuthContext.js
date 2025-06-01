import React, { createContext, useState, useContext } from 'react';
import api from '../api/api';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('user');
    return stored ? JSON.parse(stored) : null;
  });

  const login = async (email, password) => {
    const { data } = await api.post('/login', { email, password });
    if (!data.user || !data.user.id_user) throw new Error('Brak id_user w odpowiedzi backendu');
    setUser(data.user);
    localStorage.setItem('user', JSON.stringify(data.user));
    localStorage.setItem('token', data.access_token);
    return data;
  };

  const register = async (formData) => {
    const { data } = await api.post('/register', formData, {
      headers: {
        "Content-Type": "application/json",
      },
    });
    setUser(data.user);
    localStorage.setItem('user', JSON.stringify(data.user));
    if (data.access_token) {
      localStorage.setItem('token', data.access_token);
    }
    return data;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

export { AuthContext };
