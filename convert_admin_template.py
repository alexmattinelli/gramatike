#!/usr/bin/env python3
"""
🤖 Template Converter: Flask → Cloudflare Workers
Converte template admin/dashboard.html para código Workers automaticamente
"""

import re
from pathlib import Path

def extract_sections(template_html):
    """Extrai seções principais do template (Geral, Analytics, Edu, etc.)"""
    sections = {}
    
    # Padrão: <section class="tab-panel" id="tab-NOME">...</section>
    pattern = r'<section[^>]*id="tab-(\w+)"[^>]*>(.*?)</section>'
    matches = re.findall(pattern, template_html, re.DOTALL)
    
    for section_name, section_html in matches:
        sections[section_name] = section_html.strip()
    
    return sections

def convert_jinja_to_workers(html):
    """Converte sintaxe Jinja2 para f-strings Python + JavaScript"""
    
    # 1. Remove CSRF tokens (não precisa no Workers)
    html = re.sub(r'\{\%\s*if csrf_token is defined.*?\{\%\s*endif\s*\%\}', '', html, flags=re.DOTALL)
    html = re.sub(r'<input[^>]*name="csrf_token"[^>]*>', '', html)
    
    # 2. Converte url_for para paths absolutos
    html = re.sub(r'\{\{\s*url_for\([\'"]static[\'"],\s*filename=[\'"]([^\'"]+)[\'"]\)\s*\}\}', r'/static/\1', html)
    html = re.sub(r'\{\{\s*url_for\([\'"]([^.]+)\.([^\'"]+)[\'"](?:,\s*(\w+)=([^)]+))?\)\s*\}\}', 
                  lambda m: f"/{m.group(1)}/{m.group(2)}" + (f"/{{{m.group(4)}}}" if m.group(3) else ""), html)
    
    # 3. Converte variáveis Jinja {{ var }} para placeholders Python {var}
    html = re.sub(r'\{\{\s*(\w+(?:\.\w+)*)\s*\}\}', r'{\1}', html)
    
    # 4. Marca loops FOR para conversão manual
    html = re.sub(r'\{\%\s*for\s+(\w+)\s+in\s+(\w+)\s*\%\}', r'<!-- FOR \1 IN \2 START -->', html)
    html = re.sub(r'\{\%\s*endfor\s*\%\}', r'<!-- FOR END -->', html)
    
    # 5. Marca condicionais IF para conversão manual
    html = re.sub(r'\{\%\s*if\s+(.*?)\s*\%\}', r'<!-- IF \1 START -->', html)
    html = re.sub(r'\{\%\s*elif\s+(.*?)\s*\%\}', r'<!-- ELIF \1 -->', html)
    html = re.sub(r'\{\%\s*else\s*\%\}', r'<!-- ELSE -->', html)
    html = re.sub(r'\{\%\s*endif\s*\%\}', r'<!-- IF END -->', html)
    
    # 6. Converte filtros Jinja simples
    html = re.sub(r'\{\{\s*(\w+)\s*\|\s*safe\s*\}\}', r'{\1}', html)
    html = re.sub(r'\{\{\s*(\w+)\s*\|\s*escape\s*\}\}', r'{{escape_html(\1)}}', html)
    
    return html

def extract_javascript(html):
    """Extrai blocos JavaScript inline"""
    scripts = []
    pattern = r'<script[^>]*>(.*?)</script>'
    matches = re.findall(pattern, html, re.DOTALL)
    
    for script in matches:
        if script.strip():
            scripts.append(script.strip())
    
    # Remove scripts do HTML
    html_without_scripts = re.sub(pattern, '', html, flags=re.DOTALL)
    
    return html_without_scripts, scripts

def extract_styles(html):
    """Extrai blocos CSS inline"""
    styles = []
    pattern = r'<style[^>]*>(.*?)</style>'
    matches = re.findall(pattern, html, re.DOTALL)
    
    for style in matches:
        if style.strip():
            styles.append(style.strip())
    
    # Remove styles do HTML
    html_without_styles = re.sub(pattern, '', html, flags=re.DOTALL)
    
    return html_without_styles, styles

