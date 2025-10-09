# 🔔 Correções de Notificações e Email - Gramátike

## Resumo das Correções

Este PR implementa correções para dois problemas reportados:

1. ✅ **Notificações reaparecem ao voltar para a página index**
2. ✅ **Símbolo roxo no email acima de "Gramátike"**

---

## 1. 🔔 Correção: Badge de Notificações Persistente

### Problema Original

Quando o usuário navegava para outra página e voltava para a página index, o badge de notificações (número de notificações) aparecia novamente, mesmo que o usuário já tivesse visualizado as notificações anteriormente.

### Solução Implementada

Implementado rastreamento de estado usando `localStorage` para persistir a visualização das notificações.

**Como funciona:**

1. **Quando o usuário abre as notificações:**
   - O sistema marca as notificações como vistas: `localStorage.setItem('notificationsViewed', 'true')`
   - Badge desaparece após 500ms

2. **Quando a página recarrega:**
   - Gera hash das notificações atuais
   - Compara com hash anterior
   - Se houver NOVAS notificações → badge reaparece
   - Se notificações são as mesmas E foram visualizadas → badge permanece oculto

**Arquivo modificado:** `gramatike_app/templates/index.html`

**Mudanças principais:**
- `toggleNotifications()`: Marca notificações como vistas no localStorage
- `loadNotifications()`: Verifica estado de visualização e hash de notificações

---

## 2. 📧 Correção: Logo Branco no Email

### Problema Original

No email, havia um símbolo roxo/escuro em cima de "Gramátike". O logo continha pixels que ficavam visíveis no fundo roxo do header.

### Solução Implementada

Aplicado filtro CSS `filter:brightness(0) invert(1)` para converter o logo em branco puro.

**Como funciona o filtro:**
1. `brightness(0)` - Transforma toda a imagem em preto
2. `invert(1)` - Inverte preto para branco
3. **Resultado:** Logo totalmente branco no fundo roxo

**Arquivo modificado:** `gramatike_app/utils/emailer.py`

**Mudança:** Linha 27 - Adicionado `filter:brightness(0) invert(1);` no style da img do logo

---

## 📊 Impacto

### Notificações
- ❌ **Antes:** Badge reaparecia em cada recarga de página
- ✅ **Depois:** Badge persiste como "visto" entre navegações

### Email
- ❌ **Antes:** Logo com pixels roxos confusos
- ✅ **Depois:** Logo limpo e branco no header roxo

---

## 🧪 Como Testar

### Teste de Notificações:
1. Abrir página index com notificações
2. Clicar no sino → badge some
3. Navegar para outra página e voltar
4. ✅ Verificar que badge NÃO reaparece

### Teste de Email:
1. Enviar email de teste: `python3 scripts/send_test_email.py seu@email.com`
2. ✅ Verificar que logo aparece branco no header roxo

---

## 📁 Arquivos Modificados

- `gramatike_app/templates/index.html` - Sistema de notificações com localStorage
- `gramatike_app/utils/emailer.py` - Filtro CSS para logo branco

**Total:** 2 arquivos, ~20 linhas modificadas
