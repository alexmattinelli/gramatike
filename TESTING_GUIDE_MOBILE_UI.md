# 🧪 Guia de Testes - Mobile UI Improvements

## 📱 Como Testar as Mudanças Mobile

Este guia detalha como testar **TODAS** as melhorias mobile implementadas.

---

## 🛠️ Preparação

### Opção 1: DevTools (Recomendado)
1. Abrir Chrome/Firefox DevTools (F12)
2. Clicar no ícone de dispositivo mobile (Ctrl+Shift+M)
3. Selecionar tamanho: `375x667` (iPhone SE) ou `360x740` (Galaxy S9)
4. Recarregar a página

### Opção 2: Navegador Mobile Real
1. Acessar pelo celular/tablet
2. Garantir que está em modo portrait
3. Testar em diferentes tamanhos

---

## 1️⃣ INDEX.HTML - Feed de Posts

### ✅ Teste: Cards Mais Largos

**Passos:**
1. Abrir `/` (página inicial) em mobile (< 980px)
2. Verificar cards de posts

**Esperado:**
- ✅ Cards devem ir quase até as bordas da tela
- ✅ Margem lateral mínima (aproximadamente 8-10px de cada lado)
- ✅ Cards visualmente "enlarguecidos" comparado com antes

**Como verificar:**
```javascript
// No console do DevTools
const post = document.querySelector('#feed-list article.post');
const margin = window.getComputedStyle(post).marginLeft;
console.log('Margem lateral:', margin); // Deve ser negativa (-0.8rem)
```

---

### ✅ Teste: Conteúdo Maior

**Passos:**
1. Ler o texto de um post
2. Verificar tamanho da fonte

**Esperado:**
- ✅ Texto do post em tamanho `1.15rem` (18.4px se base 16px)
- ✅ Linha mais espaçada (line-height: 1.6)
- ✅ Fácil de ler sem dar zoom

**Como verificar:**
```javascript
// No console
const content = document.querySelector('.post-content');
const fontSize = window.getComputedStyle(content).fontSize;
const lineHeight = window.getComputedStyle(content).lineHeight;
console.log('Font:', fontSize, 'Line-height:', lineHeight);
// Deve ser: 18.4px / 1.6
```

---

### ✅ Teste: Botões Maiores

**Passos:**
1. Observar botões "Curtir", "Comentar", "Compartilhar"
2. Tentar clicar

**Esperado:**
- ✅ Botões visivelmente maiores
- ✅ Fácil de clicar com o dedo
- ✅ Texto dos botões legível (.85rem)

**Como verificar:**
```javascript
// No console
const btn = document.querySelector('.post-actions button');
const padding = window.getComputedStyle(btn).padding;
const fontSize = window.getComputedStyle(btn).fontSize;
console.log('Padding:', padding, 'Font:', fontSize);
// Deve ter padding maior e font ~13.6px
```

---

### ✅ Teste: Card de Ações Rápidas

**Passos:**
1. Observar card com botões de ação rápida (topo do feed)
2. Verificar largura

**Esperado:**
- ✅ Card com **mesma largura** dos posts
- ✅ Vai até as bordas (margem -0.8rem)
- ✅ Botões 52×52px (maiores que antes)

**Como verificar:**
```javascript
// No console
const actionCard = document.getElementById('mobile-actions-card');
const margin = window.getComputedStyle(actionCard).marginLeft;
const btn = actionCard.querySelector('.search-btn.icon-btn');
const width = window.getComputedStyle(btn).width;
console.log('Margin:', margin, 'Button width:', width);
// Margin deve ser negativa, button ~52px
```

---

## 2️⃣ ARTIGOS.HTML - Menu Dropdown

### ✅ Teste: Navegação Escondida

**Passos:**
1. Abrir `/artigos` em mobile (< 980px)
2. Procurar botões "Início", "Apostilas", "Exercícios", "Artigos"

**Esperado:**
- ✅ Botões **NÃO** devem aparecer no mobile
- ✅ Apenas o botão "Menu" no topo direito

**Como verificar:**
```javascript
// No console
const eduNav = document.querySelector('.edu-nav');
const display = window.getComputedStyle(eduNav).display;
console.log('edu-nav display:', display); // Deve ser 'none'
```

---

### ✅ Teste: Botão Menu

**Passos:**
1. Procurar botão no topo direito
2. Verificar texto e ícone

**Esperado (Mobile < 980px):**
- ✅ Texto: "Menu"
- ✅ Ícone: Hamburger (três linhas ☰)
- ✅ Cor: Branco em fundo semi-transparente

**Como verificar:**
```javascript
// No console
const menuText = document.getElementById('menu-text').textContent;
const menuIcon = document.getElementById('menu-icon');
const menuIconDisplay = window.getComputedStyle(menuIcon).display;
console.log('Text:', menuText, 'Icon display:', menuIconDisplay);
// Text: 'Menu', Icon: 'block'
```

