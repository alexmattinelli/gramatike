// Logging utilities for debugging and monitoring

/**
 * Helper to format data for logging
 * @param data - Data to format
 * @returns Formatted data or empty string if undefined
 */
function formatData(data: any): any {
  return data !== undefined ? data : '';
}

/**
 * Log an error with context and details
 * @param context - The context where the error occurred (e.g., 'createPost', 'login')
 * @param error - The error object or message
 * @param additionalData - Optional additional data to log
 */
export function logError(context: string, error: unknown, additionalData?: Record<string, any>) {
  console.error(`[${context}] Error:`, error);
  
  if (error instanceof Error) {
    console.error(`[${context}] Stack:`, error.stack);
    console.error(`[${context}] Message:`, error.message);
  }
  
  if (additionalData) {
    try {
      console.error(`[${context}] Additional data:`, JSON.stringify(additionalData, null, 2));
    } catch (e) {
      console.error(`[${context}] Additional data (not serializable):`, additionalData);
    }
  }
}

/**
 * Log debug information
 * @param context - The context for the log message
 * @param message - The debug message
 * @param data - Optional data to include
 */
export function logDebug(context: string, message: string, data?: any) {
  console.log(`[${context}] ${message}`, formatData(data));
}

/**
 * Log a warning
 * @param context - The context for the warning
 * @param message - The warning message
 * @param data - Optional data to include
 */
export function logWarning(context: string, message: string, data?: any) {
  console.warn(`[${context}] ${message}`, formatData(data));
}

/**
 * Log successful operations
 * @param context - The context for the success message
 * @param message - The success message
 * @param data - Optional data to include
 */
export function logSuccess(context: string, message: string, data?: any) {
  console.log(`[${context}] ✓ ${message}`, formatData(data));
}

/**
 * Log API request details
 * @param method - HTTP method
 * @param path - Request path
 * @param userId - Optional user ID making the request
 * @param additionalData - Optional additional data
 */
export function logRequest(
  method: string,
  path: string,
  userId?: number,
  additionalData?: Record<string, any>
) {
  const data = {
    method,
    path,
    userId,
    timestamp: new Date().toISOString(),
    ...additionalData
  };
  try {
    console.log('[API Request]', JSON.stringify(data));
  } catch (e) {
    console.log('[API Request]', data);
  }
}

/**
 * Log D1 database operations
 * @param operation - The database operation (e.g., 'INSERT', 'UPDATE', 'SELECT')
 * @param table - The table being operated on
 * @param details - Optional details about the operation
 */
export function logDbOperation(
  operation: string,
  table: string,
  details?: Record<string, any>
) {
  console.log(`[D1 ${operation}] Table: ${table}`, details || '');
}
