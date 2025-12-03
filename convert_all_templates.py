#!/usr/bin/env python3
"""
🚀 CONVERSOR: Flask Templates → Cloudflare Workers Templates

Este script converte TODOS os templates Flask para versões que funcionam
no Cloudflare Workers, removendo funções Flask e substituindo por valores estáticos.

Uso:
    python convert_all_templates.py

Saída:
    functions/templates/*.html - Templates convertidos para Workers
"""

import os
import re
from pathlib import Path

# Diretórios
FLASK_TEMPLATES = Path('gramatike_app/templates')
WORKERS_TEMPLATES = Path('functions/templates')

# Mapa de rotas Flask → URLs estáticas
URL_MAP = {
    'main.index': '/',
    'main.login': '/login',
    'main.cadastro': '/cadastro',
    'main.logout': '/logout',
    'main.esqueci_senha': '/esqueci-senha',
    'main.reset_senha': '/reset-senha',
    'main.meu_perfil': '/perfil',
    'main.perfil': '/perfil',
    'main.configuracoes': '/configuracoes',
    'main.educacao': '/educacao',
    'main.exercicios': '/exercicios',
    'main.artigos': '/artigos',
    'main.apostilas': '/apostilas',
    'main.podcasts': '/podcasts',
    'main.dinamicas_home': '/dinamicas',
    'main.dinamicas': '/dinamicas',
    'main.videos': '/videos',
    'main.redacao': '/redacao',
    'main.suporte': '/suporte',
    'main.criar_post': '/novo-post',
    'main.gramatike_edu': '/educacao',
    'admin.dashboard': '/admin',
    'admin.admin_dashboard': '/admin',
}


def convert_template(html):
    """Converte um template Flask para Workers."""
    
    # 1. url_for('static', filename='...') → /static/...
    html = re.sub(
        r"{{\s*url_for\(['\"]static['\"],\s*filename=['\"]([^'\"]+)['\"]\)\s*}}",
        r"/static/\1",
        html
    )
    
    # 2. url_for('main.xxx') e url_for('admin.xxx') → /xxx
    for flask_route, path in URL_MAP.items():
        # Sem parâmetros
        html = re.sub(
            rf"{{{{\s*url_for\(['\"]{ re.escape(flask_route)}['\"]\)\s*}}}}",
            path,
            html
        )
        # Com parâmetros (ignorar parâmetros por enquanto)
        html = re.sub(
            rf"{{{{\s*url_for\(['\"]{ re.escape(flask_route)}['\"],\s*[^)]*\)\s*}}}}",
            path,
            html
        )
    
    # 3. Remover CSRF token
    html = re.sub(
        r'<input\s+type=["\']hidden["\']\s+name=["\']csrf_token["\']\s+value=["\'][^"\']*["\']\s*/?>\s*',
        '',
        html
    )
    html = re.sub(r"{{\s*csrf_token\(\)[^}]*}}", '', html)
    
    # 4. Remover bloco get_flashed_messages - substituir por placeholder para mensagens dinâmicas
    html = re.sub(
        r'{%\s*with\s+messages\s*=\s*get_flashed_messages[^%]*%}.*?{%\s*endwith\s*%}',
        '<!-- FLASH_MESSAGES_PLACEHOLDER -->',
        html,
        flags=re.DOTALL
    )
    
    # 5. Substituir request.form.get(...) por string vazia
    html = re.sub(r"{{\s*request\.form\.get\([^)]*\)\s*}}", '', html)
    html = re.sub(r"{{\s*request\.args\.get\([^)]*\)\s*}}", '', html)
    
    # 6. Substituir current_user por placeholder
    html = re.sub(r"{{\s*current_user\.([a-zA-Z_]+)\s*}}", r'<!-- USER_\1 -->', html)
    html = re.sub(r"{%\s*if\s+current_user\.is_authenticated\s*%}", '{% if user %}', html)
    
    # 7. Converter blocos if/else/endif para comentários ou manter
    # Manteremos os blocos básicos mas removemos os complexos
    
    # 8. Remover {% extends %} e {% block %} - Workers não usa herança
    html = re.sub(r"{%\s*extends\s+['\"][^'\"]+['\"]\s*%}\s*", '', html)
    html = re.sub(r"{%\s*block\s+\w+\s*%}", '', html)
    html = re.sub(r"{%\s*endblock\s*%}", '', html)
    
    # 9. Simplificar loops for - converter para comentários marcadores
    # Exemplo: {% for item in items %} → <!-- FOR_LOOP: items -->
    html = re.sub(
        r"{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}",
        r'<!-- FOR_LOOP: \2 -->',
        html
    )
    html = re.sub(r"{%\s*endfor\s*%}", '<!-- END_FOR_LOOP -->', html)
    
    # 10. Simplificar if básicos
    html = re.sub(r"{%\s*if\s+(\w+)\s*%}", r'<!-- IF: \1 -->', html)
    html = re.sub(r"{%\s*elif\s+[^%]+%}", '<!-- ELIF -->', html)
    html = re.sub(r"{%\s*else\s*%}", '<!-- ELSE -->', html)
    html = re.sub(r"{%\s*endif\s*%}", '<!-- ENDIF -->', html)
    
    # 11. Remover outros blocos Jinja2 complexos
    html = re.sub(r"{%\s*set\s+[^%]+%}", '', html)
    html = re.sub(r"{%\s*include\s+[^%]+%}", '', html)
    html = re.sub(r"{%\s*import\s+[^%]+%}", '', html)
    html = re.sub(r"{%\s*from\s+[^%]+%}", '', html)
    html = re.sub(r"{%\s*macro\s+[^%]+%}.*?{%\s*endmacro\s*%}", '', html, flags=re.DOTALL)
    
    # 12. Converter variáveis simples para placeholders
    # {{ variable }} → <!-- VAR: variable -->
    html = re.sub(r"{{\s*(\w+)\s*}}", r'<!-- VAR: \1 -->', html)
    
    # 13. Remover variáveis complexas restantes
    html = re.sub(r"{{[^}]+}}", '', html)
    
    # 14. Remover blocos Jinja2 restantes
    html = re.sub(r"{%[^%]+%}", '', html)
    
    return html


