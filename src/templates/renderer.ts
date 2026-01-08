// Template Renderer Helper
// Simple template rendering with variable substitution

import type { Env } from '../types';

/**
 * Render a template with data
 * @param templatePath Path to template file
 * @param data Data to inject into template
 * @param env Cloudflare environment
 * @returns Rendered HTML string
 */
export async function renderTemplate(
  templatePath: string,
  data: Record<string, any>,
  env: any // Using any for now since ASSETS is not in Env type
): Promise<string> {
  try {
    // Fetch template from assets
    const templateUrl = templatePath.startsWith('/') 
      ? `https://placeholder.local${templatePath}` 
      : `https://placeholder.local/${templatePath}`;
    
    const response = await env.ASSETS.fetch(templateUrl);
    
    if (!response.ok) {
      throw new Error(`Template not found: ${templatePath}`);
    }
    
    let html = await response.text();
    
    // Simple variable substitution: {{variable}}
    html = html.replace(/\{\{(\w+)\}\}/g, (_match: string, key: string) => {
      return data[key] !== undefined ? String(data[key]) : _match;
    });
    
    // Conditional rendering: {{#if condition}}...{{/if}}
    html = html.replace(/\{\{#if\s+(\w+)\}\}([\s\S]*?)\{\{\/if\}\}/g, (_match: string, key: string, content: string) => {
      return data[key] ? content : '';
    });
    
    // Loop rendering: {{#each items}}...{{/each}}
    // Note: This is a simplified version
    html = html.replace(/\{\{#each\s+(\w+)\}\}([\s\S]*?)\{\{\/each\}\}/g, (_match: string, key: string, template: string) => {
      const items = data[key];
      if (!Array.isArray(items)) return '';
      
      return items.map(item => {
        let itemHtml = template;
        // Replace item.property with actual values
        itemHtml = itemHtml.replace(/\{\{(\w+)\}\}/g, (_m: string, prop: string) => {
          return item[prop] !== undefined ? String(item[prop]) : _m;
        });
        return itemHtml;
      }).join('');
    });
    
    return html;
  } catch (error) {
    console.error('[renderTemplate] Error:', error);
    throw error;
  }
}

/**
 * Load and include a partial template
 * @param partialPath Path to partial template
 * @param data Data for the partial
 * @param env Cloudflare environment
 * @returns Rendered partial HTML
 */
export async function includePartial(
  partialPath: string,
  data: Record<string, any>,
  env: any
): Promise<string> {
  return renderTemplate(partialPath, data, env);
}

/**
 * Escape HTML to prevent XSS
 * @param unsafe Unsafe HTML string
 * @returns Escaped HTML string
 */
export function escapeHtml(unsafe: string): string {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Format date for display
 * @param date Date to format
 * @returns Formatted date string
 */
export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}
