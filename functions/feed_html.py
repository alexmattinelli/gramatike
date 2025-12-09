"""
Feed page handler for Cloudflare Workers
"""
try:
    from workers import Response
except ImportError:
    from starlette.responses import Response

from ._template_processor import render_template
from gramatike_d1.auth import get_current_user


async def on_request(request, env, context):
    """Handle feed page requests - requires authentication."""
    # Check if user is authenticated
    db = getattr(env, 'DB', None) if env else None
    user = None
    
    if db:
        try:
            user = await get_current_user(db, request)
            if not user:
                # User not authenticated - redirect to login
                return Response(
                    '',
                    status=302,
                    headers={'Location': '/login.html'}
                )
        except Exception as e:
            print(f"[Feed] Error checking authentication: {type(e).__name__}")
            # Authentication check failed - redirect to login
            return Response(
                '',
                status=302,
                headers={'Location': '/login.html'}
            )
    else:
        print("[Feed] DB not available - redirecting to login")
        # DB not available - redirect to login
        return Response(
            '',
            status=302,
            headers={'Location': '/login.html'}
        )
    
    # User is authenticated - show feed
    html = render_template('feed.html')
    return Response(html, headers={'Content-Type': 'text/html; charset=utf-8'})


handler = on_request