---

### ✅ Teste: Dropdown

**Passos:**
1. Clicar no botão "Menu"
2. Verificar opções

**Esperado:**
- ✅ Dropdown abre abaixo do botão
- ✅ 6 opções visíveis:
  - 🏠 Início
  - 📄 Artigos
  - ❓ Exercícios
  - 📚 Apostilas
  - 🎲 Dinâmicas
  - 🔧 Painel
- ✅ Cada opção com ícone roxo
- ✅ Hover: fundo roxo claro

**Como testar:**
```javascript
// Abrir dropdown programaticamente
toggleMenu();

// Verificar se abriu
const dropdown = document.getElementById('menu-dropdown');
console.log('Dropdown visível:', dropdown.style.display === 'block');

// Contar opções
const links = dropdown.querySelectorAll('a');
console.log('Número de opções:', links.length); // Deve ser 6
```

---

### ✅ Teste: Fechar Dropdown

**Passos:**
1. Abrir dropdown
2. Clicar fora dele

**Esperado:**
- ✅ Dropdown fecha automaticamente

**Como verificar:**
```javascript
// Simular clique fora
document.body.click();

// Verificar se fechou
const dropdown = document.getElementById('menu-dropdown');
console.log('Dropdown fechou:', dropdown.style.display === 'none');
```

---

### ✅ Teste: Desktop

**Passos:**
1. Redimensionar para > 980px (desktop)
2. Observar botão

**Esperado:**
- ✅ Texto: "Painel"
- ✅ Ícone: Dashboard (4 quadrados 📊)
- ✅ Clicar: vai direto para `/admin/dashboard`
- ✅ Dropdown **não** abre

**Como verificar:**
```javascript
// Resize programaticamente
window.resizeTo(1200, 800);
updateMenuButton();

const menuText = document.getElementById('menu-text').textContent;
const painelIcon = document.getElementById('painel-icon');
const painelIconDisplay = window.getComputedStyle(painelIcon).display;
console.log('Text:', menuText, 'Icon display:', painelIconDisplay);
// Text: 'Painel', Icon: 'block'
```

---

## 3️⃣ APOSTILAS.HTML - Menu Dropdown

### ✅ Testes: **IDÊNTICOS** ao Artigos.html

1. ✅ Navegação escondida no mobile
2. ✅ Botão "Menu" com dropdown
3. ✅ 6 opções no dropdown
4. ✅ Fecha ao clicar fora
5. ✅ Desktop: botão "Painel" direto

---

## 4️⃣ EXERCICIOS.HTML - Menu Dropdown

### ✅ Testes: **IDÊNTICOS** ao Artigos.html

1. ✅ Navegação escondida no mobile
2. ✅ Botão "Menu" com dropdown
3. ✅ 6 opções no dropdown
4. ✅ Fecha ao clicar fora
5. ✅ Desktop: botão "Painel" direto

---

## 5️⃣ MEU_PERFIL.HTML - Barra de Navegação

### ✅ Teste: Barra Inferior Visível

**Passos:**
1. Abrir `/perfil` em mobile (< 980px)
2. Scrollar até o final da página

**Esperado:**
- ✅ Barra fixa na parte inferior
- ✅ Sempre visível (mesmo com scroll)
- ✅ Background branco
- ✅ Border top cinza
- ✅ Shadow para cima

**Como verificar:**
```javascript
// No console
const nav = document.querySelector('.mobile-bottom-nav');
const display = window.getComputedStyle(nav).display;
const position = window.getComputedStyle(nav).position;
console.log('Display:', display, 'Position:', position);
// Display: 'flex', Position: 'fixed'
```

---

### ✅ Teste: 5 Itens de Navegação

**Passos:**
1. Contar itens na barra inferior
2. Verificar cada um

**Esperado:**
- ✅ **5 itens** no total:
  1. 🏠 Início (cinza)
  2. 📚 Educação (cinza)
  3. **[+]** Criar post (circular roxo)
  4. ⏰ Em breve (cinza, não clicável)
  5. 👤 Perfil (roxo - ativo)

**Como verificar:**
```javascript
// Contar links e divs
const nav = document.querySelector('.mobile-bottom-nav');
const items = nav.querySelectorAll('a, div');
console.log('Total de itens:', items.length); // Deve ser 5

// Verificar item ativo (Perfil)
const profileLink = nav.querySelector('a[href*="meu_perfil"]');
const color = window.getComputedStyle(profileLink).color;
console.log('Cor do Perfil:', color); // Deve ser roxo
```

---

### ✅ Teste: Botão Criar Post

**Passos:**
1. Observar botão central (+)
2. Clicar nele

