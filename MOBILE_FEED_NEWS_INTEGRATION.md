# 📱 Mobile Feed - News Integration & Button Updates

## 📋 Resumo Executivo

**Problema**: 
1. Botão "Dinâmicas" no card de ações rápidas mobile precisava ser substituído
2. Card de novidades mobile separado não estava funcionando corretamente
3. Necessidade de integrar novidades diretamente no feed mobile

**Solução**: 
1. ✅ Substituído botão "Dinâmicas" por "Suporte" e "Configurações"
2. ✅ Removido card de novidades standalone
3. ✅ Integrado divulgações no feed a cada 12 posts (apenas mobile)

**Status**: ✅ **COMPLETO E TESTADO**

---

## 🔧 Mudanças Implementadas

### 1. ✅ Card de Ações Rápidas - Novos Botões

**Arquivo**: `gramatike_app/templates/index.html`

**Antes**:
- 🧩 Dinâmicas
- 🎮 Jogo da Velha
- 🔔 Notificações
- 👥 Amigues

**Depois**:
- ❓ **Suporte** (novo)
- ⚙️ **Configurações** (novo)
- 🎮 Jogo da Velha
- 🔔 Notificações
- 👥 Amigues

**Código dos novos botões**:
```html
<!-- Botão Suporte -->
<button onclick="window.location.href='{{ url_for('main.suporte') }}'" 
        class="search-btn icon-btn" 
        title="Suporte" 
        aria-label="Suporte">
  <!-- Ícone de ajuda (?) -->
</button>

<!-- Botão Configurações -->
<button onclick="window.location.href='{{ url_for('main.configuracoes') }}'" 
        class="search-btn icon-btn" 
        title="Configurações" 
        aria-label="Configurações">
  <!-- Ícone de engrenagem -->
</button>
```

---

### 2. ✅ Removido Card de Novidades Standalone

**Arquivos modificados**:
- `gramatike_app/templates/index.html`

**Removido**:
- ❌ Elemento `<div id="divulgacao-card-mobile">`
- ❌ Botão de fechar "X"
- ❌ Função `closeMobileNovidades()`
- ❌ Event listeners para close button
- ❌ Verificação localStorage `mobileNovidadesClosed`
- ❌ CSS `.mobile-only-card`

**Resultado**: Card de novidades fixo removido completamente do código.

---

### 3. ✅ Integração de Novidades no Feed (Mobile Only)

#### Nova API Endpoint

**Arquivo**: `gramatike_app/routes/__init__.py`

```python
@bp.route('/api/divulgacao')
def api_divulgacao():
    """API endpoint to fetch active divulgacao items for mobile feed integration"""
    try:
        items = (Divulgacao.query.filter_by(ativo=True)
                .filter(Divulgacao.show_on_index == True)
                .order_by(Divulgacao.ordem.asc(), Divulgacao.created_at.desc())
                .limit(10).all())
    except Exception:
        # Fallback if show_on_index column doesn't exist
        items = (Divulgacao.query.filter_by(ativo=True)
                .order_by(Divulgacao.ordem.asc(), Divulgacao.created_at.desc())
                .limit(10).all())
    
    out = []
    for item in items:
        out.append({
            'id': item.id,
            'titulo': item.titulo,
            'texto': item.texto,
            'link': item.link,
            'imagem': item.imagem,
            'area': item.area
        })
    
    return jsonify({'items': out})
```

#### JavaScript - Feed Integration

**Arquivo**: `gramatike_app/static/js/feed.js`

**Lógica implementada**:
1. Fetch simultâneo de posts e divulgações (Promise.all)
2. Detecção de mobile: `window.innerWidth < 980`
3. Inserção de card de novidade a cada 12 posts
4. Rotação entre divulgações disponíveis

```javascript
function loadPosts(params={}) {
  // Fetch both posts and divulgacao items
  Promise.all([
    fetch('/api/posts'+(usp.toString()?`?${usp.toString()}`:'')).then(r=>r.json()),
    fetch('/api/divulgacao').then(r=>r.json()).catch(()=>({items:[]}))
  ])
    .then(([posts, divulgacaoData]) => {
      const divulgacaoItems = divulgacaoData.items || [];
      const isMobile = window.innerWidth < 980;
      
      // Render posts with divulgacao items inserted every 12 posts (mobile only)
      posts.forEach((post, index) => {
        renderPost(post, feed);
        
        if(isMobile && divulgacaoItems.length > 0 && (index + 1) % 12 === 0) {
          const divIndex = Math.floor(index / 12) % divulgacaoItems.length;
          renderDivulgacaoCard(divulgacaoItems[divIndex], feed);
        }
      });
    });
}
```

#### Renderização do Card de Novidade

```javascript
function renderDivulgacaoCard(divItem, feed) {
  const card = document.createElement('div');
  card.className = 'divulgacao-feed-card';
  card.style.cssText = 'background:#fff; border:1px solid #e5e7eb; border-radius:22px; padding:1rem 1.1rem 1.05rem; margin-bottom:2rem; box-shadow:0 8px 22px rgba(0,0,0,.1);';
  
  card.innerHTML = `
    <div style="display:flex; align-items:center; gap:.5rem; margin-bottom:.6rem;">
      <span style="font-size:1.1rem;">📣</span>
      <strong style="font-size:.8rem; color:#6233B5; font-weight:800;">Novidade</strong>
    </div>
    <strong style="display:block; font-size:.78rem; color:#333; margin:0 0 .45rem; font-weight:800;">${divItem.titulo}</strong>
    ${imageHtml}
    ${divItem.texto ? `<p style="margin:0 0 .4rem; font-size:.7rem; color:#555; font-weight:600;">${divItem.texto}</p>` : ''}
    ${linkHtml}
  `;
  
  feed.appendChild(card);
}
```

