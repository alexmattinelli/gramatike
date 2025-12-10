"""
Feed page handler for Cloudflare Workers
"""
try:
    from workers import Response
except ImportError:
    from starlette.responses import Response

from ._template_processor import render_template


async def on_request(request, env, context):
    """Handle feed page requests."""
    
    # Get current user from session
    db = getattr(env, 'DB', None) if env else None
    current_user = None
    
    if db:
        try:
            from gramatike_d1.auth import get_current_user
            current_user = await get_current_user(db, request)
        except Exception as e:
            print(f"Error getting current user: {e}")
    
    # If not authenticated, redirect to login
    if not current_user:
        return Response(
            '',
            status=302,
            headers={'Location': '/login'}
        )
    
    # Build profile avatar HTML for header
    username = current_user.get('username', '?')
    user_id = current_user.get('id', 0)
    foto_perfil = current_user.get('foto_perfil', '')
    
    if foto_perfil:
        # Check if absolute URL
        if foto_perfil.startswith('http://') or foto_perfil.startswith('https://'):
            img_src = foto_perfil
        else:
            img_src = f'/static/{foto_perfil}'
        auth_profile_link_html = f'''
    <a href="/perfil" class="profile-avatar-link" aria-label="Meu Perfil" data-tooltip="Meu Perfil">
      <img src="{img_src}" alt="Avatar de {username}" loading="lazy">
    </a>'''
    else:
        initial = username[0].upper() if username else '?'
        auth_profile_link_html = f'''
    <a href="/perfil" class="profile-avatar-link" aria-label="Meu Perfil" data-tooltip="Meu Perfil">
      <span class="initial">{initial}</span>
    </a>'''
    
    # Build admin button HTML (if user is admin)
    is_admin = current_user.get('is_admin', False)
    is_superadmin = current_user.get('is_superadmin', False)
    
    if is_admin or is_superadmin:
        admin_btn_html = '''
      <a href="/admin/" class="search-btn icon-btn" title="Painel Admin" aria-label="Painel Admin">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <rect x="3" y="3" width="7" height="7"></rect>
          <rect x="14" y="3" width="7" height="7"></rect>
          <rect x="14" y="14" width="7" height="7"></rect>
          <rect x="3" y="14" width="7" height="7"></rect>
        </svg>
      </a>'''
    else:
        admin_btn_html = ''
    
    # Build mobile navigation auth HTML
    mobile_nav_auth_html = f'''
  <a href="/perfil" aria-label="Perfil" title="Perfil">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
      <circle cx="12" cy="7" r="4"></circle>
    </svg>
    <span>Perfil</span>
  </a>'''
    
    # Render template with context
    html = render_template(
        'feed.html',
        auth_profile_link_html=auth_profile_link_html,
        admin_btn_html=admin_btn_html,
        admin_painel_btn_html=admin_btn_html,  # Same button for sidebar
        mobile_nav_auth_html=mobile_nav_auth_html,
        user_username_js=username,
        usuarie_id=user_id
    )
    
    return Response(html, headers={'Content-Type': 'text/html; charset=utf-8'})


handler = on_request
