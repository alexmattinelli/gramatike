#!/usr/bin/env python3
"""
🎯 Finalizador Admin Dashboard: Converte código gerado para produção
Este script finaliza automaticamente as conversões FOR/IF do template
"""

import re
from pathlib import Path

def convert_simple_for_loops(code):
    """Converte loops FOR simples para Python"""
    
    # Padrão: <!-- FOR item IN items START -->...<!-- FOR END -->
    pattern = r'<!-- FOR (\w+) IN (\w+) START -->(.*?)<!-- FOR END -->'
    
    def replace_for(match):
        item_var = match.group(1)
        items_var = match.group(2)
        loop_content = match.group(3)
        
        # Remove indentação extra do conteúdo
        lines = loop_content.strip().split('\n')
        min_indent = min(len(line) - len(line.lstrip()) for line in lines if line.strip())
        dedented = '\n'.join(line[min_indent:] if len(line) > min_indent else line for line in lines)
        
        # Cria variável para acumular HTML
        result_var = f"{items_var}_html"
        
        python_code = f'''
{{# PYTHON LOOP START #}}
{result_var} = ""
for {item_var} in {items_var}:
    {result_var} += f"""
{dedented}
    """
{{{result_var}}}
{{# PYTHON LOOP END #}}
'''
        return python_code.strip()
    
    return re.sub(pattern, replace_for, code, flags=re.DOTALL)

def convert_simple_if_blocks(code):
    """Converte blocos IF simples para Python"""
    
    # Padrão: <!-- IF condition START -->...<!-- IF END -->
    pattern = r'<!-- IF (.+?) START -->(.*?)<!-- IF END -->'
    
    def replace_if(match):
        condition = match.group(1)
        if_content = match.group(2)
        
        # Verifica se tem ELSE
        parts = if_content.split('<!-- ELSE -->')
        
        if len(parts) == 2:
            true_content = parts[0].strip()
            false_content = parts[1].strip()
            
            # Extrai nome da variável da condição (simplificado)
            var_match = re.search(r'(\w+)', condition)
            var_name = var_match.group(1) if var_match else 'data'
            result_var = f"{var_name}_html"
            
            python_code = f'''
{{# PYTHON IF START #}}
if {condition}:
    {result_var} = f"""
{true_content}
    """
else:
    {result_var} = f"""
{false_content}
    """
{{{result_var}}}
{{# PYTHON IF END #}}
'''
        else:
            # Só IF, sem ELSE
            true_content = parts[0].strip()
            var_match = re.search(r'(\w+)', condition)
            var_name = var_match.group(1) if var_match else 'data'
            result_var = f"{var_name}_html"
            
            python_code = f'''
{{# PYTHON IF START #}}
{result_var} = ""
if {condition}:
    {result_var} = f"""
{true_content}
    """
{{{result_var}}}
{{# PYTHON IF END #}}
'''
        
        return python_code.strip()
    
    return re.sub(pattern, replace_if, code, flags=re.DOTALL)

