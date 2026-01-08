// TypeScript type definitions for Gramátike v3 - Minimalist MVP
// This file provides type declarations for TypeScript

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
  expires_at: string;
  created_at: string;
}

export interface Env {
  DB: D1Database;
  R2_BUCKET: R2Bucket;
  SECRET_KEY?: string;
  ENVIRONMENT?: string;
  ASSETS?: any;
}

export interface AuthContext {
  user: User | null;
  session: Session | null;
}

// Extend EventContext to include our custom data
declare module '@cloudflare/workers-types' {
  interface EventContext<Env, P, Data> {
    data: Data & {
      user?: User | null;
      session?: Session | null;
    };
  }
}
