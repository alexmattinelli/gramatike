# Build Instructions for Cloudflare Pages

## Configuração no Dashboard Cloudflare

Vá em: **Workers & Pages** → **gramatike** → **Settings** → **Builds & deployments**

### Build configuration

**Framework preset:** None

**Build command:**
```bash
npm run build
```

**Build output directory:**
```
public
```

**Root directory:**
```
/
```

### Environment variables (opcional)

Nenhuma variável de ambiente é necessária para o build.

As configurações do D1, R2, e secrets são configuradas via `wrangler.toml` e o dashboard.

## Build local

```bash
# Instalar dependências
npm install

# Rodar localmente
npm run dev

# Deploy manual (se necessário)
npm run deploy
```

## Troubleshooting

### Erro: "pip install -r requirements.txt"

Se você ver esse erro, significa que o Cloudflare ainda está usando configuração antiga de Python.

**Solução:**

1. Vá em **Settings** → **Builds & deployments**
2. Em **Build command**, coloque: `npm run build`
3. **NÃO** coloque nada relacionado a `pip` ou Python
4. Salve e faça **Retry deployment**

### Erro: "python_workers" compatibility flag

Se aparecer erro sobre `python_workers`:

1. Vá em **Settings** → **Functions** → **Compatibility Flags**
2. **Remova/delete** qualquer referência a `python_workers`
3. Deixe vazio ou adicione apenas flags modernas do JavaScript
4. Salve

## Migration notes

Este projeto foi migrado de Python (Pyodide) para TypeScript puro.

- ❌ Não usa mais Python
- ❌ Não usa mais Jinja2
- ✅ 100% TypeScript
- ✅ Cloudflare Pages Functions (JavaScript nativo)
- ✅ Templates via string literals
