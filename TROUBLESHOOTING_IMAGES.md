# Solução de Problemas com Imagens - Gramátike

## 🔍 Problema: "As imagens não estão funcionando"

Este documento ajuda a diagnosticar e resolver problemas com imagens que não aparecem no Gramátike.

## 🚀 Início Rápido

### Passo 1: Execute o Diagnóstico Automático

```bash
python diagnose_images.py
```

Este script verifica automaticamente sua configuração e identifica problemas comuns.

### Passo 2: Siga o Guia de Configuração

Se o diagnóstico identificar problemas, siga o guia completo em:
- [SUPABASE_BUCKET_SETUP.md](SUPABASE_BUCKET_SETUP.md)

## 📋 Checklist Rápido

- [ ] **Variáveis de ambiente configuradas?**
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `SUPABASE_BUCKET`

- [ ] **Bucket criado no Supabase?**
  - Vá em Storage → seu projeto
  - Bucket deve existir com o nome correto

- [ ] **Bucket é público?**
  - Storage → bucket → Settings
  - "Public bucket" deve estar marcado

- [ ] **Políticas RLS configuradas?**
  - Storage → bucket → Policies
  - Deve ter política de SELECT para acesso público

- [ ] **Service role key está correta?**
  - Settings → API → service_role key
  - Não confundir com anon public key

## 🔧 Diagnóstico Manual

### 1. Verificar Variáveis de Ambiente

#### Em Desenvolvimento Local (.env)

```bash
# Verifique se o arquivo .env existe e contém:
cat .env | grep SUPABASE
```

Deve mostrar algo como:
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
SUPABASE_BUCKET=avatars
```

#### Em Produção (Vercel)

1. Acesse o projeto no Vercel
2. Vá em **Settings** → **Environment Variables**
3. Verifique que as 3 variáveis existem e estão preenchidas
4. Se adicionou ou modificou recentemente, faça um **redeploy**

### 2. Verificar Supabase

#### Testar Upload Manual

1. Acesse seu projeto no Supabase
2. Vá em **Storage** → seu bucket
3. Tente fazer upload de uma imagem de teste
4. Se falhar, o bucket pode não existir ou você não tem permissões

#### Testar Acesso Público

1. Após upload bem-sucedido, clique na imagem
2. Copie a URL pública
3. Abra em uma nova aba anônima/privada
4. Se a imagem não carregar → políticas não estão configuradas

### 3. Inspecionar URLs Geradas

No navegador:

1. Abra o site (F12 para DevTools)
2. Vá na aba **Console**
3. Tente criar um post com imagem
4. Verifique se aparecem mensagens de erro
5. Vá na aba **Network**
6. Filtre por "img"
7. Veja quais URLs estão sendo geradas e qual o status HTTP

URLs corretas devem ser:
```
https://xxxxx.supabase.co/storage/v1/object/public/avatars/posts/1/12345_image.jpg
```

## ❌ Problemas Comuns e Soluções

### Problema 1: Erro 403 (Forbidden)

**Sintoma**: Imagens aparecem como "Imagem não disponível" ou quebradas

**Causa**: Bucket não tem acesso público configurado

**Solução**:
1. No Supabase, vá em Storage → seu bucket → Policies
2. Crie uma política de SELECT:
   ```sql
   CREATE POLICY "Public Access"
   ON storage.objects FOR SELECT
   USING ( bucket_id = 'avatars' );
   ```
3. Ou marque o bucket como "Public bucket" nas configurações

### Problema 2: Erro 401 (Unauthorized) no Upload

**Sintoma**: Imagens não são enviadas, erro ao criar post

**Causa**: Service role key inválida ou não configurada

**Solução**:
1. Verifique que está usando `service_role` key e NÃO `anon public`
2. No Supabase: Settings → API → copie a `service_role` key
3. Atualize a variável `SUPABASE_SERVICE_ROLE_KEY`
4. No Vercel, redeploy após atualizar

### Problema 3: Erro 404 (Not Found)

**Sintoma**: URL da imagem retorna "não encontrado"

**Causa**: Bucket não existe ou nome está incorreto

**Solução**:
1. Verifique o nome do bucket no Supabase
2. Atualize `SUPABASE_BUCKET` com o nome correto
3. Ou crie um bucket com o nome especificado

### Problema 4: Imagens Não Carregam Localmente

**Sintoma**: Upload funciona mas imagens não aparecem

**Causa**: Arquivo está sendo salvo localmente ao invés do Supabase

**Solução**:
1. Verifique que as variáveis de ambiente estão no `.env`
2. Reinicie o servidor Flask após configurar `.env`
3. Verifique os logs para mensagens como "Supabase não configurado"

### Problema 5: Funciona Localmente mas Não em Produção

**Sintoma**: Tudo OK no desenvolvimento mas falha no Vercel

**Causa**: Variáveis de ambiente não estão no Vercel

**Solução**:
1. Vá em Vercel → Settings → Environment Variables
2. Adicione as 3 variáveis obrigatórias
3. **IMPORTANTE**: Faça redeploy após configurar
4. Aguarde alguns minutos para propagação

### Problema 6: CORS Error

**Sintoma**: Erro de CORS no console do navegador

**Causa**: Domínio não está permitido nas configurações do Supabase

**Solução**:
1. No Supabase: Settings → API → CORS Configuration
2. Adicione sua URL do Vercel (ex: `https://gramatike.vercel.app`)
3. Adicione também `http://localhost:5000` para desenvolvimento
4. Clique em Save

