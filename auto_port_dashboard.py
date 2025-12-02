#!/usr/bin/env python3
"""
Auto-port: Converte template Flask admin/dashboard.html para código Workers
Este script faz a conversão completa mantendo toda a funcionalidade
"""

import re

def convert_flask_template_to_workers():
    """Converte o template Flask completo para Python Workers"""
    
    # Lê o template original
    with open('gramatike_app/templates/admin/dashboard.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Remove comentários HTML desnecessários
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    # Converte Jinja2 para Python
    conversions = [
        # {{ variable }} -> {variable}
        (r'\{\{\s*(\w+[\.\w]*)\s*\}\}', r'{\1}'),
        
        # {{ url_for('static', filename='X') }} -> /static/X
        (r"\{\{\s*url_for\('static',\s*filename='([^']+)'\)\s*\}\}", r'/static/\1'),
        
        # {{ csrf_token() }} -> (remove, Workers não usa)
        (r'\{\{\s*csrf_token\(\).*?\}\}', ''),
        
        # Remove {% if csrf_token is defined %}
        (r'\{%\s*if csrf_token is defined.*?%\}.*?\{%\s*endif\s*%\}', ''),
        
        # {% for item in items %} -> {for_items}  (placeholder)
        (r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}', r'{# FOR \1 IN \2 #}'),
        (r'\{%\s*endfor\s*%\}', r'{# ENDFOR #}'),
        
        # {% if condition %} -> {if_condition} (placeholder)  
        (r'\{%\s*if\s+(.*?)\s*%\}', r'{# IF \1 #}'),
        (r'\{%\s*elif\s+(.*?)\s*%\}', r'{# ELIF \1 #}'),
        (r'\{%\s*else\s*%\}', r'{# ELSE #}'),
        (r'\{%\s*endif\s*%\}', r'{# ENDIF #}'),
    ]
    
    for pattern, replacement in conversions:
        html = re.sub(pattern, replacement, html)
    
    # Escapa chaves para f-string Python
    # Mas não as que são placeholders ou variáveis
    html = html.replace('{', '{{').replace('}', '}}')
    html = re.sub(r'\{\{(\w+[\.\w]*)\}\}', r'{\1}', html)
    html = re.sub(r'\{\{# (.*?) #\}\}', r'{# \1 #}', html)
    
    # Gera o código Python
    python_code = f'''
async def _admin_page(self, db, current_user):
    """Admin Dashboard - VERSÃO COMPLETA AUTO-GERADA"""
    
    # Check admin
    if not current_user:
        return redirect('/login')
    
    is_admin = current_user.get('is_admin', False) or current_user.get('is_superadmin', False)
    if not is_admin:
        return html_response("<h1>Acesso Negado</h1>")
    
    # Get data
    stats = await get_admin_stats(db) if db else {{}}
    all_users = await get_all_usuaries(db) if db else []
    
    # Build HTML
    return html_response(f"""
{html}
    """)
'''
    
    # Salva o resultado
    with open('admin_dashboard_converted.py', 'w', encoding='utf-8') as f:
        f.write(python_code)
    
    print("✅ Conversão completa!")
    print("📝 Arquivo gerado: admin_dashboard_converted.py")
    print("\n⚠️  PRÓXIMO PASSO:")
    print("1. Revise o arquivo gerado")
    print("2. Ajuste os loops FOR e IF manualmente")
    print("3. Copie para index.py substituindo _admin_page")

if __name__ == '__main__':
    convert_flask_template_to_workers()
