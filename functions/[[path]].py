"""
Catch-all handler for Cloudflare Workers - serves static files
"""
import os
from pathlib import Path

try:
    from workers import Response
except ImportError:
    from starlette.responses import Response, FileResponse


# MIME types for common static files
MIME_TYPES = {
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.webp': 'image/webp',
    '.ico': 'image/x-icon',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf',
    '.eot': 'application/vnd.ms-fontobject',
    '.webmanifest': 'application/manifest+json',
}


async def on_request(request, env, context):
    """
    Catch-all handler for serving static files and handling unmatched routes.
    """
    # Get the path from the request
    url = request.url
    path = url.split('?')[0].split('#')[0]  # Remove query and fragment
    
    # Extract the path component after the domain
    if '://' in path:
        path = '/' + path.split('://', 1)[1].split('/', 1)[1] if '/' in path.split('://', 1)[1] else '/'
    
    # Clean up the path
    path = path.strip('/')
    
    # If path is empty, redirect to index
    if not path:
        return Response('', status=302, headers={'Location': '/index.html'})
    
    # Try to serve as static file
    static_dir = Path(__file__).parent.parent / 'gramatike_app' / 'static'
    file_path = static_dir / path
    
    # Security check: ensure the resolved path is within static directory
    try:
        file_path = file_path.resolve()
        static_dir = static_dir.resolve()
        if not str(file_path).startswith(str(static_dir)):
            # Path traversal attempt
            return Response('Forbidden', status=403, headers={'Content-Type': 'text/plain'})
    except Exception:
        return Response('Not Found', status=404, headers={'Content-Type': 'text/plain'})
    
    # Check if file exists
    if file_path.is_file():
        # Determine MIME type
        ext = file_path.suffix.lower()
        content_type = MIME_TYPES.get(ext, 'application/octet-stream')
        
        # Read and return file
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            headers = {
                'Content-Type': content_type,
                'Cache-Control': 'public, max-age=31536000' if ext in ['.css', '.js', '.woff', '.woff2'] else 'public, max-age=3600',
            }
            
            return Response(content, headers=headers)
        except Exception as e:
            return Response(f'Error reading file: {str(e)}', status=500, headers={'Content-Type': 'text/plain'})
    
    # File not found - return 404
    return Response('Not Found', status=404, headers={'Content-Type': 'text/plain'})


handler = on_request
