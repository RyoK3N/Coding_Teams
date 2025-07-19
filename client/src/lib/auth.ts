export interface AuthUser {
  id: string;
  username: string;
  role: string;
  email?: string;
}

export const auth = {
  getToken(): string | null {
    return localStorage.getItem('auth_token');
  },

  getUser(): AuthUser | null {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },

  isAuthenticated(): boolean {
    return !!this.getToken() && !!this.getUser();
  },

  logout(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    // Use a more reliable redirect method
    window.location.replace('/login');
  },

  setAuth(token: string, user: AuthUser): void {
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user', JSON.stringify(user));
  },
};