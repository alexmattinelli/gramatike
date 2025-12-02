#!/usr/bin/env python3
"""
🔄 Conversor Completo de Templates: Flask → Workers
Analisa TODOS os templates e gera código Workers mantendo a essência de cada página
"""

import re
from pathlib import Path
import json

# Mapeamento de templates → funções no index.py
TEMPLATES_MAP = {
    'configuracoes.html': '_configuracoes_page',
    'suporte.html': '_suporte_page',
    'meu_perfil.html': '_meu_perfil_page',
    'perfil.html': '_profile_page',
    'exercicios.html': '_exercicios_page',
    'dinamicas.html': '_dinamicas_page',
    'dinamica_view.html': '_dinamica_view_page',
    'dinamica_edit.html': '_dinamica_edit_page',
    'redacao.html': '_redacao_page',
    'videos.html': '_videos_page',
    'artigos.html': '_artigos_page',
    'apostilas.html': '_apostilas_page',
    'podcasts.html': '_podcasts_page',
    'gramatike_edu.html': '_educacao_page',
    'index.html': '_index_page',
    'login.html': '_login_page',
    'cadastro.html': '_cadastro_page',
    'register.html': '_cadastro_page',
    'esqueci_senha.html': '_esqueci_senha_page',
    'post_detail.html': '_post_detail_page',
    'admin/dashboard.html': '_admin_page',
}

def analyze_template(template_path):
    """Analisa template e extrai informações importantes"""
    html = template_path.read_text(encoding='utf-8')
    
    info = {
        'path': str(template_path),
        'name': template_path.name,
        'size': len(html),
        'lines': html.count('\n') + 1,
        'has_forms': bool(re.search(r'<form', html, re.I)),
        'form_count': len(re.findall(r'<form', html, re.I)),
        'has_tabs': bool(re.search(r'class=["\'].*tab', html, re.I)),
        'has_javascript': bool(re.search(r'<script', html, re.I)),
        'has_css': bool(re.search(r'<style', html, re.I)),
        'csrf_tokens': len(re.findall(r'csrf_token', html, re.I)),
        'url_for_calls': len(re.findall(r'url_for\(', html)),
        'jinja_loops': len(re.findall(r'\{%\s*for\s+', html)),
        'jinja_ifs': len(re.findall(r'\{%\s*if\s+', html)),
        'jinja_vars': len(re.findall(r'\{\{\s*\w+', html)),
    }
    
    # Detecta features especiais
    features = []
    if 'avatar' in html.lower() or 'upload' in html.lower():
        features.append('upload')
    if 'dark' in html.lower() and 'mode' in html.lower():
        features.append('dark_mode')
    if 'password' in html.lower():
        features.append('password_fields')
    if 'quill' in html.lower() or 'editor' in html.lower():
        features.append('rich_text_editor')
    if 'chart' in html.lower():
        features.append('charts')
    if 'spotify' in html.lower():
        features.append('spotify_embed')
    
    info['features'] = features
    
    # Extrai título da página
    title_match = re.search(r'<title>(.*?)</title>', html, re.I)
    info['title'] = title_match.group(1) if title_match else template_path.stem.title()
    
    return info

def get_workers_function_size(function_name):
    """Obtém tamanho da função correspondente em index.py"""
    index_path = Path('index.py')
    if not index_path.exists():
        return None
    
    content = index_path.read_text(encoding='utf-8')
    
    # Procura a função
    pattern = rf'async def {function_name}\([^)]*\):(.*?)(?=\n    async def |\nclass |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        func_body = match.group(1)
        return {
            'size': len(func_body),
            'lines': func_body.count('\n'),
            'has_forms': '<form' in func_body,
            'complexity': 'simple' if len(func_body) < 1000 else 'medium' if len(func_body) < 3000 else 'complex'
        }
    
    return None

def compare_templates():
    """Compara todos templates Flask com código Workers"""
    templates_dir = Path('gramatike_app/templates')
    
    print("🔍 Analisando templates Flask vs Workers...\n")
    
    results = []
    missing_functions = []
    outdated_pages = []
    
    for template_file in templates_dir.rglob('*.html'):
        # Pula templates de base/partials
        if 'base' in template_file.name.lower() or 'partial' in template_file.name.lower():
            continue
        
        # Análise do template
        template_info = analyze_template(template_file)
        
        # Nome relativo do template
        rel_path = template_file.relative_to(templates_dir)
        template_key = str(rel_path)
        
        # Busca função correspondente
        function_name = TEMPLATES_MAP.get(template_key)
        
        if function_name:
            workers_info = get_workers_function_size(function_name)
            
            if workers_info:
                # Compara complexidade
                template_complexity = template_info['size']
                workers_complexity = workers_info['size']
                
                ratio = workers_complexity / template_complexity if template_complexity > 0 else 0
                
                status = '✅ OK'
                if ratio < 0.3:
                    status = '⚠️ SIMPLIFICADO'
                    outdated_pages.append({
                        'template': template_key,
                        'function': function_name,
                        'ratio': ratio,
                        'info': template_info
                    })
                elif template_info['has_forms'] and not workers_info['has_forms']:
                    status = '⚠️ SEM FORMULÁRIOS'
                    outdated_pages.append({
                        'template': template_key,
                        'function': function_name,
                        'ratio': ratio,
                        'info': template_info
                    })
                
                results.append({
                    'template': template_key,
                    'function': function_name,
                    'status': status,
                    'template_size': template_info['size'],
                    'workers_size': workers_info['size'],
                    'ratio': ratio,
                    'features': template_info['features']
                })
            else:
                missing_functions.append({
                    'template': template_key,
                    'function': function_name,
                    'info': template_info
                })
        else:
            # Template sem função mapeada
            missing_functions.append({
                'template': template_key,
                'function': None,
                'info': template_info
            })
    
    return results, missing_functions, outdated_pages

