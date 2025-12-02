#!/usr/bin/env python3
"""
Conversor Flask Template → Workers Code
"""

import sys
import re
from pathlib import Path


def convert_template(template_path):
    """Converte template completo."""
    
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    func_name = f"_{Path(template_path).stem}_page"
    
    # Extrai body
    body_match = re.search(r'<body[^>]*>(.*)</body>', html, re.DOTALL)
    body_content = body_match.group(1) if body_match else html
    
    # Extrai CSS
    style_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
    css_content = style_match.group(1) if style_match else ""
    
    # Remove style do body
    body_content = re.sub(r'<style>.*?</style>', '', body_content, flags=re.DOTALL)
    
    # Conversões básicas
    body_content = re.sub(r"{{\s*url_for\('static',\s*filename=['\"]([^'\"]+)['\"]\)\s*}}", r"/static/\1", body_content)
    body_content = re.sub(r"{{\s*csrf_token\(\)\s*}}", "", body_content)
    body_content = re.sub(r'<input\s+type=["\']hidden["\']\s+name=["\']csrf_token["\'][^>]*>', "", body_content)
    
    # Escapa chaves mantendo variáveis Python
    body_content = re.sub(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', r'<<<VAR:\1>>>', body_content)
    body_content = body_content.replace('{', '{{').replace('}', '}}')
    body_content = re.sub(r'<<<VAR:([a-zA-Z_][a-zA-Z0-9_]*)>>>', r'{\1}', body_content)
    
    css_content = re.sub(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', r'<<<VAR:\1>>>', css_content)
    css_content = css_content.replace('{', '{{').replace('}', '}}')
    css_content = re.sub(r'<<<VAR:([a-zA-Z_][a-zA-Z0-9_]*)>>>', r'{\1}', css_content)
    
    # Monta código usando concatenação de strings (não f-string)
    code_lines = [
        'async def ' + func_name + '(self, db, current_user):',
        '    """Página gerada automaticamente - REVISE antes de usar!"""',
        '    ',
        '    # TODO: Buscar dados do banco',
        '    # conteudos = await get_conteudos(db, tipo="...")',
        '    # topics = await get_topics(db)',
        '    ',
        '    # TODO: Implementar filtros de busca',
        '    q = ""  # request.args.get(\'q\', \'\')',
        '    ',
        '    return f"""{page_head("Título da Página", """',
        css_content,
        '    """)}',
        body_content,
        '{page_footer(True)}"""',
    ]
    
    return '\n'.join(code_lines)


def main():
    if len(sys.argv) < 2:
        print("Uso: python converter_template.py <template.html>")
        sys.exit(1)
    
    template_path = sys.argv[1]
    
    if not Path(template_path).exists():
        print("# Erro: Arquivo não encontrado:", template_path, file=sys.stderr)
        sys.exit(1)
    
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
