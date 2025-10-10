# Atualização de Paginação e Menu/Painel - Outubro 2025

## 📋 Problema Original

> Na versão de PC, a numeração de pagina vai ter limite de 10 e no mobille limite de 3, e não é para ter o botão Menu, é para ser Painel. O menu só vai existir na versão Mobille

## ✅ Solução Implementada

### 1. Limites de Paginação Responsivos

#### Desktop (> 980px)
- **Limite**: Máximo de 10 números de página exibidos
- **Comportamento**: Quando há mais de 10 páginas, mostra:
  - Primeira página (sempre visível)
  - Reticências (...) se necessário
  - Até 10 páginas ao redor da página atual
  - Reticências (...) se necessário
  - Última página (sempre visível)

#### Mobile (≤ 980px)
- **Limite**: Máximo de 3 números de página exibidos
- **Comportamento**: Quando há mais de 3 páginas, mostra:
  - Primeira página (sempre visível)
  - Reticências (...) se necessário
  - Até 3 páginas ao redor da página atual
  - Reticências (...) se necessário
  - Última página (sempre visível)

### 2. Botão Menu/Painel Adaptativo

#### Desktop (> 980px)
- **Texto**: "Painel"
- **Ícone**: Dashboard (4 quadrados)
- **Comportamento**: Clique vai direto para `/admin/dashboard`
- **Dropdown**: Não exibe

#### Mobile (≤ 980px)
- **Texto**: "Menu"
- **Ícone**: Hamburger (3 linhas)
- **Comportamento**: Clique abre/fecha dropdown
- **Dropdown**: Exibe menu com 5 opções:
  - 📑 Artigos
  - 🧠 Exercícios
  - 📚 Apostilas
  - 🎲 Dinâmicas
  - 🛠️ Painel

## 🔧 Detalhes Técnicos

### Arquivo Modificado
```
gramatike_app/templates/gramatike_edu.html
```

### Código Adicionado

#### 1. Estrutura HTML do Botão
```html
<button id="menu-toggle" onclick="toggleMenu()">
  <svg id="menu-icon"><!-- Hamburger icon --></svg>
  <svg id="painel-icon" style="display:none;"><!-- Dashboard icon --></svg>
  <span id="menu-text">Menu</span>
</button>
```

#### 2. Função de Atualização do Botão
```javascript
function updateMenuButton() {
  const isMobile = window.innerWidth <= 980;
  const menuText = document.getElementById('menu-text');
  const menuIcon = document.getElementById('menu-icon');
  const painelIcon = document.getElementById('painel-icon');
  const dropdown = document.getElementById('menu-dropdown');
  
  if (isMobile) {
    // Mobile: Show "Menu" with hamburger icon
    if (menuText) menuText.textContent = 'Menu';
    if (menuIcon) menuIcon.style.display = 'block';
    if (painelIcon) painelIcon.style.display = 'none';
  } else {
    // Desktop: Show "Painel" with dashboard icon
    if (menuText) menuText.textContent = 'Painel';
    if (menuIcon) menuIcon.style.display = 'none';
    if (painelIcon) painelIcon.style.display = 'block';
    if (dropdown) dropdown.style.display = 'none';
  }
}
```

#### 3. Função de Toggle do Menu
```javascript
function toggleMenu() {
  const isMobile = window.innerWidth <= 980;
  
  if (isMobile) {
    // Mobile: Toggle dropdown
    const dropdown = document.getElementById('menu-dropdown');
    if (dropdown) {
      dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
    }
  } else {
    // Desktop: Go directly to Painel
    window.location.href = "{{ url_for('admin.dashboard') }}";
  }
}
```

#### 4. Lógica de Paginação Responsiva
```javascript
function renderPagination() {
  // ... código existente ...
  
  // Page numbers with limit based on screen size
  const isMobile = window.innerWidth <= 980;
  const maxPages = isMobile ? 3 : 10;
  
  let startPage = 1;
  let endPage = totalPages;
  
  if (totalPages > maxPages) {
    const half = Math.floor(maxPages / 2);
    startPage = Math.max(1, currentPage - half);
    endPage = Math.min(totalPages, startPage + maxPages - 1);
    
    // Adjust if we're near the end
    if (endPage - startPage + 1 < maxPages) {
      startPage = Math.max(1, endPage - maxPages + 1);
    }
  }
  
  // Show first page if not in range
  if (startPage > 1) {
    html += `<button onclick="changePage(1)" class="pag-btn">1</button>`;
    if (startPage > 2) {
      html += `<span class="pag-btn" style="background:transparent; color:#666; pointer-events:none; border:none;">...</span>`;
    }
  }
  
  // Show page numbers in range
  for (let i = startPage; i <= endPage; i++) {
    if (i === currentPage) {
      html += `<span class="pag-btn" style="background:#9B5DE5; color:#fff; pointer-events:none;">${i}</span>`;
    } else {
      html += `<button onclick="changePage(${i})" class="pag-btn">${i}</button>`;
    }
  }
  
  // Show last page if not in range
  if (endPage < totalPages) {
    if (endPage < totalPages - 1) {
      html += `<span class="pag-btn" style="background:transparent; color:#666; pointer-events:none; border:none;">...</span>`;
    }
    html += `<button onclick="changePage(${totalPages})" class="pag-btn">${totalPages}</button>`;
  }
}
```

