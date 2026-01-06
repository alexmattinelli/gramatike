// Utility functions
import type { ApiResponse } from '../types';

/**
 * Create a JSON response
 */
export function jsonResponse<T>(
  data: T,
  status = 200,
  headers: Record<string, string> = {}
): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...headers
    }
  });
}

/**
 * Create a success API response
 */
export function successResponse<T>(
  data: T,
  message?: string,
  status = 200
): Response {
  const response: ApiResponse<T> = {
    success: true,
    data,
    ...(message && { message })
  };
  return jsonResponse(response, status);
}

/**
 * Create an error API response
 */
export function errorResponse(
  error: string,
  status = 400
): Response {
  const response: ApiResponse = {
    success: false,
    error
  };
  return jsonResponse(response, status);
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Sanitize HTML to prevent XSS
 */
export function sanitizeHtml(html: string): string {
  return html
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
}

/**
 * Get client IP from request
 */
export function getClientIp(request: Request): string {
  return request.headers.get('CF-Connecting-IP') || 
         request.headers.get('X-Forwarded-For')?.split(',')[0] ||
         'unknown';
}

/**
 * Get user agent from request
 */
export function getUserAgent(request: Request): string {
  return request.headers.get('User-Agent') || 'unknown';
}

/**
 * Parse request body as JSON
 */
export async function parseJsonBody<T = any>(request: Request): Promise<T | null> {
  try {
    const body = await request.json();
    return body as T;
  } catch (error) {
    console.error('Error parsing JSON body:', error);
    return null;
  }
}

/**
 * Get query parameter from URL
 */
export function getQueryParam(request: Request, param: string): string | null {
  const url = new URL(request.url);
  return url.searchParams.get(param);
}

/**
 * Get multiple query parameters
 */
export function getQueryParams(request: Request, ...params: string[]): Record<string, string | null> {
  const url = new URL(request.url);
  const result: Record<string, string | null> = {};
  
  for (const param of params) {
    result[param] = url.searchParams.get(param);
  }
  
  return result;
}

/**
 * Format date to ISO string
 */
export function formatDate(date: Date | string): string {
  if (typeof date === 'string') {
    return new Date(date).toISOString();
  }
  return date.toISOString();
}

/**
 * Validate content for moderation
 */
export function validateContent(content: string): { valid: boolean; error?: string } {
  if (!content || content.trim().length === 0) {
    return { valid: false, error: 'Conteúdo não pode estar vazio' };
  }
  
  if (content.length > 5000) {
    return { valid: false, error: 'Conteúdo muito longo (máximo 5000 caracteres)' };
  }
  
  return { valid: true };
}

/**
 * Build file path for R2 storage
 */
export function buildAvatarPath(userId: number, filename: string): string {
  const timestamp = Date.now();
  const ext = filename.split('.').pop() || 'jpg';
  return `avatars/${userId}/${timestamp}.${ext}`;
}

export function buildPostImagePath(userId: number, filename: string): string {
  const timestamp = Date.now();
  const ext = filename.split('.').pop() || 'jpg';
  return `posts/${userId}/${timestamp}.${ext}`;
}

export function buildApostilaPath(filename: string): string {
  const timestamp = Date.now();
  const ext = filename.split('.').pop() || 'pdf';
  return `apostilas/${timestamp}_${filename}`;
}

/**
 * Upload file to R2 storage
 */
export async function uploadToR2(
  bucket: R2Bucket,
  path: string,
  data: ArrayBuffer | ReadableStream,
  contentType?: string
): Promise<string | null> {
  try {
    await bucket.put(path, data, {
      httpMetadata: contentType ? { contentType } : undefined
    });
    
    // Return the public URL (adjust based on your R2 configuration)
    return `https://storage.gramatike.com/${path}`;
  } catch (error) {
    console.error('Error uploading to R2:', error);
    return null;
  }
}

/**
 * Delete file from R2 storage
 */
export async function deleteFromR2(
  bucket: R2Bucket,
  path: string
): Promise<boolean> {
  try {
    await bucket.delete(path);
    return true;
  } catch (error) {
    console.error('Error deleting from R2:', error);
    return false;
  }
}