def process_all_templates():
    """Processa todos os templates Flask e salva versões para Workers."""
    
    # Criar diretório de saída
    WORKERS_TEMPLATES.mkdir(parents=True, exist_ok=True)
    
    # Processar templates na raiz
    templates_processed = 0
    
    for template_file in FLASK_TEMPLATES.glob('*.html'):
        print(f"📄 Convertendo: {template_file.name}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            html = f.read()
        
        converted = convert_template(html)
        
        output_file = WORKERS_TEMPLATES / template_file.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(converted)
        
        templates_processed += 1
    
    # Processar templates em subdiretórios (admin/)
    admin_dir = FLASK_TEMPLATES / 'admin'
    if admin_dir.exists():
        workers_admin = WORKERS_TEMPLATES / 'admin'
        workers_admin.mkdir(exist_ok=True)
        
        for template_file in admin_dir.glob('*.html'):
            print(f"📄 Convertendo: admin/{template_file.name}")
            
            with open(template_file, 'r', encoding='utf-8') as f:
                html = f.read()
            
            converted = convert_template(html)
            
            output_file = workers_admin / template_file.name
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(converted)
            
            templates_processed += 1
    
    print(f"\n✅ {templates_processed} templates convertidos!")
    print(f"📁 Salvos em: {WORKERS_TEMPLATES}/")
    
    return templates_processed


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 CONVERSOR: Flask Templates → Cloudflare Workers")
    print("=" * 60)
    print()
    
    count = process_all_templates()
    
    print()
    print("=" * 60)
    print("✅ CONVERSÃO COMPLETA!")
    print("=" * 60)
    print()
    print("Próximos passos:")
    print("1. Revise os templates em functions/templates/")
    print("2. Atualize os handlers em functions/*.py para usar esses templates")
    print("3. Teste o deploy com 'npm run deploy'")