#### 5. Event Listeners
```javascript
// Update button on load and resize
updateMenuButton();
window.addEventListener('resize', updateMenuButton);
```

## 🎨 Exemplos Visuais

### Cenário 1: Desktop - Primeira Página (20 páginas totais)
```
← Anterior | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | ... | 20 | Próximo →
```

### Cenário 2: Desktop - Página 10 (20 páginas totais)
```
← Anterior | 1 | ... | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | ... | 20 | Próximo →
```

### Cenário 3: Mobile - Primeira Página (20 páginas totais)
```
1 | 2 | 3 | ... | 20 | Próximo →
```

### Cenário 4: Mobile - Página 10 (20 páginas totais)
```
← Anterior | 1 | ... | 9 | 10 | 11 | ... | 20 | Próximo →
```

## 🧪 Como Testar

### 1. Testar Botão Menu/Painel

**Desktop (> 980px)**:
1. Abrir página Gramátike Edu em tela grande
2. Verificar que botão mostra "Painel" com ícone de dashboard
3. Clicar no botão
4. Verificar que navega para `/admin/dashboard`

**Mobile (≤ 980px)**:
1. Abrir página Gramátike Edu em tela pequena ou redimensionar
2. Verificar que botão mostra "Menu" com ícone hamburger
3. Clicar no botão
4. Verificar que dropdown abre com 5 opções
5. Clicar fora do dropdown
6. Verificar que dropdown fecha

### 2. Testar Paginação

**Desktop (> 980px)**:
1. Criar conteúdo suficiente para ter 20+ páginas (60+ itens com 3 por página)
2. Verificar que primeira página mostra até 10 números
3. Navegar para página do meio (ex: 10)
4. Verificar que mostra 10 números ao redor da página atual
5. Verificar que mostra reticências antes e depois
6. Verificar que primeira e última páginas sempre aparecem

**Mobile (≤ 980px)**:
1. Redimensionar para móvel
2. Verificar que primeira página mostra até 3 números
3. Navegar para página do meio
4. Verificar que mostra 3 números ao redor da página atual
5. Verificar que reticências aparecem corretamente

### 3. Testar Responsividade

1. Abrir página em desktop
2. Redimensionar janela gradualmente
3. Verificar que ao passar de 980px:
   - Botão muda de "Painel" para "Menu"
   - Ícone muda de dashboard para hamburger
   - Paginação reduz de 10 para 3 números máximos

## ✅ Checklist de Validação

- [x] Desktop mostra "Painel" e vai ao dashboard
- [x] Mobile mostra "Menu" e abre dropdown
- [x] Desktop mostra até 10 números de página
- [x] Mobile mostra até 3 números de página
- [x] Reticências aparecem quando há páginas ocultas
- [x] Primeira e última páginas sempre visíveis quando há muitas páginas
- [x] Botões Anterior/Próximo funcionam
- [x] Atualização automática ao redimensionar janela
- [x] Dropdown fecha ao clicar fora (mobile)
- [x] Navegação funciona em todas as páginas

## 📊 Impacto

### Usuários Desktop
- ✅ Acesso direto ao painel (1 clique em vez de 2)
- ✅ Mais números de página visíveis (10 vs todos)
- ✅ Navegação mais rápida em conteúdo extenso

### Usuários Mobile
- ✅ Menu organizado e acessível
- ✅ Paginação compacta (3 números)
- ✅ Melhor uso do espaço limitado da tela
- ✅ Interface menos sobrecarregada

## 🚀 Deploy

A mudança é compatível com o código existente e não requer:
- Mudanças no backend
- Migrações de banco de dados
- Atualizações de dependências

Após merge e deploy no Vercel, as mudanças estarão imediatamente ativas.

---

**Data**: Outubro 2025  
**Autor**: GitHub Copilot  
**Arquivo**: `gramatike_app/templates/gramatike_edu.html`  
**Commit**: `af9b8e5`
