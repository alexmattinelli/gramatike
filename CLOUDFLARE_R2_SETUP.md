# Configuração do Cloudflare R2 Storage

Este guia explica como configurar o Cloudflare R2 para armazenamento de arquivos (avatares, imagens de posts, PDFs, etc.) no Gramátike.

## Pré-requisitos

- Uma conta no [Cloudflare](https://dash.cloudflare.com)
- Acesso ao plano gratuito ou pago do Cloudflare (R2 tem tier gratuito generoso)

## Passo 1: Obter Account ID

1. Acesse o [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Clique em qualquer domínio ou em **Workers & Pages**
3. Na barra lateral direita, você verá **Account ID**
4. Copie este valor para `CLOUDFLARE_ACCOUNT_ID`

## Passo 2: Criar um Bucket R2

1. No dashboard, vá em **R2 Object Storage**
2. Clique em **Create bucket**
3. Dê um nome ao bucket (ex: `gramatike`)
4. Escolha a localização (recomendado: automático ou próximo aos seus usuários)
5. Clique em **Create bucket**

## Passo 3: Habilitar Acesso Público

Para que as imagens sejam acessíveis publicamente:

### Opção A: R2.dev Subdomain (mais simples)

1. Clique no bucket criado
2. Vá em **Settings**
3. Em **Public access**, clique em **Allow Access**
4. Habilite **R2.dev subdomain**
5. Copie a URL gerada (ex: `https://pub-abc123.r2.dev`)
6. Use esta URL em `CLOUDFLARE_R2_PUBLIC_URL`

### Opção B: Domínio Personalizado (recomendado para produção)

1. Clique no bucket criado
2. Vá em **Settings**
3. Em **Custom domains**, clique em **Connect Domain**
4. Configure um subdomínio (ex: `cdn.gramatike.com.br`)
5. Use este domínio em `CLOUDFLARE_R2_PUBLIC_URL`

## Passo 4: Criar API Token para Acesso

1. Vá em **R2 Object Storage** > **Manage R2 API Tokens**
2. Clique em **Create API token**
3. Configure:
   - **Token name**: `gramatike-upload`
   - **Permissions**: Object Read & Write
   - **Specify bucket(s)**: Selecione o bucket criado
   - **TTL**: (opcional) defina uma expiração
4. Clique em **Create API Token**
5. **IMPORTANTE**: Copie os valores exibidos:
   - **Access Key ID** → `CLOUDFLARE_R2_ACCESS_KEY_ID`
   - **Secret Access Key** → `CLOUDFLARE_R2_SECRET_ACCESS_KEY`

⚠️ **O Secret Access Key só é mostrado uma vez!** Salve-o em local seguro.

## Passo 5: Configurar Variáveis de Ambiente

### Desenvolvimento Local (.env)

```env
CLOUDFLARE_ACCOUNT_ID=abc123def456
CLOUDFLARE_R2_ACCESS_KEY_ID=sua-access-key-id
CLOUDFLARE_R2_SECRET_ACCESS_KEY=sua-secret-access-key
CLOUDFLARE_R2_BUCKET=gramatike
CLOUDFLARE_R2_PUBLIC_URL=https://pub-abc123.r2.dev
```

### Produção (Cloudflare Pages)

1. Vá em **Workers & Pages** > seu projeto
2. Clique em **Settings** > **Environment Variables**
3. Adicione as mesmas variáveis acima
4. Clique em **Save**
5. **Redeploy** o projeto para aplicar

## Passo 6: Testar a Configuração

Execute o script de diagnóstico:

```bash
python diagnose_images.py
```

Deve mostrar:
```
✅ CLOUDFLARE_ACCOUNT_ID está configurada
✅ CLOUDFLARE_R2_ACCESS_KEY_ID está configurada
✅ CLOUDFLARE_R2_SECRET_ACCESS_KEY está configurada
✅ CLOUDFLARE_R2_BUCKET está configurada
✅ Conexão com R2 bem-sucedida
```

## Estrutura de Arquivos no Bucket

O Gramátike organiza os arquivos assim:

```
gramatike/
├── avatars/
│   └── {user_id}/
│       └── {timestamp}_{filename}
├── posts/
│   └── {user_id}/
│       └── {timestamp}_{filename}
├── apostilas/
│   └── {timestamp}_{filename}
├── divulgacao/
│   └── {timestamp}_{filename}
└── dinamicas/
    └── {user_id}/
        └── {timestamp}_{filename}
```

## Configuração de CORS (se necessário)

Se tiver problemas de CORS, configure no bucket:

1. Vá no bucket > **Settings** > **CORS Policy**
2. Adicione:

```json
[
  {
    "AllowedOrigins": ["https://gramatike.com.br", "http://localhost:5000"],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }
]
```

## Troubleshooting

### Erro 403 (Forbidden)
- Verifique se `CLOUDFLARE_R2_ACCESS_KEY_ID` e `CLOUDFLARE_R2_SECRET_ACCESS_KEY` estão corretos
- Confirme que o token tem permissão para o bucket específico

### Erro 404 (Not Found)
- Verifique se `CLOUDFLARE_R2_BUCKET` tem o nome correto
- Confirme que o bucket existe

### Imagens não aparecem
- Verifique se o acesso público está habilitado
- Confirme que `CLOUDFLARE_R2_PUBLIC_URL` está correto
- Teste a URL diretamente no navegador

### Timeout no upload
- Arquivos muito grandes podem causar timeout
- Considere aumentar `MAX_CONTENT_LENGTH` no Flask

## Limites do R2

**Tier Gratuito:**
- 10 GB de armazenamento/mês
- 1 milhão de operações Class A (PUT, POST, LIST)/mês
- 10 milhões de operações Class B (GET)/mês

**Pago (acima do gratuito):**
- $0.015/GB armazenamento
- $4.50/milhão operações Class A
- $0.36/milhão operações Class B

## Referências

- [Documentação oficial do Cloudflare R2](https://developers.cloudflare.com/r2/)
- [API S3 Compatível](https://developers.cloudflare.com/r2/api/s3/)
- [Preços do R2](https://developers.cloudflare.com/r2/pricing/)