def generate_workers_code(sections, scripts, styles):
    """Gera código Python Workers completo"""
    
    # Combina estilos
    combined_css = "\n".join(styles)
    
    # Combina JavaScript
    combined_js = "\n\n".join(scripts)
    
    # Gera constantes Python
    code = '# Constantes do Admin Dashboard - AUTO-GERADAS\n\n'
    code += f'ADMIN_CSS = """\n{combined_css}\n"""\n\n'
    
    for section_name, section_html in sections.items():
        const_name = f"{section_name.upper()}_TAB_HTML"
        code += f'{const_name} = f"""\n{section_html}\n"""\n\n'
    
    code += f'ADMIN_JAVASCRIPT = """\n{combined_js}\n"""\n\n'
    
    # Gera função _admin_page
    code += '''async def _admin_page(self, db, current_user):
    """Admin Dashboard - VERSÃO AUTO-GERADA"""
    
    # Check admin
    if not current_user:
        return redirect('/login')
    
    is_admin = current_user.get('is_admin', False) or current_user.get('is_superadmin', False)
    if not is_admin:
        return html_response("<h1>Acesso Negado</h1>")
    
    # Get data
    stats = await get_admin_stats(db) if db else {}
    all_users = await get_all_usuaries(db) if db else []
    edu_topics = []  # TODO: implementar get_edu_topics
    divulgacoes = []  # TODO: implementar get_divulgacoes
    
    # Build HTML
    return f"""{page_head("Painel de Controle — Gramátike", ADMIN_CSS)}
<header class="site-head">
    <div class="admin-badge">ADMIN</div>
    <h1 class="logo">Gramátike</h1>
    <nav class="tabs">
'''
    
    # Adiciona tabs para cada seção
    for i, section_name in enumerate(sections.keys()):
        active = ' active' if i == 0 else ''
        emoji = {'geral': '📊', 'analytics': '📈', 'edu': '📚', 'gramatike': '✏️', 'publi': '📢'}.get(section_name, '📄')
        code += f'        <a href="javascript:void(0)" data-tab="{section_name}" class="tab-link{active}" role="tab">{emoji} {section_name.title()}</a>\n'
    
    code += '''    </nav>
</header>

<main>
'''
    
    # Adiciona seções
    for i, (section_name, _) in enumerate(sections.items()):
        active = ' active' if i == 0 else ''
        const_name = f"{section_name.upper()}_TAB_HTML"
        code += f'    <section class="tab-panel{active}" id="tab-{section_name}" role="tabpanel">\n'
        code += f'        {{{const_name}}}\n'
        code += f'    </section>\n\n'
    
    code += '''</main>

<script>
{ADMIN_JAVASCRIPT}
</script>

{page_footer(False)}
"""
'''
    
    return code

def main():
    # Lê o template Flask
    template_path = Path('gramatike_app/templates/admin/dashboard.html')
    
    if not template_path.exists():
        print(f"❌ Arquivo não encontrado: {template_path}")
        return
    
    print(f"📖 Lendo template: {template_path}")
    html = template_path.read_text(encoding='utf-8')
    
    print("🔍 Extraindo seções...")
    sections = extract_sections(html)
    print(f"   Encontradas {len(sections)} seções: {', '.join(sections.keys())}")
    
    print("🎨 Extraindo estilos CSS...")
    html, styles = extract_styles(html)
    print(f"   Encontrados {len(styles)} blocos CSS")
    
    print("⚙️  Extraindo JavaScript...")
    html, scripts = extract_javascript(html)
    print(f"   Encontrados {len(scripts)} blocos JavaScript")
    
    print("🔄 Convertendo sintaxe Jinja2 → Python...")
    for section_name in sections:
        sections[section_name] = convert_jinja_to_workers(sections[section_name])
    
    print("🏗️  Gerando código Workers...")
    workers_code = generate_workers_code(sections, scripts, styles)
    
    # Salva resultado
    output_path = Path('admin_dashboard_generated.py')
    output_path.write_text(workers_code, encoding='utf-8')
    
    print(f"\n✅ Conversão completa!")
    print(f"📁 Arquivo gerado: {output_path}")
    print(f"📏 Tamanho: {len(workers_code):,} bytes ({len(workers_code) // 1024} KB)")
    print("\n⚠️  PRÓXIMOS PASSOS:")
    print("1. Revise o arquivo gerado (especialmente loops FOR e condicionais IF)")
    print("2. Substitua os comentários <!-- FOR ... --> por código Python apropriado")
    print("3. Teste localmente antes de fazer deploy")
    print("4. Copie o código para index.py substituindo a função _admin_page()")

if __name__ == '__main__':
    main()