### Problema 7: Imagens Antigas Funcionam, Novas Não

**Sintoma**: Imagens antigas carregam mas novas não

**Causa**: Políticas foram desabilitadas ou bucket mudou

**Solução**:
1. Verifique se as políticas ainda existem no Supabase
2. Veja se o nome do bucket mudou
3. Verifique se a service role key foi regenerada

## 🔍 Logs e Debug

### Ver Logs da Aplicação

#### Desenvolvimento Local
```bash
# Os logs aparecem no terminal onde você rodou flask run
# Procure por mensagens como:
# "Uploading to Supabase: ..."
# "Upload successful: ..."
# "Upload failed: HTTP 403"
```

#### Produção (Vercel)
```bash
# No dashboard do Vercel:
# 1. Clique no seu projeto
# 2. Vá em "Deployments"
# 3. Clique no deployment ativo
# 4. Vá em "Logs" ou "Functions"
# 5. Procure por erros relacionados a "upload" ou "storage"
```

### Debug no Navegador

1. Abra DevTools (F12)
2. Vá na aba **Console**
3. Procure por warnings:
   - "Imagem falhou ao carregar: ..."
4. Vá na aba **Network**
5. Filtre por imagens que falharam (status 403, 404, etc.)
6. Clique na requisição falha
7. Veja a URL exata e a resposta do servidor

### Debug no Backend

Adicione logging temporário em `gramatike_app/routes/__init__.py`:

```python
# Na função api_posts_multi_create(), após linha 2044:
logger = logging.getLogger(__name__)
logger.info(f"Tentando upload: {remote_path}")
logger.info(f"URL resultante: {public_url}")
```

## 📊 Status HTTP e Significados

| Código | Significado | Possível Causa |
|--------|-------------|----------------|
| 200 | OK | Upload bem-sucedido |
| 401 | Unauthorized | Service key inválida |
| 403 | Forbidden | Sem permissão de leitura |
| 404 | Not Found | Bucket não existe |
| 413 | Too Large | Imagem muito grande (>3MB) |
| 500 | Server Error | Erro no Supabase |

## 🎯 Teste Passo a Passo

### Teste 1: Variáveis de Ambiente

```bash
python diagnose_images.py
# Deve mostrar: ✅ SUPABASE_URL está configurada
# Deve mostrar: ✅ SUPABASE_SERVICE_ROLE_KEY está configurada
# Deve mostrar: ✅ SUPABASE_BUCKET está configurada
```

### Teste 2: Upload

```bash
python diagnose_images.py
# Deve mostrar: ✅ Upload de teste realizado com sucesso!
# Deve mostrar uma URL pública
```

### Teste 3: Acesso Público

```bash
python diagnose_images.py
# Deve mostrar: ✅ Imagem acessível publicamente!
```

### Teste 4: No Aplicativo

1. Acesse o Gramátike
2. Crie um novo post
3. Adicione uma imagem (< 3MB)
4. Publique o post
5. Verifique que a imagem aparece no feed
6. Abra o console (F12) e veja se há erros

## 🆘 Ainda Não Funciona?

Se após seguir todos os passos acima ainda tiver problemas:

1. **Execute o diagnóstico novamente**:
   ```bash
   python diagnose_images.py > diagnostico.txt
   ```

2. **Capture logs**:
   - No navegador: Console e Network tabs (screenshot)
   - No servidor: logs do Flask ou Vercel

3. **Abra uma issue no GitHub** com:
   - Resultado do `diagnose_images.py`
   - Screenshots dos erros no navegador
   - Logs do servidor (sem expor credentials!)
   - Passos que você já tentou

4. **Verifique a documentação do Supabase**:
   - [Storage Quickstart](https://supabase.com/docs/guides/storage)
   - [RLS Policies](https://supabase.com/docs/guides/auth/row-level-security)

## 📚 Documentos Relacionados

- [SUPABASE_BUCKET_SETUP.md](SUPABASE_BUCKET_SETUP.md) - Setup completo
- [README.md](README.md#supabase-storage) - Configuração geral
- [SUPABASE_UPLOAD_FIX.md](SUPABASE_UPLOAD_FIX.md) - Implementação técnica

## 💡 Dicas de Prevenção

1. **Sempre teste após configurar**: Use `diagnose_images.py`
2. **Não compartilhe a service_role key**: É secreta!
3. **Redeploy após mudar variáveis**: No Vercel
4. **Use nomes consistentes**: Para buckets
5. **Documente mudanças**: Se alterar configurações
6. **Backup de políticas**: Anote as RLS policies configuradas
7. **Monitore logs**: Especialmente após mudanças

## 🔐 Segurança

⚠️ **NUNCA**:
- Exponha a `service_role` key no frontend
- Commit a key no Git
- Compartilhe a key em issues/PRs públicas
- Use a `anon public` key no backend

✅ **SEMPRE**:
- Use variáveis de ambiente
- Configure RLS policies restritivas
- Monitore uploads suspeitos
- Revogue keys se exposta acidentalmente
