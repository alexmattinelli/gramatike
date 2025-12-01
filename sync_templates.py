#!/usr/bin/env python3
"""
Script para sincronizar templates Flask para Cloudflare Workers
Compara os templates em gramatike_app/templates/ com as páginas no index.py
"""

import os
import re

# Templates Flask existentes
TEMPLATES_DIR = "gramatike_app/templates"
templates = []

for file in os.listdir(TEMPLATES_DIR):
    if file.endswith('.html'):
        templates.append(file.replace('.html', ''))

# Admin templates
admin_dir = os.path.join(TEMPLATES_DIR, 'admin')
if os.path.exists(admin_dir):
    for file in os.listdir(admin_dir):
        if file.endswith('.html'):
            templates.append(f'admin/{file.replace(".html", "")}')

print("=" * 60)
print("📋 TEMPLATES FLASK vs CLOUDFLARE WORKERS")
print("=" * 60)

# Ler index.py para ver quais páginas existem
with open('index.py', 'r') as f:
    index_content = f.read()

# Encontrar todas as funções _*_page
pages_in_workers = re.findall(r'async def _(\w+)_page\(', index_content)

print(f"\n✅ Páginas implementadas no Workers ({len(pages_in_workers)}):")
for page in sorted(pages_in_workers):
    print(f"  - {page}")

print(f"\n📄 Templates Flask encontrados ({len(templates)}):")
for template in sorted(templates):
    print(f"  - {template}")

# Comparar
templates_normalized = [t.replace('_', '').replace('/', '_') for t in templates]
missing_in_workers = []

for template in templates:
    normalized = template.replace('_', '').replace('/', '_').replace('-', '')
    
    # Verificar se existe função correspondente
    found = False
    for page in pages_in_workers:
        if page.replace('_', '') == normalized:
            found = True
            break
    
    if not found:
        missing_in_workers.append(template)

print(f"\n⚠️  Templates faltando no Workers ({len(missing_in_workers)}):")
for template in sorted(missing_in_workers):
    print(f"  - {template}")

print("\n" + "=" * 60)
print("💡 PRÓXIMOS PASSOS")
print("=" * 60)

if missing_in_workers:
    print("\n1. Templates faltando precisam ser portados para index.py")
    print("2. Crie funções async def _NOME_page() para cada um")
    print("3. Adicione rotas no método fetch()")
else:
    print("\n✅ Todos os templates estão implementados no Workers!")
    print("\nMas podem estar DESATUALIZADOS. Para sincronizar:")
    print("1. Compare cada template Flask com sua função _page() no index.py")
    print("2. Atualize o HTML das funções se necessário")

print("\n" + "=" * 60)
