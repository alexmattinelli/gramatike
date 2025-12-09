"""
Index (home) page handler for Cloudflare Workers
"""
try:
    from workers import Response
except ImportError:
    from starlette.responses import Response

from ._template_processor import render_template


async def on_request(request, env, context):
    """Handle home page requests."""
    # Check if user is authenticated
    from gramatike_d1.auth import get_current_user
    
    db = getattr(env, 'DB', None) if env else None
    user = None
    
    if db:
        try:
            user = await get_current_user(db, request)
            if user:
                print(f"[Index] User authenticated: {user.get('username')} (ID: {user.get('id')}) - showing feed.html")
            else:
                print("[Index] User not authenticated - showing landing.html")
        except Exception as e:
            print(f"[Index] Error checking authentication: {type(e).__name__}: {str(e)}")
    else:
        print("[Index] DB not available - showing landing.html")
    
    # Show feed.html for authenticated users, landing.html for guests
    template = 'feed.html' if user else 'landing.html'
    html = render_template(template)
    return Response(html, headers={'Content-Type': 'text/html; charset=utf-8'})


handler = on_request
