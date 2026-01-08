// TypeScript type definitions for Gramátike v2

export interface User {
  id: number;
  username: string;
  email: string;
  password: string;
  name?: string;
  bio?: string;
  avatar?: string;
  is_admin: number;
  is_banned: number;
  created_at: string;
  updated_at: string;
}

export interface Post {
  id: number;
  user_id: number;
  content: string;
  image?: string;
  created_at: string;
  updated_at: string;
  // Joined fields
  username?: string;
  name?: string;
  avatar?: string;
  likes_count?: number;
  comments_count?: number;
  user_liked?: boolean;
}

export interface Comment {
  id: number;
  user_id: number;
  post_id: number;
  content: string;
  created_at: string;
  // Joined fields
  username?: string;
  name?: string;
  avatar?: string;
}

export interface Like {
  id: number;
  user_id: number;
  post_id: number;
  created_at: string;
}

export interface Session {
  id: number;
  user_id: number;
  token: string;
  expires_at: string;
  created_at: string;
}

export interface Env {
  DB: D1Database;
  R2_BUCKET: R2Bucket;
  SECRET_KEY?: string;
}

export interface AuthContext {
  user: User | null;
  session: Session | null;
}
