#!/usr/bin/env python3
"""
Sincroniza o CSS do index.html para o BASE_CSS no index.py.

Este script extrai todo o CSS do arquivo gramatike_app/templates/index.html
e atualiza a constante BASE_CSS no arquivo index.py.

Uso:
    python scripts/sync_css.py

Após executar, faça deploy com:
    npm run deploy
"""

import re
import os

def extract_css_from_html(html_path: str) -> str:
    """Extrai todo o CSS de um arquivo HTML."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extrair todas as tags <style>
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html_content, re.DOTALL)
    
    # Combinar todo o CSS
    all_css = '\n'.join(style_blocks)
    
    # Limpar espaços em branco excessivos
    lines = []
    for line in all_css.split('\n'):
        stripped = line.strip()
        if stripped:
            lines.append(stripped)
    
    return '\n'.join(lines)


def update_base_css(index_py_path: str, new_css: str) -> bool:
    """Atualiza o BASE_CSS no index.py."""
    with open(index_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar o bloco BASE_CSS = """..."""
    pattern = r'(BASE_CSS\s*=\s*""")(.*?)(""")'
    
    # Escapar caracteres especiais no CSS
    escaped_css = new_css.replace('\\', '\\\\')
    
    # Substituir o conteúdo
    new_content, count = re.subn(
        pattern,
        lambda m: m.group(1) + '\n' + escaped_css + '\n' + m.group(3),
        content,
        flags=re.DOTALL
    )
    
    if count == 0:
        print("ERRO: Não foi possível encontrar BASE_CSS no index.py")
        return False
    
    with open(index_py_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True


def main():
    # Caminhos dos arquivos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    html_path = os.path.join(project_root, 'gramatike_app', 'templates', 'index.html')
    index_py_path = os.path.join(project_root, 'index.py')
    
    print(f"Extraindo CSS de: {html_path}")
    
    if not os.path.exists(html_path):
        print(f"ERRO: Arquivo não encontrado: {html_path}")
        return 1
    
    if not os.path.exists(index_py_path):
        print(f"ERRO: Arquivo não encontrado: {index_py_path}")
        return 1
    
    # Extrair CSS
    css = extract_css_from_html(html_path)
    print(f"CSS extraído: {len(css)} caracteres")
    
    # Atualizar index.py
    print(f"Atualizando: {index_py_path}")
    if update_base_css(index_py_path, css):
        print("✓ BASE_CSS atualizado com sucesso!")
        print("\nPróximos passos:")
        print("1. Revisar as mudanças: git diff index.py")
        print("2. Commitar: git add index.py && git commit -m 'Sync CSS from index.html'")
        print("3. Deploy: npm run deploy")
        return 0
    else:
        return 1


if __name__ == '__main__':
    exit(main())
