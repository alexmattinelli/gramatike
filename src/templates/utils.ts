// Template utility functions for HTML escaping and asset URLs

/**
 * Escape HTML special characters to prevent XSS
 */
export function escapeHtml(text: string | undefined | null): string {
  if (!text) return '';
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.toString().replace(/[&<>"']/g, m => map[m]);
}

/**
 * Get asset URL, handling both static paths and external URLs
 */
export function getAssetUrl(path: string | undefined | null): string {
  if (!path) return '/static/img/perfil.png';
  const clean = path.replace(/^\//, '');
  if (clean.startsWith('http')) return clean;
  return `/static/${clean}`;
}
