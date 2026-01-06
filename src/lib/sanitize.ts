// Sanitization utilities for Cloudflare D1
// D1 does not accept 'undefined' values - only null, numbers, strings, or buffers

/**
 * Sanitizes a value for D1 - converts undefined to null
 * @param value - The value to sanitize
 * @returns The sanitized value (null if undefined)
 */
export function sanitizeForD1<T>(value: T | undefined | null): T | null {
  if (value === undefined) {
    return null;
  }
  if (value === null) {
    return null;
  }
  return value;
}

/**
 * Sanitizes multiple parameters for D1
 * @param params - The parameters to sanitize
 * @returns Array of sanitized parameters
 */
export function sanitizeParams(...params: any[]): any[] {
  return params.map(p => sanitizeForD1(p));
}

/**
 * Sanitizes an object's properties for D1
 * Useful for update operations where you have multiple optional fields
 * @param obj - Object with properties to sanitize
 * @returns Object with sanitized properties
 */
export function sanitizeObject<T extends Record<string, any>>(obj: T): Record<string, any> {
  const result: Record<string, any> = {};
  for (const [key, value] of Object.entries(obj)) {
    result[key] = sanitizeForD1(value);
  }
  return result;
}
