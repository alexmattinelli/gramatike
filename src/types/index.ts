// TypeScript type definitions for Gramátike

export interface Env {
  DB: D1Database;
  R2_BUCKET: R2Bucket;
  SECRET_KEY?: string;
  ENVIRONMENT?: string;
}

export interface User {
  id: number;
  nome?: string;
  username: string;
  email: string;
  password: string;
  email_confirmed: number;
  email_confirmed_at?: string;
  foto_perfil: string;
  genero?: string;
  pronome?: string;
  bio?: string;
  data_nascimento?: string;
  created_at: string;
  is_admin: number;
  is_superadmin: number;
  is_banned: number;
  banned_at?: string;
  ban_reason?: string;
  suspended_until?: string;
}

export interface Post {
  id: number;
  usuarie?: string;
  usuarie_id?: number;
  conteudo?: string;
  imagem?: string;
  data: string;
  is_deleted: number;
  deleted_at?: string;
  deleted_by?: number;
}

export interface PostWithUser extends Post {
  username?: string;
  foto_perfil?: string;
  like_count?: number;
  comment_count?: number;
  user_liked?: boolean;
}

export interface Comment {
  id: number;
  usuarie_id?: number;
  post_id: number;
  conteudo: string;
  data?: string;
  parent_id?: number;
}

export interface Session {
  id: number;
  user_id: number;
  token: string;
  created_at: string;
  expires_at: string;
  user_agent?: string;
  ip_address?: string;
}

export interface EduContent {
  id: number;
  tipo: string;
  titulo: string;
  conteudo?: string;
  resumo?: string;
  imagem?: string;
  arquivo_url?: string;
  link?: string;
  data: string;
  autor_id?: number;
  tema_id?: number;
  is_deleted: number;
}

export interface AuthResult {
  success: boolean;
  user?: User;
  token?: string;
  error?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