**Esperado:**
- ✅ Botão circular
- ✅ Background roxo
- ✅ Ícone + branco
- ✅ Tamanho: 48×48px
- ✅ Posição: levemente para cima (margin: -10px 0)
- ✅ Clicar: vai para `/novo_post`

**Como verificar:**
```javascript
// No console
const createBtn = document.querySelector('a[href*="novo_post"]');
const borderRadius = window.getComputedStyle(createBtn).borderRadius;
const width = window.getComputedStyle(createBtn).width;
console.log('Border radius:', borderRadius, 'Width:', width);
// Border radius: 50%, Width: 48px
```

---

### ✅ Teste: Desktop

**Passos:**
1. Redimensionar para > 980px
2. Procurar barra inferior

**Esperado:**
- ✅ Barra **NÃO** aparece
- ✅ Footer normal visível

**Como verificar:**
```javascript
// No console (desktop)
const nav = document.querySelector('.mobile-bottom-nav');
const display = window.getComputedStyle(nav).display;
console.log('Barra mobile display:', display); // Deve ser 'none'
```

---

## 6️⃣ PERFIL.HTML (Outro usuário)

### ✅ Status: Sem mudanças

**Teste:**
1. Abrir `/perfil/<id>` de outro usuário
2. Verificar barra inferior

**Esperado:**
- ✅ Já tinha barra inferior (sem mudanças)
- ✅ Item "Perfil" **NÃO** está destacado (não é meu perfil)

---

## 🎯 Teste Completo - Fluxo de Navegação

### Cenário: Navegação Mobile Completa

**Passos:**
1. 📱 Abrir `/` (index) em mobile
2. ✅ Verificar cards largos e conteúdo grande
3. 👆 Clicar em "Educação" (barra inferior)
4. ✅ Verificar página educação carregou
5. 👆 Clicar em "Menu" (topo direito)
6. ✅ Verificar dropdown abriu com 6 opções
7. 👆 Clicar em "Artigos"
8. ✅ Verificar página artigos carregou
9. 👆 Clicar em "Perfil" (barra inferior)
10. ✅ Verificar página perfil carregou
11. ✅ Verificar item "Perfil" está destacado (roxo)

**Esperado:**
- ✅ Navegação fluida sem problemas
- ✅ Todas as páginas com navegação consistente
- ✅ Menu dropdown funciona em Artigos/Apostilas/Exercícios
- ✅ Barra inferior presente em todas as páginas

---

## 🐛 Problemas Comuns

### Problema 1: Cards não estão largos
**Causa**: Media query não aplicada  
**Solução**: Verificar viewport width < 980px

### Problema 2: Navegação inline aparece no mobile
**Causa**: CSS `.edu-nav { display:none }` não aplicado  
**Solução**: Limpar cache do navegador

### Problema 3: Dropdown não abre
**Causa**: JavaScript não carregou  
**Solução**: Verificar console por erros

### Problema 4: Barra inferior não aparece
**Causa**: CSS não aplicado ou viewport > 980px  
**Solução**: Verificar media query e viewport

---

## 📊 Checklist Final

### Mobile (< 980px)

#### Index
- [ ] Cards largos (margem -0.8rem) ✅
- [ ] Conteúdo 1.15rem ✅
- [ ] Botões ação .5rem .95rem ✅
- [ ] Card ações mesma largura ✅
- [ ] Botões ação 52×52px ✅

#### Artigos
- [ ] Nav inline escondida ✅
- [ ] Botão "Menu" visível ✅
- [ ] Dropdown abre ✅
- [ ] 6 opções no dropdown ✅
- [ ] Fecha ao clicar fora ✅

#### Apostilas
- [ ] Nav inline escondida ✅
- [ ] Menu dropdown funcional ✅

#### Exercícios
- [ ] Nav inline escondida ✅
- [ ] Menu dropdown funcional ✅

#### Meu Perfil
- [ ] Barra inferior visível ✅
- [ ] 5 itens na barra ✅
- [ ] Item Perfil destacado ✅
- [ ] Botão + circular roxo ✅

### Desktop (≥ 980px)

#### Artigos/Apostilas/Exercícios
- [ ] Nav inline visível ✅
- [ ] Botão "Painel" (não Menu) ✅
- [ ] Clicar vai para dashboard ✅

#### Meu Perfil
- [ ] Barra inferior escondida ✅
- [ ] Footer visível ✅

---

## ✅ Resultado Esperado

Após todos os testes:
- ✅ 100% das páginas com navegação mobile
- ✅ 100% dos cards enlarguecidos corretamente
- ✅ 100% do conteúdo legível e clicável
- ✅ 100% da navegação consistente
- ✅ Experiência mobile profissional! 🎉

---

**Status**: ✅ Pronto para teste  
**Data**: Outubro 2025  
**Última atualização**: Hoje