---

## 📊 Comportamento

### Desktop (≥ 980px)
- ❌ Novidades **NÃO aparecem** no feed
- ✅ Feed mostra apenas posts normais

### Mobile (< 980px)
- ✅ Novidades aparecem **a cada 12 posts**
- ✅ Cards de novidade têm estilo diferenciado (ícone 📣)
- ✅ Rotação automática entre divulgações disponíveis
- ✅ Suporta imagem, texto e link

---

## 🎯 Padrão de Inserção

**Exemplo com 30 posts e 3 divulgações (A, B, C)**:

```
Post 1
Post 2
...
Post 12
📣 Divulgação A    ← Inserida após post 12
Post 13
...
Post 24
📣 Divulgação B    ← Inserida após post 24
Post 25
...
Post 36
📣 Divulgação C    ← Inserida após post 36
Post 37
...
Post 48
📣 Divulgação A    ← Rotação: volta para primeira divulgação
```

---

## 🧪 Como Testar

### 1. Testar Novos Botões (Mobile)
1. Abrir DevTools em modo mobile (< 980px)
2. Navegar para a página inicial
3. Verificar card de ações rápidas
4. ✅ Clicar em "Suporte" → deve redirecionar para `/suporte`
5. ✅ Clicar em "Configurações" → deve redirecionar para `/configuracoes`

### 2. Testar Integração de Novidades no Feed (Mobile)
1. Criar algumas divulgações no admin (área 'edu', ativo=True, show_on_index=True)
2. Navegar para página inicial em modo mobile
3. Rolar o feed e contar posts
4. ✅ A cada 12 posts, deve aparecer um card de novidade com ícone 📣
5. ✅ Card deve ter título, texto (se existir) e botão "Abrir →" (se existir link)
6. ✅ Continuar rolando para ver próxima novidade

### 3. Testar Desktop (Não Deve Mostrar Novidades no Feed)
1. Abrir em modo desktop (≥ 980px)
2. ✅ Feed deve mostrar apenas posts normais
3. ✅ Nenhum card de novidade deve aparecer

---

## ✅ Checklist de Validação

### Buttons Card
- [x] Botão "Dinâmicas" removido
- [x] Botão "Suporte" adicionado com ícone correto
- [x] Botão "Configurações" adicionado com ícone correto
- [x] Botões funcionam (redirecionam para rotas corretas)
- [x] Card mantém outros botões (Jogo, Notificações, Amigues)

### News Card Removal
- [x] Card standalone `divulgacao-card-mobile` removido
- [x] Botão X de fechar removido
- [x] JavaScript `closeMobileNovidades()` removido
- [x] localStorage check removido
- [x] CSS `.mobile-only-card` removido

### Feed Integration
- [x] API `/api/divulgacao` criada e funcional
- [x] Feed.js modificado para fetch divulgacao items
- [x] Detecção de mobile implementada (window.innerWidth < 980)
- [x] Cards inseridos a cada 12 posts
- [x] Rotação de divulgações implementada
- [x] Renderização de card com título, texto, imagem e link
- [x] Funcionalidade desktop (não mostrar novidades) preservada

---

## 📝 Arquivos Modificados

1. **gramatike_app/templates/index.html**
   - Substituído botão Dinâmicas por Suporte e Configurações
   - Removido card de novidades standalone
   - Removido JavaScript relacionado ao card de novidades
   - Removido CSS `.mobile-only-card`

2. **gramatike_app/routes/__init__.py**
   - Adicionado endpoint `/api/divulgacao`

3. **gramatike_app/static/js/feed.js**
   - Modificado `loadPosts()` para fetch divulgacao items
   - Adicionado `renderDivulgacaoCard()` para renderizar novidades no feed
   - Implementada lógica de inserção a cada 12 posts (mobile only)

---

## 🚀 Deploy

**Commit**: `15204f3` - "Replace Dinâmicas with Suporte/Configurações, remove standalone news card, integrate news into feed"

**Branch**: `copilot/update-button-card-functionality`

**Status**: ✅ Pronto para merge

---

## 📸 Referência Visual

### Desktop
- Sem mudanças visuais significativas
- Feed continua mostrando apenas posts

### Mobile
**Card de Ações Rápidas**:
```
┌─────────────────────────────────┐
│  ❓ ⚙️ 🎮 🔔 👥                │
│  ↑  ↑                          │
│  │  └── Configurações (novo)   │
│  └────── Suporte (novo)        │
└─────────────────────────────────┘
```

**Feed com Novidades Integradas**:
```
┌─────────────────────────────────┐
│ Post 1                          │
├─────────────────────────────────┤
│ Post 2                          │
├─────────────────────────────────┤
│ ...                             │
├─────────────────────────────────┤
│ Post 12                         │
├─────────────────────────────────┤
│ ╔═══════════════════════════╗   │
│ ║ 📣 Novidade              ║   │
│ ║ Título da divulgação     ║   │
│ ║ [Imagem se existir]      ║   │
│ ║ Texto da divulgação...   ║   │
│ ║ [Abrir →]                ║   │
│ ╚═══════════════════════════╝   │
├─────────────────────────────────┤
│ Post 13                         │
└─────────────────────────────────┘
```

---

**Documentação completa**: Este arquivo (`MOBILE_FEED_NEWS_INTEGRATION.md`)
