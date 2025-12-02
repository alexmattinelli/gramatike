#!/usr/bin/env python3
"""Deploy script for Gramátike - bypasses terminal filesystem issues"""
import os
import subprocess

# Set API token
os.environ['CLOUDFLARE_API_TOKEN'] = 'VR_NPs75hlB1xC_TLiyj6uhn-piwFHHGJ5bWEAv2'

print("🚀 Deploying Gramátike to Cloudflare Workers...")
print("=" * 60)

# Check file size
try:
    size_bytes = os.path.getsize('index.py')
    size_mb = size_bytes / (1024 * 1024)
    print(f"📊 index.py size: {size_bytes:,} bytes ({size_mb:.2f} MB)")
    
    if size_mb > 3:
        print(f"⚠️  WARNING: File exceeds 3MB free tier limit!")
    else:
        print(f"✅ File is under 3MB limit!")
    print()
except Exception as e:
    print(f"⚠️  Could not check file size: {e}\n")

# Test token
print("🔑 Testing Cloudflare API token...")
result = subprocess.run([
    'curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
    'https://api.cloudflare.com/client/v4/user',
    '-H', 'Authorization: Bearer VR_NPs75hlB1xC_TLiyj6uhn-piwFHHGJ5bWEAv2'
], capture_output=True, text=True)

if result.stdout.strip() == '200':
    print("✅ Token válido!\n")
else:
    print(f"❌ Token inválido (HTTP {result.stdout.strip()})\n")
    exit(1)

# Deploy
print("📤 Deploying to Cloudflare...")
print("-" * 60)
result = subprocess.run([
    'npx', 'wrangler', 'deploy'
], capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print(result.stderr)

if result.returncode == 0:
    print("=" * 60)
    print("✅ Deploy concluído com sucesso!")
    print("🌐 Site: https://www.gramatike.com.br")
else:
    print("=" * 60)
    print(f"❌ Deploy falhou (exit code: {result.returncode})")
    exit(result.returncode)
