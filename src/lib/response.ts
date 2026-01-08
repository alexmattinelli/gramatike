// Response helper utilities for Gramátike v2

export function jsonResponse(data: any, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' }
  });
}

export function errorResponse(error: string, status = 400): Response {
  return jsonResponse({ error }, status);
}

export function successResponse(message: string, data?: any): Response {
  return jsonResponse({ success: true, message, ...data });
}

export function htmlResponse(html: string, status = 200): Response {
  return new Response(html, {
    status,
    headers: { 'Content-Type': 'text/html; charset=utf-8' }
  });
}

export function redirectResponse(url: string, status = 302): Response {
  return new Response(null, {
    status,
    headers: { 'Location': url }
  });
}
