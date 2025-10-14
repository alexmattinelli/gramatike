# 🧪 Guia de Teste Visual: Fix "Falha ao salvar" Resumo de Podcast

## 📝 Passo a Passo para Testar

### Pré-requisitos
- Estar logado como **admin** ou **superadmin**
- Ter pelo menos 1 podcast cadastrado no sistema

---

## ✅ Teste 1: Editar Podcast com Resumo Curto

### Passos:
1. Acesse o **Dashboard Admin**
2. Clique na aba **"Edu"**
3. Selecione a seção **"Podcasts"**
4. Clique no botão **"Editar"** (ícone de engrenagem) em qualquer podcast
5. No campo **"Resumo"**, adicione um texto curto:
   ```
   Este é um podcast sobre gramática portuguesa.
   ```
6. Clique em **"Salvar"**

### ✅ Resultado Esperado:
- ✅ O diálogo deve **fechar automaticamente**
- ✅ A lista de podcasts deve **recarregar**
- ✅ **Nenhuma** mensagem de erro "Falha ao salvar"
- ✅ Ao reabrir o editor, o resumo deve estar salvo

---

## ✅ Teste 2: Editar Podcast com Resumo Longo (1090 caracteres)

### Passos:
1. Acesse o **Dashboard Admin** → **Edu** → **Podcasts**
2. Clique em **"Editar"** em qualquer podcast
3. No campo **"Resumo"**, cole o seguinte texto longo (1090 chars):

```
Neste texto, proponho uma abordagem de neutralização de gênero em português brasileiro na perspectiva do sistema linguístico. Para isso, parto de considerações sobre a caracterização de mudanças deliberadas e sobre os padrões de marcação e produtividade de gênero gramatical na língua. São avaliados, nessa perspectiva, quatro tipos de empregos correntes de gênero inclusivo: uso de feminino marcado no caso de substantivos comuns de dois gêneros (ex. a presidenta); emprego de formas femininas e masculinas, sobretudo em vocativos, em vez do uso genérico do masculino (ex. alunas e alunos); inclusão de novas marcas no final de nomes e adjetivos, como x e @ (ex. amigx, amig@), ou ampliação da função de marcas já existentes, como -e (ex. amigue); alteração na base de pronomes e artigos (ex. ile, le). Desses empregos, além do feminino marcado e do contraste entre formas femininas e masculinas, que já têm uso significativo na língua, proponho que, no domínio da palavra, -e encontra condições menos limitadas para expansão no sistema no subconjunto de substantivos e adjetivos sexuados.
```

4. Clique em **"Salvar"**

### ✅ Resultado Esperado:
- ✅ O diálogo deve **fechar automaticamente**
- ✅ A lista de podcasts deve **recarregar**
- ✅ **Nenhuma** mensagem de erro "Falha ao salvar"
- ✅ Ao reabrir o editor, o resumo completo (1090 chars) deve estar salvo

---

## ✅ Teste 3: Editar Outros Campos (Título, Autor, URL)

### Passos:
1. Acesse o **Dashboard Admin** → **Edu** → **Podcasts**
2. Clique em **"Editar"** em qualquer podcast
3. Modifique:
   - **Título**: "Podcast sobre Linguagem Neutra"
   - **Autore**: "Dr. João Silva"
   - **URL**: Cole um iframe do Spotify
   - **Resumo**: Adicione qualquer texto
4. Clique em **"Salvar"**

### ✅ Resultado Esperado:
- ✅ Todas as alterações devem ser salvas
- ✅ Nenhum erro deve aparecer
- ✅ Ao reabrir o editor, todos os campos devem refletir as mudanças

---

## ❌ Teste Regressão: Verificar que NÃO quebrou outras funcionalidades

### Teste 4: Editar Artigo
1. Vá para **Edu** → **Artigos**
2. Edite qualquer artigo
3. Salve as alterações
4. ✅ Deve continuar funcionando normalmente

### Teste 5: Editar Apostila
1. Vá para **Edu** → **Apostilas**
2. Edite qualquer apostila
3. Salve as alterações
4. ✅ Deve continuar funcionando normalmente

---

## 🐛 O que verificar em caso de erro:

### Se aparecer "Falha ao salvar":
1. **Abra o Console do Browser** (F12 → Console)
2. Verifique se há erro de **CSRF** ou **403 Forbidden**
3. Se sim, significa que o fix não foi aplicado corretamente

### Se aparecer "Erro de rede":
1. Verifique a **conexão com o servidor**
2. Verifique se a rota `/admin/edu/content/<id>/update` está respondendo
3. Veja os logs do servidor Flask

---

## 📊 Checklist de Validação

Antes de marcar como ✅ concluído, verifique:

- [ ] ✅ Resumo curto (< 100 chars) salva sem erro
- [ ] ✅ Resumo médio (200-500 chars) salva sem erro
- [ ] ✅ Resumo longo (1000+ chars) salva sem erro
- [ ] ✅ Resumo muito longo (1900 chars) salva sem erro
- [ ] ✅ Todos os outros campos (título, autor, URL) salvam corretamente
- [ ] ✅ Edição de artigos continua funcionando
- [ ] ✅ Edição de apostilas continua funcionando
- [ ] ✅ Nenhum erro no console do browser
- [ ] ✅ Nenhum erro nos logs do servidor

---

## 🔍 Detalhes Técnicos do Fix

### O que foi corrigido:
1. **Adicionado CSRF token** ao formulário `podcastEditForm`
   - Linha 997: `<input type="hidden" name="csrf_token" value="{{ csrf_token() if csrf_token is defined else '' }}" />`

2. **Adicionado `credentials: 'same-origin'`** ao fetch request
   - Linha 1108: `fetch(..., { method:'POST', body: fd, credentials: 'same-origin' })`

### Por que funcionou:
- O Flask-WTF valida CSRF em todas as rotas POST
- Sem o token, o servidor retorna **400 Bad Request**
- Sem `credentials`, os cookies de sessão não são enviados
- Resultado: "Falha ao salvar"

### Referência:
- Mesmo padrão usado em `artigos.html` e `apostilas.html`
- Documentação: `FIX_PODCAST_RESUMO_SAVE.md`
