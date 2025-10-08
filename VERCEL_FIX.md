# Fix: Vercel Deployment Error - "Something went wrong"

## Problema Identificado

O aplicativo estava falhando no deploy da Vercel com o erro genérico:
```
Something went wrong
There was an issue displaying the content.
Please contact us if the error persists.
```

## Causa Raiz

O erro foi causado por **duas incompatibilidades** na função `_ensure_pwa_icons()` em `gramatike_app/__init__.py`:

### 1. **Pillow 10+ Incompatibilidade** (Principal)
- O código usava `draw.textsize()`, método **removido no Pillow 10.0.0**
- Pillow atual (11.3.0) não tem esse método
- Causava `AttributeError` durante inicialização do app
- Mesmo com try-except, o erro poderia crashar o runtime serverless

### 2. **Filesystem Read-Only no Vercel**
- Código tentava criar diretórios com `os.makedirs()`
- Tentava salvar arquivos com `im.save()`
- Vercel usa filesystem **read-only** (exceto `/tmp`)
- Operações de escrita falhavam, podendo causar crashes

## Solução Aplicada

### Fix 1: Substituir `textsize()` por `textbbox()` (Pillow 10+)

**Antes:**
```python
tw, th = draw.textsize(txt, font=font)
draw.text(((size-tw)//2, (size-th)//2), txt, fill=(255,255,255,255), font=font)
```

**Depois:**
```python
# Use textbbox (Pillow 10+) em vez de textsize (deprecated)
bbox = draw.textbbox((0, 0), txt, font=font)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
draw.text(((size-tw)//2, (size-th)//2), txt, fill=(255,255,255,255), font=font)
```

### Fix 2: Tratar Filesystem Read-Only

**Criação de diretório:**
```python
# Tenta criar diretório; ignora se falhar (read-only filesystem em serverless)
try:
    os.makedirs(base_dir, exist_ok=True)
except (OSError, PermissionError):
    # Filesystem read-only (Vercel/serverless) - ícones devem existir no repo
    return
```

**Salvamento de arquivo:**
```python
# Tenta salvar; ignora se falhar (filesystem read-only)
try:
    im.convert('RGB').save(path, format='PNG')
except (OSError, PermissionError):
    # Filesystem read-only (Vercel/serverless)
    pass
```

## Por Que Funciona Agora

1. ✅ **Pillow 10+ compatível**: Usa `textbbox()` que existe em todas as versões modernas
2. ✅ **Serverless-safe**: Não crashea se não conseguir escrever arquivos
3. ✅ **Ícones pré-existentes**: Ícones já estão no repo em `gramatike_app/static/img/icons/`
4. ✅ **Graceful fallback**: App funciona mesmo se geração de ícones falhar

## Arquivos Modificados

- `gramatike_app/__init__.py` (linhas 300-305, 369-381)

## Testes Realizados

1. ✅ Import do app sem erros
2. ✅ WSGI compliance (Vercel usa WSGI)
3. ✅ Health endpoint funcional
4. ✅ Compatibilidade Pillow 10+
5. ✅ Simulação de filesystem read-only
6. ✅ Todas as rotas registradas corretamente

## Deploy na Vercel

O aplicativo agora deve fazer deploy com sucesso na Vercel. Certifique-se de que:

1. **Variáveis de ambiente** estão configuradas (ver README.md):
   - `SECRET_KEY` (obrigatório)
   - `DATABASE_URL` (PostgreSQL recomendado para produção)
   - `SUPABASE_*` (para uploads de arquivos)
   - `MAIL_*` (para envio de emails)

2. **Ícones PWA** existem no repositório:
   - `gramatike_app/static/img/icons/icon-192.png`
   - `gramatike_app/static/img/icons/icon-512.png`

3. **Python runtime** configurado no `vercel.json` (Python 3.12)

## Verificação de Deploy

Após o deploy, teste:

```bash
# Teste o health endpoint
curl https://seu-app.vercel.app/api/health

# Resposta esperada: {"status":"ok"}
```

## Próximos Passos

Se o erro persistir, verifique:

1. **Logs da Vercel**: Function logs no dashboard
2. **Variáveis de ambiente**: Todas configuradas corretamente?
3. **Dependências**: `requirements.txt` completo?
4. **Database**: PostgreSQL conectando corretamente?
