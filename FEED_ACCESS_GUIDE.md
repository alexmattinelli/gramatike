# Guia de Acesso ao Feed - Gramátike

## Resumo Executivo

O feed está **funcionando corretamente** e contém todos os recursos solicitados:
- ✅ **Postagens** (Posts feed)
- ✅ **Amigues** (Friends sidebar - seguimento mútuo)
- ✅ **Jogo da Velha** (Tic-tac-toe game)

## Como Acessar o Feed

### Para Novos Usuários

1. **Criar uma conta:**
   - Acesse `/cadastro` (ou clique em "Cadastro" na landing page)
   - Preencha o formulário de registro:
     - Nome (opcional)
     - Nome de usuárie (obrigatório, mínimo 5 caracteres, sem espaços)
     - Email (obrigatório)
     - Senha (obrigatória)
     - Gênero e pronome
     - Data de nascimento
   - Clique em "Cadastrar"

2. **Fazer login:**
   - Acesse `/login` (ou clique em "Login")
   - Entre com seu usuárie/email e senha
   - **Você será redirecionado automaticamente para o feed** (/feed)

### Para Usuários Já Cadastrados

1. **Login direto:**
   - Acesse `/login`
   - Entre com suas credenciais
   - Redirecionamento automático para `/feed`

2. **Acesso via página inicial:**
   - Acesse `/` (raiz do site)
   - Se você já está autenticade, será redirecionado para `/feed`
   - Se não está autenticade, verá a landing page

## Estrutura do Feed

O feed.html contém as seguintes seções principais:

### 1. Coluna Principal (Feed)
- **Barra de busca** - pesquisar posts, usuáries (@) e hashtags (#)
- **Botão "+" para criar post** - acessa /novo_post
- **Lista de posts** (#feed-list) - mostra posts de todes usuáries
- **Funcionalidades em cada post:**
  - Curtir/Descurtir
  - Comentar
  - Ver comentários
  - Compartilhar
  - Relatar
  - Seguir autore (se não for você mesme)
  - Excluir (se for seu post)

### 2. Coluna Lateral Direita (Desktop)

#### Card de Navegação Rápida
- Botão **Educação** - leva para /educacao
- Botão **Em breve** - recursos futuros

#### Card de Notificações
- Notificações de noves seguidories
- Notificações de curtidas em seus posts
- Badge mostrando quantidade de notificações não vistas

#### Card de Amigues
- Lista de amigues (seguimento mútuo)
- Botões de ação:
  - Suporte
  - Configurações
  - Painel Admin (apenas para admins)

#### Card de Novidades
- Divulgações e avisos da plataforma

#### Card Jogo da Velha
- Jogo vs Robo (IA)
- Você joga como X, Robo como O
- Botão para reiniciar o jogo

### 3. Barra Inferior (Mobile)
Em dispositivos móveis (width < 980px), uma barra de navegação inferior aparece com:
- Início (feed)
- Educação
- Botão central "+" para criar post
- Em breve
- Perfil / Logout

## Layout Responsivo

### Desktop (>980px)
- Layout de 2 colunas:
  - Coluna esquerda: Feed principal (960px max)
  - Coluna direita: Sidebar fixa com amigues, jogo e notificações (300px)

### Mobile (<980px)
- Layout de 1 coluna:
  - Feed ocupa largura total
  - Sidebar escondida
  - Card de ações rápidas recolhível (triângulo no topo)
  - Barra de navegação inferior fixa
  - Header roxo simplificado (faixa no topo)

## Fluxo de Autenticação

```
┌─────────────────┐
│  Acessa /       │
└────────┬────────┘
         │
    ┌────▼────┐
    │Autenticade?│
    └─┬───────┬─┘
      │       │
     SIM     NÃO
      │       │
      │    ┌──▼──────────┐
      │    │Landing Page │
      │    └─────────────┘
      │
   ┌──▼──────────┐
   │Redirect     │
   │para /feed   │
   └──┬──────────┘
      │
   ┌──▼──────────┐
   │  FEED       │
   │  ✓ Posts    │
   │  ✓ Amigues  │
   │  ✓ Jogo     │
   └─────────────┘
```

## Proteção de Rotas

A rota `/feed` é protegida por `@login_required`:
- Usuáries não autenticades são redirecionados para `/login?next=%2Ffeed`
- Após login bem-sucedido, são redirecionados de volta para `/feed`
- A página raiz `/` redireciona automaticamente usuáries autenticades para `/feed`

## Recursos do Feed

### Postagens
- Feed dinâmico carregado via API (`/api/posts`)
- Suporta imagens (até 4 por post)
- Suporta menções (@usuarie) e hashtags (#tag)
- Autocomplete para menções e hashtags
- Moderação de conteúdo

### Amigues
- Lista carregada via API (`/api/amigues`)
- Mostra usuáries com seguimento mútuo
- Fotos de perfil clicáveis (levam ao perfil)
- Limite de 12 amigues visíveis (+ contador se houver mais)

### Jogo da Velha
- Implementado em JavaScript puro
- Jogador humano é sempre X
- IA (Robo) joga como O
- Lógica de vitória e empate
- Botão de reiniciar

### Notificações
- Carregadas via API (`/api/notifications`)
- Atualização a cada 2 minutos
- Badge com contador
- Persist`ncia de estado (localStorage)

## Troubleshooting

### Problema: "Não consigo acessar o feed"
**Solução:** Verifique se você está autenticade. O feed requer login.

### Problema: "Sou redirecionado para /login"
**Solução:** Isso é esperado. Faça login e você será redirecionado para o feed.

### Problema: "Feed aparece vazio"
**Solução:** 
1. Abra o console do navegador (F12)
2. Verifique se há erros de JavaScript
3. Verifique se a API `/api/posts` está retornando dados
4. Tente criar um post em `/novo_post`

### Problema: "Amigues não aparecem"
**Solução:**
1. Você precisa seguir outros usuáries primeiro
2. Eles precisam te seguir de volta (seguimento mútuo)
3. API: `/api/amigues` retorna apenas seguimento mútuo

### Problema: "Jogo da velha não funciona"
**Solução:**
1. Verifique se JavaScript está habilitado
2. Verifique o console por erros
3. Experimente reiniciar o jogo com o botão "Reiniciar"

## Validação de Funcionalidades

Todos os recursos foram testados e validados:

```
✓ Template feed.html existe e carrega
✓ Rota /feed está configurada
✓ @login_required protege a rota
✓ Posts section (#feed-list) presente
✓ Friends section (amigues) presente
✓ Tic-tac-toe game (jogo da velha) presente
✓ Search functionality presente
✓ Post creation presente
✓ Database tables criadas (user, post, post_likes)
✓ Redirect flow funciona (/ -> /feed quando autenticade)
✓ Login redirect funciona (/feed -> /login quando não autenticade)
```

## Arquivos Relacionados

- **Template:** `gramatike_app/templates/feed.html`
- **Rotas:** `gramatike_app/routes/__init__.py` (linhas 819-834)
- **Models:** `gramatike_app/models.py`
- **JavaScript:** Inline em `feed.html` (linhas 694-1852)
- **Estilos:** Inline em `feed.html` + `static/style.css` + `static/gramatike_common.css`

## Conclusão

O feed está **100% funcional** com todos os recursos solicitados:
- ✅ Postagens
- ✅ Amigues (sidebar)
- ✅ Jogo da Velha

Para acessar, basta:
1. Criar uma conta em `/cadastro`
2. Fazer login em `/login`
3. Ser automaticamente redirecionade para `/feed`

Ou, se já tiver conta, apenas fazer login que o redirect é automático.