def add_helper_functions():
    """Gera funções helper necessárias"""
    return '''
# ========== Admin Dashboard Helpers ==========

def escape_html(text):
    """Escapa HTML para prevenir XSS"""
    if not text:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;"))

def build_users_table_rows(all_users, limit=100):
    """Constrói linhas da tabela de usuáries"""
    rows = ""
    for user in (all_users[:limit] if len(all_users) > limit else all_users):
        user_id = user.get('id', 0)
        username = escape_html(user.get('username', ''))
        email = escape_html(user.get('email', ''))
        is_admin = user.get('is_admin', False)
        is_superadmin = user.get('is_superadmin', False)
        is_banned = user.get('is_banned', False)
        
        badge = ""
        if is_superadmin:
            badge = '<span class="badge badge-superadmin">SUPERADMIN</span>'
        elif is_admin:
            badge = '<span class="badge badge-admin">ADMIN</span>'
        elif is_banned:
            badge = '<span class="badge" style="background:#f44;color:#fff;">BANIDO</span>'
        
        rows += f"""
        <tr>
            <td data-label="ID">{user_id}</td>
            <td data-label="Username">{username}</td>
            <td data-label="Email">{email}</td>
            <td data-label="Status">{badge}</td>
            <td data-label="Ações" class="actions-stack">
                <form method="POST" action="/admin/users/{user_id}/promote" class="inline">
                    <button type="submit" class="action-btn">Promover</button>
                </form>
                <form method="POST" action="/admin/users/{user_id}/ban" class="inline">
                    <button type="submit" class="action-btn danger">Banir</button>
                </form>
                <form method="POST" action="/admin/users/{user_id}/delete" class="inline" onsubmit="return confirm('Excluir?')">
                    <button type="submit" class="action-btn danger">Deletar</button>
                </form>
            </td>
        </tr>
        """
    
    return rows

def build_edu_topics_list(topics, area_filter=None):
    """Constrói lista de tópicos educacionais"""
    filtered = [t for t in topics if not area_filter or t.get('area') == area_filter]
    
    if not filtered:
        return '<p class="muted-inline">Nenhum tópico criado ainda.</p>'
    
    html = '<div style="display:grid; gap:.8rem; grid-template-columns:1fr;">'
    for topic in filtered:
        topic_id = topic.get('id', 0)
        nome = escape_html(topic.get('nome', ''))
        descricao = escape_html(topic.get('descricao', ''))
        
        html += f"""
        <div style="background:#f9fbfd; border:1px solid #e3e9f0; border-radius:12px; padding:.9rem;">
            <div style="display:flex; justify-content:space-between; align-items:start; gap:.8rem;">
                <div style="flex:1;">
                    <div style="font-weight:700; font-size:.85rem; color:#333;">{nome}</div>
                    {"<div style='font-size:.7rem; color:#666;'>" + descricao + "</div>" if descricao else ""}
                </div>
                <button onclick="toggleTopicEdit('{area_filter}-{topic_id}')" class="action-btn" style="font-size:.6rem;">
                    Editar
                </button>
            </div>
            <div id="topic-edit-{area_filter}-{topic_id}" style="display:none; margin-top:.8rem; padding-top:.8rem; border-top:1px solid #e3e9f0;">
                <form method="POST" action="/admin/edu/topics/{topic_id}/update">
                    <input name="nome" value="{nome}" required style="width:100%; padding:.5rem; margin-bottom:.5rem; border:1px solid #cfd7e2; border-radius:8px;">
                    <textarea name="descricao" style="width:100%; padding:.5rem; margin-bottom:.5rem; border:1px solid #cfd7e2; border-radius:8px; min-height:60px;">{descricao}</textarea>
                    <button type="submit" class="action-btn">Salvar</button>
                    <button type="button" onclick="toggleTopicEdit('{area_filter}-{topic_id}')" class="action-btn">Cancelar</button>
                </form>
            </div>
        </div>
        """
    
    html += '</div>'
    return html

def build_divulgacoes_list(divulgacoes):
    """Constrói lista de divulgações"""
    if not divulgacoes:
        return '<p class="small-muted">Nenhuma divulgação cadastrada.</p>'
    
    html = '<div style="display:grid; gap:1rem; grid-template-columns:1fr;">'
    for div in divulgacoes:
        div_id = div.get('id', 0)
        titulo = escape_html(div.get('titulo', ''))
        texto = escape_html(div.get('texto', ''))
        link = escape_html(div.get('link', ''))
        ativa = div.get('ativa', False)
        
        status_class = ' promo-active' if ativa else ''
        
        html += f"""
        <div class="card{status_class}">
            <h4>{titulo}</h4>
            <p class="small-muted">{texto}</p>
            <div style="margin-top:.8rem; display:flex; gap:.4rem;">
                <form method="POST" action="/admin/divulgacoes/{div_id}/toggle" class="inline">
                    <button type="submit" class="action-btn">{"Desativar" if ativa else "Ativar"}</button>
                </form>
                <button class="action-btn" onclick="editDivulgacao({div_id})">Editar</button>
                <form method="POST" action="/admin/divulgacoes/{div_id}/delete" class="inline" onsubmit="return confirm('Excluir?')">
                    <button type="submit" class="action-btn danger">Excluir</button>
                </form>
            </div>
        </div>
        """
    
    html += '</div>'
    return html

# ========== Fim dos Helpers ==========

'''

