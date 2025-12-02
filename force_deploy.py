#!/usr/bin/env python3
"""
Force deploy para Cloudflare Workers - bypassa problemas de terminal
"""
import os
import subprocess
import sys

# Token API
TOKEN = "VR_NPs75hlB1xC_TLiyj6uhn-piwFHHGJ5bWEAv2"

print("=" * 70)
print("🚀 GRAMÁTIKE - DEPLOY FORÇADO")
print("=" * 70)

# Verificar tamanho do arquivo
try:
    size = os.path.getsize("index.py")
    lines = sum(1 for _ in open("index.py"))
    size_mb = size / (1024 * 1024)
    
    print(f"\n📊 Arquivo index.py:")
    print(f"   • Linhas: {lines:,}")
    print(f"   • Tamanho: {size:,} bytes ({size_mb:.2f} MB)")
    
    if size_mb > 3:
        print(f"   ⚠️  AVISO: Arquivo ainda excede 3MB!")
        print(f"   • Plano gratuito permite até 3MB")
        print(f"   • Diferença: +{(size_mb - 3):.2f} MB")
    else:
        print(f"   ✅ Arquivo está dentro do limite de 3MB!")
        
except Exception as e:
    print(f"⚠️  Erro ao verificar arquivo: {e}")

print("\n" + "=" * 70)
print("📤 INICIANDO DEPLOY...")
print("=" * 70 + "\n")

# Configurar ambiente
env = os.environ.copy()
env['CLOUDFLARE_API_TOKEN'] = TOKEN

# Executar deploy
try:
    result = subprocess.run(
        ['npx', 'wrangler', 'deploy'],
        env=env,
        capture_output=True,
        text=True,
        cwd='/workspaces/gramatike'
    )
    
    # Mostrar output
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    # Verificar resultado
    print("\n" + "=" * 70)
    if result.returncode == 0:
        print("✅ DEPLOY CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        print("\n🌐 Site disponível em: https://www.gramatike.com.br")
        print("\n📋 Próximos passos:")
        print("   1. Testar /configuracoes")
        print("   2. Testar /suporte")
        print("   3. Testar /perfil")
        print("   4. Verificar CSS carregando corretamente")
        sys.exit(0)
    else:
        print("❌ DEPLOY FALHOU!")
        print("=" * 70)
        print(f"\nCódigo de saída: {result.returncode}")
        sys.exit(1)
        
except FileNotFoundError:
    print("❌ ERRO: wrangler não encontrado!")
    print("\nInstale com: npm install -g wrangler")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERRO INESPERADO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
