// functions/types.ts
export interface Env {
  DB: D1Database;
  ASSETS: Fetcher;
  // Adicione outros bindings se tiver
}

export interface User {
  id: number;
  username: string;
  email?: string;
  name?: string;
  avatar_initials?: string;
  verified?: boolean;
  online_status?: boolean;
  role?: 'user' | 'admin' | 'moderator';
  created_at?: string;
}

export interface Session {
  id: string;
  user_id: number;
  expires_at: string;
}

export interface AuthContext {
  user: User | null;
  session: Session | null;
}

export interface Post {
  id: number;
  user_id: number;
  content: string;
  likes: number;
  comments: number;
  created_at: string;
  updated_at?: string;
}

// Para respostas da API
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
