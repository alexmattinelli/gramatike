"""
Template Loader for Cloudflare Workers

Loads pre-converted templates from functions/templates/ directory.
Templates have already been converted from Flask/Jinja2 to static HTML.
"""

import os
import re

# Base path for converted templates
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')


def load_template(template_name):
    """
    Load a converted template file.
    
    Args:
        template_name: Name of template file (e.g., 'login.html')
    
    Returns:
        Template HTML string
    """
    template_path = os.path.join(TEMPLATES_DIR, template_name)
    
    if not os.path.exists(template_path):
        return f"<h1>Template não encontrado: {template_name}</h1>"
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def render_template(template_name, **context):
    """
    Load a template and replace placeholders with actual values.
    
    Args:
        template_name: Name of template file
        **context: Variables to substitute
    
    Returns:
        Processed HTML string
    """
    html = load_template(template_name)
    
    # Replace FLASH_MESSAGES_PLACEHOLDER with actual flash messages
    flash_html = context.get('flash_html', '')
    html = html.replace('<!-- FLASH_MESSAGES_PLACEHOLDER -->', flash_html)
    
    # Replace CONTENT_PLACEHOLDER with dynamic content
    content_html = context.get('content_html', '')
    html = html.replace('<!-- CONTENT_PLACEHOLDER -->', content_html)
    
    # Replace FEED_PLACEHOLDER with feed posts
    feed_html = context.get('feed_html', '')
    html = html.replace('<!-- FEED_PLACEHOLDER -->', feed_html)
    
    # Replace DIVULGACOES_PLACEHOLDER with divulgacoes
    divulgacoes_html = context.get('divulgacoes_html', '')
    html = html.replace('<!-- DIVULGACOES_PLACEHOLDER -->', divulgacoes_html)
    
    # Replace ADMIN_BTN_PLACEHOLDER with admin button if present
    admin_btn_html = context.get('admin_btn_html', '')
    html = html.replace('<!-- ADMIN_BTN_PLACEHOLDER -->', admin_btn_html)
    
    # Replace ADMIN_PAINEL_BTN_PLACEHOLDER with admin painel button if present
    admin_painel_btn_html = context.get('admin_painel_btn_html', admin_btn_html)
    html = html.replace('<!-- ADMIN_PAINEL_BTN_PLACEHOLDER -->', admin_painel_btn_html)
    
    # Replace AUTH_PROFILE_LINK_PLACEHOLDER with profile link for authenticated users
    auth_profile_link_html = context.get('auth_profile_link_html', '')
    html = html.replace('<!-- AUTH_PROFILE_LINK_PLACEHOLDER -->', auth_profile_link_html)
    
    # Replace MOBILE_NAV_AUTH_PLACEHOLDER with mobile nav auth section
    mobile_nav_auth_html = context.get('mobile_nav_auth_html', '')
    html = html.replace('<!-- MOBILE_NAV_AUTH_PLACEHOLDER -->', mobile_nav_auth_html)
    
    # Replace EMAIL_STATUS_PLACEHOLDER with email confirmation status
    email_status_html = context.get('email_status_html', '')
    html = html.replace('<!-- EMAIL_STATUS_PLACEHOLDER -->', email_status_html)
    
    # Replace FOOTER_PLACEHOLDER with page footer
    footer_html = context.get('footer_html', '')
    html = html.replace('<!-- FOOTER_PLACEHOLDER -->', footer_html)
    
    # Replace EXTRA_CSS_PLACEHOLDER with additional CSS
    extra_css = context.get('extra_css', '')
    html = html.replace('<!-- EXTRA_CSS_PLACEHOLDER -->', f'<style>{extra_css}</style>' if extra_css else '')
    
    # Replace user-related placeholders
    user_foto = context.get('user_foto', '/static/img/perfil.png')
    html = html.replace('<!-- USER_FOTO_PLACEHOLDER -->', user_foto)
    
    user_username_js = context.get('user_username_js', '')
    html = html.replace('<!-- USER_USERNAME_JS_PLACEHOLDER -->', user_username_js)
    
    user_id = context.get('user_id', 0)
    html = html.replace('<!-- USER_ID_PLACEHOLDER -->', str(user_id))
    
    # Replace admin-specific placeholders
    total_users = context.get('total_users', 0)
    html = html.replace('<!-- TOTAL_USERS_PLACEHOLDER -->', str(total_users))
    
    total_posts = context.get('total_posts', 0)
    html = html.replace('<!-- TOTAL_POSTS_PLACEHOLDER -->', str(total_posts))
    
    total_comments = context.get('total_comments', 0)
    html = html.replace('<!-- TOTAL_COMMENTS_PLACEHOLDER -->', str(total_comments))
    
    users_table_html = context.get('users_table_html', '')
    html = html.replace('<!-- USERS_TABLE_PLACEHOLDER -->', users_table_html)
    
    # Replace VAR placeholders: <!-- VAR: name --> with actual values
    for key, value in context.items():
        if key not in ['flash_html', 'content_html', 'feed_html', 'divulgacoes_html', 'user', 'current_user']:
            placeholder = f'<!-- VAR: {key} -->'
            html = html.replace(placeholder, str(value) if value else '')
    
    # Replace USER placeholders: <!-- USER_username --> etc
    user = context.get('user') or context.get('current_user')
    if user:
        if isinstance(user, dict):
            for attr in ['username', 'nome', 'email', 'foto_perfil', 'bio', 'id']:
                placeholder = f'<!-- USER_{attr} -->'
                html = html.replace(placeholder, str(user.get(attr, '')) if user.get(attr) else '')
    
    return html


def create_error_html(message):
    """Create a styled error message HTML snippet."""
    return f'''<ul class="flash-messages"><li class="flash-error">{message}</li></ul>'''


def create_success_html(message):
    """Create a styled success message HTML snippet."""
    return f'''<ul class="flash-messages"><li class="flash-success">{message}</li></ul>'''


