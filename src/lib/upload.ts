// R2 Upload Handler
// Handles file uploads to Cloudflare R2 storage

import type { R2Bucket } from '@cloudflare/workers-types';

/**
 * Upload a file to R2 storage
 * @param bucket R2 bucket instance
 * @param file File to upload
 * @param userId User ID for organizing files
 * @param folder Folder name (e.g., 'uploads', 'avatars')
 * @returns Public URL of the uploaded file or null if failed
 */
export async function uploadToR2(
  bucket: R2Bucket,
  file: File,
  userId: number,
  folder: string = 'uploads'
): Promise<string | null> {
  try {
    // Generate unique filename with timestamp
    const timestamp = Date.now();
    const sanitizedFilename = file.name.replace(/[^a-zA-Z0-9.-]/g, '_');
    const filename = `${folder}/${userId}/${timestamp}-${sanitizedFilename}`;
    
    // Convert file to array buffer
    const arrayBuffer = await file.arrayBuffer();
    
    // Upload to R2
    await bucket.put(filename, arrayBuffer, {
      httpMetadata: {
        contentType: file.type || 'application/octet-stream'
      }
    });
    
    return filename;
  } catch (error) {
    console.error('[uploadToR2] Error:', error);
    return null;
  }
}

/**
 * Get public URL for an R2 file
 * @param filename File path in R2
 * @param publicUrl Public URL base from environment
 * @returns Full public URL
 */
export function getPublicUrl(filename: string, publicUrl: string): string {
  // Remove trailing slash from public URL if present
  const baseUrl = publicUrl.endsWith('/') ? publicUrl.slice(0, -1) : publicUrl;
  
  // Ensure filename starts with /
  const path = filename.startsWith('/') ? filename : `/${filename}`;
  
  return `${baseUrl}${path}`;
}

/**
 * Delete a file from R2 storage
 * @param bucket R2 bucket instance
 * @param filename File path to delete
 * @returns true if successful, false otherwise
 */
export async function deleteFromR2(
  bucket: R2Bucket,
  filename: string
): Promise<boolean> {
  try {
    await bucket.delete(filename);
    return true;
  } catch (error) {
    console.error('[deleteFromR2] Error:', error);
    return false;
  }
}

/**
 * Validate file type
 * @param file File to validate
 * @param allowedTypes Allowed MIME types
 * @returns true if valid, false otherwise
 */
export function validateFileType(file: File, allowedTypes: string[]): boolean {
  return allowedTypes.some(type => {
    if (type.endsWith('/*')) {
      // Wildcard type (e.g., 'image/*')
      const baseType = type.split('/')[0];
      return file.type.startsWith(`${baseType}/`);
    }
    return file.type === type;
  });
}

/**
 * Validate file size
 * @param file File to validate
 * @param maxSize Maximum size in bytes
 * @returns true if valid, false otherwise
 */
export function validateFileSize(file: File, maxSize: number): boolean {
  return file.size <= maxSize;
}

/**
 * Default allowed image types
 */
export const ALLOWED_IMAGE_TYPES = [
  'image/jpeg',
  'image/jpg',
  'image/png',
  'image/gif',
  'image/webp'
];

/**
 * Default max file size (5MB)
 */
export const MAX_FILE_SIZE = 5 * 1024 * 1024;
