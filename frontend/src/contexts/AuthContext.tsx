import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface User {
  name: string;
  email: string;
  role: string;
  initials: string;
  provider?: string;
  username?: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (type?: 'email' | 'github') => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const DEFAULT_USER: User = {
  name: 'Demo Engineer',
  email: 'demo@infrashift.dev',
  role: 'Platform Engineer',
  initials: 'DE',
  provider: 'email',
};

const GITHUB_USER: User = {
  name: 'GitHub Demo User',
  email: 'demo@infrashift.dev',
  role: 'Platform Engineer',
  initials: 'GH',
  provider: 'github',
  username: 'github-demo',
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);
  
  // Check localStorage on mount
  useEffect(() => {
    const isDemoAuthed = localStorage.getItem('infrashift_demo_auth') === 'true';
    const authType = localStorage.getItem('infrashift_demo_auth_type');
    
    if (isDemoAuthed) {
      setIsAuthenticated(true);
      setUser(authType === 'github' ? GITHUB_USER : DEFAULT_USER);
    }
  }, []);

  const login = (type: 'email' | 'github' = 'email') => {
    localStorage.setItem('infrashift_demo_auth', 'true');
    localStorage.setItem('infrashift_demo_auth_type', type);
    setIsAuthenticated(true);
    setUser(type === 'github' ? GITHUB_USER : DEFAULT_USER);
  };

  const logout = () => {
    localStorage.removeItem('infrashift_demo_auth');
    localStorage.removeItem('infrashift_demo_auth_type');
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
