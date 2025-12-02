#!/usr/bin/env python3
"""
🚀 CONVERSOR AUTOMÁTICO: Flask Template → Workers Code

Este script converte QUALQUER template Jinja2 para código Python Workers pronto.

Uso:
    python converter_template.py gramatike_app/templates/exercicios.html > codigo_exercicios_workers.py
    python converter_template.py gramatike_app/templates/artigos.html > codigo_artigos_workers.py
"""

import sys
import re
from pathlib import Path


def extract_function_name(template_path):
    """Extrai o nome da função baseado no nome do arquivo."""
    stem = Path(template_path).stem
    return f"_{stem}_page"


def convert_url_for(html):
    """Converte url_for para paths diretos."""
    html = re.sub(
        r"{{\s*url_for\('static',\s*filename=['\"]([^'\"]+)['\"]\)\s*}}",
        r"/static/\1",
        html
    )
    
    url_map = {
        "main.educacao": "/educacao",
        "main.exercicios": "/exercicios",
        "main.artigos": "/artigos",
        "main.apostilas": "/apostilas",
        "main.podcasts": "/podcasts",
        "main.dinamicas_home": "/dinamicas",
        "main.redacao": "/redacao",
        "main.videos": "/videos",
        "admin.dashboard": "/admin/dashboard",
        "main.login": "/login",
        "main.configuracoes": "/configuracoes",
        "main.meu_perfil": "/meu_perfil",
    }
    
    for route, path in url_map.items():
        html = re.sub(
            rf"{{{{\s*url_for\(['\"]{ re.escape(route)}['\"](?:,\s*[^}}]*)?\)\s*}}}}",
            path,
            html
        )
    
    return html


def remove_csrf(html):
    """Remove CSRF tokens."""
    html = re.sub(r"{{\s*csrf_token\(\)\s*}}", "", html)
    html = re.sub(
        r'<input\s+type=["\']hidden["\']\s+name=["\']csrf_token["\']\s+value=["\'][^"\']*["\']\s*/?>', 
        "", 
        html
    )
    return html


def escape_braces(html):
    """Escapa chaves para f-string."""
    html = re.sub(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', r'<<<PYVAR:\1>>>', html)
    html = html.replace('{', '{{').replace('}', '}}')
    html = re.sub(r'<<<PYVAR:([a-zA-Z_][a-zA-Z0-9_]*)>>>', r'{\1}', html)
    return html


def convert_template(template_path):
    """Converte template completo."""
    
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    func_name = extract_function_name(template_path)
    
    # Extrai body
    body_match = re.search(r'<body[^>]*>(.*)</body>', html, re.DOTALL)
    body_content = body_match.group(1) if body_match else html
    
    # Extrai CSS
    style_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
    css_content = style_match.group(1) if style_match else ""
    
    # Remove style do body
    body_content = re.sub(r'<style>.*?</style>', '', body_content, flags=re.DOTALL)
    
    # Conversões
    body_content = convert_url_for(body_content)
    body_content = remove_csrf(body_content)
    
    # Escapa
    css_content = escape_braces(css_content)
    body_content = escape_braces(body_content)
    
    # Gera código
    code = f'''async def {func_name}(self, db, current_user):
    """Página gerada automaticamente - REVISE antes de usar!"""
    
    # TODO: Buscar dados do banco
    # conteudos = await get_conteudos(db, tipo="...")
    # topics = await get_topics(db)
    
    # TODO: Implementar filtros de busca
    q = ""  # request.args.get('q', '')
    
    return f"""{{{page_head("Título da Página", """
{css_content}
    """)}}}
{body_content}
{{{page_footer(True)}}}"""
'''
    
    return code


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    template_path = sys.argv[1]
    
    if not Path(template_path).exists():
        print("# Erro: Arquivo não encontrado:", template_path, file=sys.stderr)
        sys.exit(1)
    
    # Mensagens de aviso SEM f-string
    print("# Convertendo:", template_path)
    print("# ATENÇÃO: Este código é uma base. REVISE e ajuste:")
    print("#    - Busca de dados do banco")
    print("#    - Filtros e paginação")
    print("#    - Loops Jinja para lógica Python")
    print("#    - Condicionais Jinja para lógica Python")
    print()
    
    code = convert_template(template_path)
    print(code)


if __name__ == "__main__":
    main()