def print_report(results, missing_functions, outdated_pages):
    """Imprime relatório de análise"""
    
    print("=" * 80)
    print("📊 RELATÓRIO DE COMPARAÇÃO: Templates Flask vs Workers")
    print("=" * 80)
    print()
    
    # Templates analisados
    print(f"📄 Total de templates analisados: {len(results) + len(missing_functions)}")
    print(f"✅ Templates com função Workers: {len(results)}")
    print(f"❌ Templates sem função Workers: {len(missing_functions)}")
    print(f"⚠️  Templates desatualizados/simplificados: {len(outdated_pages)}")
    print()
    
    # Páginas desatualizadas (PRINCIPAL PROBLEMA)
    if outdated_pages:
        print("=" * 80)
        print("⚠️  PÁGINAS DESATUALIZADAS (precisam ser portadas)")
        print("=" * 80)
        for page in sorted(outdated_pages, key=lambda x: x['ratio']):
            template = page['template']
            function = page['function']
            ratio = page['ratio']
            info = page['info']
            
            print(f"\n📄 {template}")
            print(f"   Função: {function}")
            print(f"   Complexidade: {ratio:.1%} do original")
            print(f"   Formulários: {info['form_count']}")
            print(f"   Features: {', '.join(info['features']) if info['features'] else 'nenhuma'}")
            print(f"   Tamanho: {info['lines']} linhas")
    
    # Funções faltando
    if missing_functions:
        print("\n" + "=" * 80)
        print("❌ TEMPLATES SEM FUNÇÃO WORKERS")
        print("=" * 80)
        for item in missing_functions:
            template = item['template']
            function = item['function'] or '(não mapeada)'
            info = item['info']
            print(f"\n📄 {template}")
            print(f"   Função: {function}")
            print(f"   Tamanho: {info['lines']} linhas")
            print(f"   Features: {', '.join(info['features']) if info['features'] else 'nenhuma'}")
    
    # Resumo por status
    print("\n" + "=" * 80)
    print("📈 RESUMO POR STATUS")
    print("=" * 80)
    
    status_count = {}
    for r in results:
        status = r['status']
        status_count[status] = status_count.get(status, 0) + 1
    
    for status, count in sorted(status_count.items()):
        print(f"   {status}: {count} páginas")
    
    print()

def generate_port_script(outdated_pages):
    """Gera script para portar páginas desatualizadas"""
    
    print("=" * 80)
    print("🔧 GERANDO SCRIPT DE PORTAGEM")
    print("=" * 80)
    print()
    
    script = "# PÁGINAS PRIORITÁRIAS PARA PORTAR\n\n"
    
    for i, page in enumerate(outdated_pages, 1):
        template = page['template']
        function = page['function']
        info = page['info']
        
        script += f"## {i}. {template}\n"
        script += f"Função: {function}\n"
        script += f"Features: {', '.join(info['features']) if info['features'] else 'básico'}\n"
        script += f"Formulários: {info['form_count']}\n"
        script += f"Complexidade: {info['lines']} linhas\n"
        script += f"\nComandos:\n"
        script += f"```bash\n"
        script += f"# Veja o template original:\n"
        script += f"code gramatike_app/templates/{template}\n\n"
        script += f"# Procure a função em index.py:\n"
        script += f"grep -n 'def {function}' index.py\n"
        script += f"```\n\n"
    
    output_path = Path('TEMPLATES_OUTDATED_REPORT.md')
    output_path.write_text(script, encoding='utf-8')
    
    print(f"✅ Relatório salvo em: {output_path}")
    print()

def main():
    print("🚀 Conversor Completo de Templates\n")
    
    # Verifica se os diretórios existem
    if not Path('gramatike_app/templates').exists():
        print("❌ Diretório gramatike_app/templates não encontrado")
        return
    
    if not Path('index.py').exists():
        print("❌ Arquivo index.py não encontrado")
        return
    
    # Compara templates
    results, missing_functions, outdated_pages = compare_templates()
    
    # Imprime relatório
    print_report(results, missing_functions, outdated_pages)
    
    # Gera script de portagem
    if outdated_pages:
        generate_port_script(outdated_pages)
    
    print("=" * 80)
    print("🎯 PRÓXIMOS PASSOS")
    print("=" * 80)
    print()
    print("1. Revise TEMPLATES_OUTDATED_REPORT.md")
    print("2. Priorize páginas mais usadas (Configurações, Suporte, etc.)")
    print("3. Use convert_template_to_workers.py para cada página")
    print("4. Teste localmente antes de deploy")
    print()
    
    # Salva JSON com dados completos
    json_data = {
        'results': results,
        'missing_functions': missing_functions,
        'outdated_pages': outdated_pages,
        'summary': {
            'total_templates': len(results) + len(missing_functions),
            'with_workers_function': len(results),
            'without_workers_function': len(missing_functions),
            'outdated': len(outdated_pages)
        }
    }
    
    json_path = Path('templates_analysis.json')
    json_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"📊 Dados completos salvos em: {json_path}")

if __name__ == '__main__':
    main()
