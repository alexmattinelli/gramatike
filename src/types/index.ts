// TypeScript type definitions for Gramátike v3 - Minimalist MVP

export interface Env {
  DB: D1Database;
  R2_BUCKET: R2Bucket;
  SECRET_KEY?: string;
  ENVIRONMENT?: string;
  ASSETS?: any;
}

export interface User {
  id: number;
  username: string;
  email: string;
  password: string;
  name?: string;
  is_admin: number;
  is_banned: number;
  created_at: string;
}

export interface Post {
  id: number;
  user_id: number;
  content: string;
  created_at: string;
}

export interface PostWithUser extends Post {
  username: string;
  name?: string;
}

export interface Session {
  id: number;
  user_id: number;
  token: string;
  created_at: string;
  expires_at: string;
}

export interface AuthContext {
  user: User | null;
  session: Session | null;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
