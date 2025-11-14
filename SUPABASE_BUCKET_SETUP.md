# Guia de Configuração do Supabase Storage para Imagens

## Problema Comum: "As imagens não estão funcionando"

Se as imagens não estão sendo exibidas no Gramátike, o problema mais comum é que o bucket do Supabase não está configurado corretamente para permitir acesso público de leitura.

## Pré-requisitos

- Uma conta no [Supabase](https://supabase.com)
- Um projeto criado no Supabase
- Acesso às configurações do projeto

## Passo 1: Criar o Bucket de Storage

1. Acesse o painel do seu projeto no Supabase
2. No menu lateral, clique em **Storage**
3. Clique em **New bucket** (Novo bucket)
4. Configure o bucket:
   - **Nome**: `avatars` (ou o nome que você preferir)
   - **Public bucket**: ✅ Marque esta opção (IMPORTANTE!)
   - **File size limit**: 3MB (ou conforme sua necessidade)
   - **Allowed MIME types**: `image/jpeg, image/png, image/webp, image/gif, application/pdf`
5. Clique em **Create bucket**

## Passo 2: Configurar Políticas de Acesso (RLS Policies)

Mesmo que o bucket seja público, você precisa criar políticas para permitir leitura e upload.

### Opção A: Configuração Automática (Recomendada)

1. Clique no bucket `avatars` que você acabou de criar
2. Clique na aba **Policies**
3. Clique em **New policy**
4. Escolha o template **"Enable read access for all users"**
5. Revise a política e clique em **Save policy**

### Opção B: Configuração Manual (Avançada)

Se preferir criar as políticas manualmente:

#### Política 1: Leitura Pública (SELECT)

```sql
CREATE POLICY "Public Access"
ON storage.objects FOR SELECT
USING ( bucket_id = 'avatars' );
```

Esta política permite que qualquer pessoa (mesmo sem autenticação) visualize as imagens.

#### Política 2: Upload Autenticado (INSERT)

```sql
CREATE POLICY "Authenticated Upload"
ON storage.objects FOR INSERT
WITH CHECK ( bucket_id = 'avatars' AND auth.role() = 'authenticated' );
```

Esta política permite que usuários autenticados façam upload de imagens.

#### Política 3: Upload via Service Role Key

Para que o backend possa fazer upload usando a service role key, certifique-se de que a política permite uploads com `auth.role() = 'service_role'` ou desabilite RLS temporariamente durante testes.

## Passo 3: Obter Credenciais do Supabase

1. No menu lateral, vá em **Settings** → **API**
2. Anote as seguintes informações:
   - **Project URL**: algo como `https://xxxxx.supabase.co`
   - **anon public**: chave pública (não é usada no backend)
   - **service_role**: chave secreta (⚠️ NUNCA compartilhe ou exponha no frontend!)

## Passo 4: Configurar Variáveis de Ambiente

### Desenvolvimento Local (`.env`)

Crie ou edite o arquivo `.env` na raiz do projeto:

```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_BUCKET=avatars
```

### Produção (Vercel)

1. Acesse o projeto no Vercel
2. Vá em **Settings** → **Environment Variables**
3. Adicione as 3 variáveis:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_BUCKET`
4. Certifique-se de selecionar **Production**, **Preview** e **Development** para cada variável
5. Clique em **Save**
6. **IMPORTANTE**: Faça um novo deploy para que as variáveis tenham efeito

## Passo 5: Testar a Configuração

### Teste Manual no Supabase

1. Acesse o bucket no painel do Supabase
2. Tente fazer upload de uma imagem de teste
3. Após o upload, clique na imagem
4. Copie a URL pública (deve ser algo como: `https://xxxxx.supabase.co/storage/v1/object/public/avatars/test.jpg`)
5. Cole a URL em uma nova aba do navegador
6. ✅ Se a imagem carregar, a configuração de leitura pública está correta
7. ❌ Se mostrar erro 403 ou 401, revise as políticas de acesso

### Teste no Aplicativo

Use o script de diagnóstico incluído no projeto:

```bash
python diagnose_images.py
```

Este script verifica:
- ✅ Variáveis de ambiente configuradas
- ✅ Conectividade com Supabase
- ✅ Permissões de upload
- ✅ Permissões de leitura pública

## Problemas Comuns e Soluções

### 1. Erro 403 (Forbidden) ao acessar imagens

**Causa**: Bucket não tem políticas de leitura pública configuradas

**Solução**:
- Verifique que o bucket está marcado como "Public bucket"
- Crie a política de leitura pública (SELECT) conforme Passo 2

### 2. Erro 401 (Unauthorized) ao fazer upload

**Causa**: Service role key inválida ou não configurada

**Solução**:
- Verifique que `SUPABASE_SERVICE_ROLE_KEY` está correta
- Certifique-se de usar a chave `service_role` e NÃO a `anon public`
- No Vercel, redeploy após adicionar/modificar variáveis

### 3. Imagens aparecem quebradas (ícone de imagem quebrada)

**Causa**: URL da imagem está incorreta ou bucket não existe

**Solução**:
- Verifique que `SUPABASE_BUCKET` tem o nome correto do bucket
- Inspecione o HTML da página (F12) e veja qual URL está sendo gerada
- Teste a URL manualmente no navegador

### 4. Upload funciona localmente mas não em produção

**Causa**: Variáveis de ambiente não configuradas no Vercel

**Solução**:
- Verifique que as 3 variáveis estão configuradas no Vercel
- Certifique-se de selecionar todos os ambientes (Production, Preview, Development)
- Faça um novo deploy após configurar

### 5. Erro de CORS ao acessar imagens

**Causa**: Políticas de CORS não configuradas no Supabase

**Solução**:
1. Vá em **Settings** → **API** → **CORS**
2. Adicione a URL do seu site Vercel (ex: `https://gramatike.vercel.app`)
3. Adicione também `http://localhost:5000` para desenvolvimento local

## Verificação Final

Após configurar tudo, teste o fluxo completo:

1. ✅ Faça login no Gramátike
2. ✅ Crie um novo post com uma imagem
3. ✅ Verifique que a imagem aparece no feed
4. ✅ Clique na imagem para abrir em tela cheia
5. ✅ Acesse o perfil e verifique que a imagem aparece lá também

Se todos os passos funcionarem, sua configuração está completa! 🎉

## Recursos Adicionais

- [Documentação oficial do Supabase Storage](https://supabase.com/docs/guides/storage)
- [Políticas RLS no Supabase](https://supabase.com/docs/guides/auth/row-level-security)
- [Configurar CORS no Supabase](https://supabase.com/docs/guides/api/cors)

## Suporte

Se ainda tiver problemas após seguir este guia:

1. Execute `python diagnose_images.py` e compartilhe o resultado
2. Verifique os logs no Vercel (caso esteja em produção)
3. Verifique os logs do Supabase em **Logs** → **Storage**
4. Abra uma issue no GitHub com detalhes do erro