def clean_python_markers(code):
    """Remove marcadores de conversão Python"""
    code = re.sub(r'\{# PYTHON LOOP START #\}', '', code)
    code = re.sub(r'\{# PYTHON LOOP END #\}', '', code)
    code = re.sub(r'\{# PYTHON IF START #\}', '', code)
    code = re.sub(r'\{# PYTHON IF END #\}', '', code)
    return code

def analyze_remaining_conversions(code):
    """Analisa conversões que ainda precisam ser feitas manualmente"""
    remaining = []
    
    # Procura FORs aninhados ou complexos
    complex_fors = re.findall(r'<!-- FOR .+? -->', code)
    if complex_fors:
        remaining.append(f"⚠️  {len(complex_fors)} loops FOR complexos precisam conversão manual")
    
    # Procura IFs com ELIF
    elifs = re.findall(r'<!-- ELIF .+? -->', code)
    if elifs:
        remaining.append(f"⚠️  {len(elifs)} condicionais com ELIF precisam conversão manual")
    
    # Procura filtros Jinja complexos
    filters = re.findall(r'\{\{.+?\|.+?\}\}', code)
    if filters:
        remaining.append(f"⚠️  {len(filters)} filtros Jinja complexos precisam conversão manual")
    
    return remaining

def main():
    print("🎯 Finalizador Admin Dashboard\n")
    
    # Lê arquivo gerado
    input_path = Path('admin_dashboard_generated.py')
    if not input_path.exists():
        print(f"❌ Arquivo não encontrado: {input_path}")
        print("   Execute primeiro: python convert_admin_template.py")
        return
    
    print(f"📖 Lendo: {input_path}")
    code = input_path.read_text(encoding='utf-8')
    
    print("🔄 Convertendo loops FOR simples...")
    code = convert_simple_for_loops(code)
    
    print("🔄 Convertendo blocos IF simples...")
    code = convert_simple_if_blocks(code)
    
    print("🔧 Limpando marcadores...")
    code = clean_python_markers(code)
    
    print("🛠️  Adicionando helpers...")
    helpers = add_helper_functions()
    final_code = helpers + "\n\n" + code
    
    print("🔍 Analisando conversões restantes...")
    remaining = analyze_remaining_conversions(code)
    
    # Salva resultado
    output_path = Path('admin_dashboard_final.py')
    output_path.write_text(final_code, encoding='utf-8')
    
    print(f"\n✅ Finalização completa!")
    print(f"📁 Arquivo gerado: {output_path}")
    print(f"📏 Tamanho: {len(final_code):,} bytes ({len(final_code) // 1024} KB)")
    
    if remaining:
        print("\n⚠️  ATENÇÃO - Conversões Manuais Necessárias:")
        for item in remaining:
            print(f"   {item}")
        print("\n   Use um editor para procurar e converter estes itens.")
    else:
        print("\n✨ Todas as conversões automáticas concluídas!")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Revise admin_dashboard_final.py")
    print("2. Copie os helpers para o topo de index.py (após imports)")
    print("3. Copie as constantes ADMIN_CSS, *_TAB_HTML, ADMIN_JAVASCRIPT")
    print("4. Substitua a função _admin_page() pela versão nova")
    print("5. Teste localmente: python -m flask run")
    print("6. Deploy: npm run deploy")

if __name__ == '__main__':
    main()
