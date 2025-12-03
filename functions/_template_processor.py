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


