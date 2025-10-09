# ✅ Checklist de Testes - Layout Mobile

## 🧪 Testes de Responsividade

### Desktop (> 980px)
- [ ] Sidebar visível à direita
- [ ] Feed em 2 colunas (feed + sidebar)
- [ ] Barra de navegação inferior **não visível**
- [ ] Notificações funcionam na sidebar
- [ ] Todos os cards da sidebar aparecem

### Tablet (768px - 980px)
- [ ] Sidebar **oculta**
- [ ] Feed ocupa largura total
- [ ] Barra de navegação inferior **visível**
- [ ] Navegação inferior tem 5 itens

### Mobile (< 768px)
- [ ] Sidebar **oculta**
- [ ] Feed em largura total
- [ ] Barra de navegação inferior **visível e fixa**
- [ ] Posts aparecem corretamente
- [ ] Sem scroll horizontal

## 🔔 Testes de Funcionalidade

### Barra de Navegação Inferior
- [ ] Ícone "Início" redireciona para feed
- [ ] Ícone "Educação" abre página educação
- [ ] Botão "+" (roxo) abre página criar post
- [ ] Ícone "Notificações" abre painel de notificações
- [ ] Ícone "Perfil" abre perfil do usuário
- [ ] Para usuário não autenticado, mostra "Entrar"

### Notificações
- [ ] Badge aparece na sidebar (desktop)
- [ ] Badge aparece na barra inferior (mobile)
- [ ] Badges sincronizados (mesmo número)
- [ ] Badge desaparece ao abrir notificações
- [ ] Badge reaparece com novas notificações

### Layout e Espaçamento
- [ ] Footer não sobrepõe barra inferior mobile
- [ ] Espaço adequado entre conteúdo e barra inferior
- [ ] Safe area (notch) respeitado em iPhones
- [ ] Scroll funciona corretamente
- [ ] Nenhum elemento cortado ou escondido

## 📱 Testes por Dispositivo

### iPhone SE (375px)
- [ ] Layout mobile correto
- [ ] Barra inferior visível
- [ ] Todos os ícones acessíveis
- [ ] Texto legível

### iPhone 12/13 (390px)
- [ ] Layout mobile correto
- [ ] Safe area respeitado
- [ ] Barra inferior não sobreposta

### iPad (768px)
- [ ] Transição correta para mobile
- [ ] Barra inferior aparece
- [ ] Layout adequado

### iPad Pro (1024px)
- [ ] Sidebar visível (desktop mode)
- [ ] Sem barra inferior
- [ ] Layout desktop correto

## 🎨 Testes Visuais

- [ ] Ícones renderizam corretamente
- [ ] Cores consistentes com tema
- [ ] Botão "+" destacado em roxo
- [ ] Transições suaves
- [ ] Hover states funcionam
- [ ] Active states (ao clicar) funcionam

## ⚡ Testes de Performance

- [ ] Página carrega rápido
- [ ] Sem erros no console
- [ ] Nenhum warning de CSS
- [ ] JavaScript sem erros
- [ ] Imagens carregam corretamente

## 🔐 Testes de Segurança

- [ ] CSRF tokens presentes em forms
- [ ] Links seguros (https onde aplicável)
- [ ] Sem dados sensíveis expostos

## ♿ Testes de Acessibilidade

- [ ] Labels ARIA presentes nos ícones
- [ ] Navegação por teclado funciona
- [ ] Títulos descritivos nos links
- [ ] Contraste adequado
- [ ] Texto alternativo em imagens/ícones

## 🌐 Testes Cross-Browser

### Chrome/Edge
- [ ] Layout mobile correto
- [ ] Barra inferior funciona
- [ ] Notificações sincronizadas

### Safari (iOS)
- [ ] Safe area respeitado
- [ ] Barra inferior não esconde
- [ ] Scroll funciona

### Firefox
- [ ] Layout responsivo OK
- [ ] CSS Grid/Flexbox funciona
- [ ] JavaScript sem erros

## 📝 Notas de Teste

### Breakpoints Implementados
- **1200px**: Ajuste de padding (24px)
- **980px**: Mudança principal (oculta sidebar, exibe bottom nav)
- **860px**: Flex direction column
- **640px**: Logo menor
- **420px**: Padding mínimo (12px)

### Elementos Chave
- `.right-col`: Sidebar (oculta < 980px)
- `.mobile-bottom-nav`: Barra inferior (visível < 980px)
- `#mobile-notifications-badge`: Badge sincronizado
- Safe area: `env(safe-area-inset-bottom)`

## ✨ Resultado Esperado

✅ **Desktop**: Sidebar visível, sem bottom nav  
✅ **Mobile**: Sidebar oculta, bottom nav visível e funcional  
✅ **Notificações**: Sincronizadas entre desktop e mobile  
✅ **UX**: Experiência tipo app de rede social em mobile  
