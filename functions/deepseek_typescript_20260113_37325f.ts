// functions/types.ts
export interface Env {
  DB: D1Database;
  ASSETS: Fetcher;
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