# 🔧 Cloudflare R2 Public Access Setup - Fix 404 Error

## 🚨 Problema

Ao acessar o site pelo celular (ou qualquer dispositivo), você recebe o erro:

```
Error 404
Object not found
This object does not exist or is not publicly accessible at this URL. 
Check the URL of the object that you're looking for or contact the owner 
to enable Public access.

Is this your bucket?
Learn how to enable Public Access
```

## 🎯 Causa Raiz

Este erro ocorre porque o **bucket R2 não está configurado com acesso público**. Quando o navegador tenta carregar imagens (avatars, fotos de perfil, etc.) do bucket R2, o bucket rejeita o acesso porque não tem um domínio público configurado.

## ✅ Solução Completa

### Passo 1: Acessar o Cloudflare Dashboard

1. Faça login no [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Selecione sua conta
3. No menu lateral, clique em **R2**

### Passo 2: Localizar Seu Bucket

1. Na lista de buckets, encontre o bucket chamado **"bucket"** (ou "gramatike" se você renomeou)
2. Clique no nome do bucket para abrir as configurações

### Passo 3: Habilitar Public Access

Existem **duas opções** para habilitar acesso público:

#### Opção A: Usar Domínio Público Padrão do R2 (Mais Rápido)

1. Dentro do bucket, clique na aba **Settings**
2. Role até a seção **Public Access**
3. Clique em **Allow Access** ou **Connect Domain**
4. Selecione **R2.dev subdomain**
5. Clique em **Allow Access**

Você receberá um domínio público no formato:
```
https://pub-[hash-aleatório].r2.dev
```

**Exemplo:**
```
https://pub-1a2b3c4d5e6f7g8h.r2.dev
```

#### Opção B: Usar Domínio Personalizado (Recomendado para Produção)

Se você tem um domínio próprio (ex: `gramatike.com.br`):

1. Na seção **Public Access** do bucket
2. Clique em **Connect Domain**
3. Selecione **Custom domain**
4. Digite um subdomínio, por exemplo:
   - `files.gramatike.com.br`
   - `cdn.gramatike.com.br`
   - `storage.gramatike.com.br`
5. Siga as instruções para configurar o registro DNS CNAME
6. Aguarde a propagação do DNS (pode levar até 24h, mas geralmente é rápido)

### Passo 4: Configurar CORS (Cross-Origin Resource Sharing)

Para permitir que o site carregue recursos do R2, você precisa configurar CORS:

1. Ainda nas configurações do bucket, encontre a seção **CORS policy**
2. Clique em **Edit CORS policy**
3. Adicione a seguinte configuração:

```json
[
  {
    "AllowedOrigins": [
      "https://www.gramatike.com.br",
      "https://gramatike.com.br",
      "https://*.pages.dev"
    ],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": [],
    "MaxAgeSeconds": 3600
  }
]
```

**Para desenvolvimento local**, adicione também:
```json
[
  {
    "AllowedOrigins": [
      "https://www.gramatike.com.br",
      "https://gramatike.com.br",
      "https://*.pages.dev",
      "http://localhost:8788",
      "http://localhost:3000"
    ],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": [],
    "MaxAgeSeconds": 3600
  }
]
```

4. Clique em **Save**

### Passo 5: Atualizar Variáveis de Ambiente (se aplicável)

Se o código do Gramátike usa variáveis de ambiente para construir URLs do R2, você precisa configurá-las:

1. No Cloudflare Dashboard, vá em **Workers & Pages**
2. Selecione o projeto **gramatike**
3. Clique em **Settings** → **Environment Variables**
4. Adicione (ou atualize) a variável:

**Nome:** `CLOUDFLARE_R2_PUBLIC_URL`  
**Valor:** Seu domínio público do R2 (ex: `https://pub-1a2b3c4d5e6f7g8h.r2.dev`)

5. Clique em **Save**
6. Faça um novo deploy (ou trigger um rebuild) para aplicar as mudanças

### Passo 6: Testar o Acesso

#### Teste 1: Acesso Direto ao Bucket

Teste se o bucket está acessível publicamente:

```bash
# Substitua pela URL do seu bucket
curl -I https://pub-1a2b3c4d5e6f7g8h.r2.dev
```

Você deve receber um status `200 OK` ou `403 Forbidden` (403 é OK, significa que o bucket existe mas o objeto específico não).

Se receber `404`, o Public Access ainda não está configurado corretamente.

#### Teste 2: Upload de Avatar

1. Acesse o site: `https://www.gramatike.com.br`
2. Faça login
3. Vá em **Configurações** ou **Meu Perfil**
4. Tente fazer upload de uma imagem de avatar
5. Verifique se a imagem aparece corretamente

#### Teste 3: Acesso Mobile

1. Abra o site no celular: `https://www.gramatike.com.br`
2. Navegue pelas páginas (Feed, Perfil, etc.)
3. Verifique se todas as imagens carregam corretamente
4. Não deve aparecer mais o erro 404

## 📋 Checklist de Configuração

Use este checklist para garantir que tudo está configurado:

- [ ] Bucket R2 criado (nome: "bucket" ou "gramatike")
- [ ] Public Access habilitado (domínio público configurado)
- [ ] CORS policy configurada no bucket
- [ ] Variável `CLOUDFLARE_R2_PUBLIC_URL` configurada (se necessário)
- [ ] Deploy realizado após configurar variáveis
- [ ] Teste de acesso direto ao bucket (curl) bem-sucedido
- [ ] Upload de avatar funciona
- [ ] Site acessível e funcional no celular
- [ ] Nenhum erro 404 ao carregar imagens

## 🔍 Troubleshooting

### Ainda recebo erro 404 após configurar

**Possíveis causas:**

1. **Propagação DNS (domínio personalizado):**
   - Aguarde até 24h para propagação completa
   - Use o domínio `r2.dev` temporariamente

2. **Cache do navegador:**
   - Limpe o cache do navegador
   - Tente em modo anônimo/privado

3. **CORS não configurado:**
   - Verifique se a política CORS está salva
   - Confirme que os domínios estão corretos

4. **Variável de ambiente não atualizada:**
   - Verifique se `CLOUDFLARE_R2_PUBLIC_URL` está configurada
   - Faça um novo deploy após alterar variáveis

### Como verificar se o Public Access está ativo?

1. No dashboard do bucket R2
2. Veja a seção **Public Access**
3. Deve mostrar um domínio (ex: `pub-xxxx.r2.dev`) com status **Active**

### O bucket está público mas ainda recebo 404

Isso pode significar que:
- O objeto (arquivo) específico não existe no bucket
- O caminho do objeto está incorreto
- Verifique os logs do Cloudflare Workers para ver quais URLs estão sendo acessadas

## 📚 Recursos Adicionais

- [Cloudflare R2 - Public Buckets](https://developers.cloudflare.com/r2/buckets/public-buckets/)
- [Cloudflare R2 - CORS Configuration](https://developers.cloudflare.com/r2/buckets/cors/)
- [Cloudflare Pages - Environment Variables](https://developers.cloudflare.com/pages/platform/build-configuration/#environment-variables)

## 🎉 Resultado Esperado

Após seguir todos os passos:

✅ O site carrega completamente no celular sem erros 404  
✅ Avatars e imagens de perfil aparecem corretamente  
✅ Upload de arquivos funciona normalmente  
✅ A experiência mobile é idêntica à desktop  

---

**Última atualização:** 2026-02-03  
**Versão do Gramátike:** v2.2.0
