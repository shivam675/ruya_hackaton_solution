import { create } from 'zustand';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
}

// Helper to safely access localStorage
const getStoredToken = (): string | null => {
  try {
    return localStorage.getItem('access_token');
  } catch (e) {
    console.warn('localStorage not available:', e);
    return null;
  }
};

const setStoredToken = (token: string): void => {
  try {
    localStorage.setItem('access_token', token);
  } catch (e) {
    console.warn('localStorage not available:', e);
  }
};

const removeStoredToken = (): void => {
  try {
    localStorage.removeItem('access_token');
  } catch (e) {
    console.warn('localStorage not available:', e);
  }
};

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: getStoredToken(),
  isAuthenticated: !!getStoredToken(),
  
  login: async (email: string, password: string) => {
    const { authAPI } = await import('@/lib/api');
    const data = await authAPI.login(email, password);
    setStoredToken(data.access_token);
    
    // Fetch user info
    const user = await authAPI.getCurrentUser();
    
    set({
      token: data.access_token,
      user,
      isAuthenticated: true,
    });
  },
  
  logout: () => {
    removeStoredToken();
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  },
  
  setUser: (user: User) => {
    set({ user });
  },
}));
