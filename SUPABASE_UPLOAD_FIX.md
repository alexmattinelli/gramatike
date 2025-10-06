# Fix para Upload de Fotos e PDFs (Supabase Storage)

## Problema Identificado

O aplicativo estava tentando salvar arquivos (fotos de posts, PDFs de apostilas, imagens de divulgação) no sistema de arquivos local. Isso não funciona em ambientes serverless como Vercel, onde o sistema de arquivos é read-only ou efêmero.

## Solução Implementada

Adicionado suporte ao Supabase Storage para todos os tipos de upload de arquivos, com fallback para armazenamento local caso o Supabase não esteja configurado.

### Mudanças no Código

#### 1. `/gramatike_app/utils/storage.py`
- Adicionadas novas funções auxiliares:
  - `build_post_image_path()` - gera caminhos para imagens de posts
  - `build_apostila_path()` - gera caminhos para PDFs de apostilas
  - `build_divulgacao_path()` - gera caminhos para imagens de divulgação

#### 2. `/gramatike_app/routes/__init__.py`
- **`api_posts_multi_create()`**: Atualizada para tentar upload no Supabase primeiro
  - Se Supabase estiver configurado → salva no Supabase e retorna URL pública
  - Se Supabase não estiver configurado → fallback para armazenamento local
  
- **`admin_divulgacao_upload()`**: Atualizada da mesma forma
  - Tenta Supabase primeiro, depois fallback local

#### 3. `/gramatike_app/routes/admin.py`
- **`edu_publicar()`**: Seção de upload de apostilas (PDFs) atualizada
  - Tenta Supabase primeiro, depois fallback local
  - Nota: Geração de thumbnail de PDF só funciona no modo local (requer arquivo físico)

### Configuração Necessária

Para que os uploads funcionem em produção (Vercel), você precisa configurar as seguintes variáveis de ambiente:

```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=sua-service-role-key-aqui
SUPABASE_BUCKET=avatars
```

#### Passos no Supabase:

1. **Criar bucket de storage**:
   - Vá para Storage no painel do Supabase
   - Crie um bucket chamado "avatars" (ou outro nome de sua escolha)

2. **Configurar políticas de acesso**:
   - O bucket precisa permitir leitura pública para que as URLs funcionem
   - Upload/update devem ser permitidos via service role key
   
3. **Obter credenciais**:
   - SUPABASE_URL: encontrado em Settings > API > Project URL
   - SUPABASE_SERVICE_ROLE_KEY: encontrado em Settings > API > service_role key (secret)

4. **Configurar no Vercel**:
   - Settings > Environment Variables
   - Adicione as 3 variáveis acima
   - Redeploy o aplicativo

### Comportamento

- **Com Supabase configurado**: Todos os arquivos são salvos no Supabase Storage e URLs públicas são retornadas
- **Sem Supabase**: Arquivos são salvos localmente (funciona apenas em desenvolvimento local)

### Testado

✓ Sintaxe Python validada
✓ Funções de geração de path testadas
✓ Imports verificados

### Próximos Passos

1. Configure as credenciais do Supabase no Vercel
2. Teste upload de foto em um post
3. Teste upload de PDF de apostila
4. Teste upload de imagem de divulgação
5. Verifique que as URLs públicas funcionam corretamente
