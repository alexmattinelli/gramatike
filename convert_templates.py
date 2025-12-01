#!/usr/bin/env python3
"""
Conversor automático de templates Flask para Cloudflare Workers
Este script sincroniza os templates HTML para o index.py
"""

import os
import re
from pathlib import Path

def convert_flask_to_python(html_content, template_name):
    """
    Converte template Flask (Jinja2) para string Python f-string
    """
    # Remove comentários HTML excessivos
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    
    # Converte {{ variable }} para {variable}
    html_content = re.sub(r'\{\{\s*(\w+)\s*\}\}', r'{\1}', html_content)
    
    # Converte {% if %} para código Python (simplificado)
    # Por enquanto, mantemos o HTML como está
    
    # Escapa chaves duplas {{ para Python f-string
    html_content = html_content.replace('{', '{{').replace('}', '}}')
    
    # Reverte as variáveis
    html_content = re.sub(r'\{\{(\w+)\}\}', r'{\1}', html_content)
    
    # Remove url_for e substitui por caminhos diretos
    html_content = re.sub(
        r'\{\{ url_for\([\'"]static[\'"]\s*,\s*filename=[\'"](.+?)[\'"]\)\s*\}\}',
        r'/static/\1',
        html_content
    )
    
    # Remove csrf_token
    html_content = re.sub(
        r'\{\{ csrf_token\(\) \}\}|\{\{ csrf_token if csrf_token is defined else [\'"\'"] \}\}',
        '',
        html_content
    )
    
    return html_content.strip()

def read_template(template_path):
    """Lê um template HTML"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Erro ao ler {template_path}: {e}")
        return None

def main():
    """Gera código Python para todos os templates"""
    
    templates_dir = Path("gramatike_app/templates")
    output_file = "templates_converted.py"
    
    print("=" * 60)
    print("🔄 CONVERTENDO TEMPLATES FLASK → PYTHON")
    print("=" * 60)
    
    templates = {}
    
    # Processa templates na raiz
    for template_file in templates_dir.glob("*.html"):
        template_name = template_file.stem
        html_content = read_template(template_file)
        if html_content:
            templates[template_name] = convert_flask_to_python(html_content, template_name)
            print(f"✓ {template_name}")
    
    # Processa templates admin
    admin_dir = templates_dir / "admin"
    if admin_dir.exists():
        for template_file in admin_dir.glob("*.html"):
            template_name = f"admin_{template_file.stem}"
            html_content = read_template(template_file)
            if html_content:
                templates[template_name] = convert_flask_to_python(html_content, template_name)
                print(f"✓ admin/{template_file.stem}")
    
    print(f"\n✅ Total: {len(templates)} templates convertidos")
    print(f"📝 Salvando em {output_file}...")
    
    # Gera arquivo Python
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('# Templates convertidos automaticamente de Flask para Workers\n')
        f.write('# Gerado pelo script convert_templates.py\n\n')
        
        for name, content in templates.items():
            f.write(f'# Template: {name}\n')
            f.write(f'TEMPLATE_{name.upper()} = """\n')
            f.write(content)
            f.write('\n"""\n\n')
    
    print(f"✅ Arquivo gerado: {output_file}")
    print("\n💡 Próximo passo:")
    print("   Copie as templates necessárias para index.py")

if __name__ == '__main__':
    main()
