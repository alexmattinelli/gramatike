# Centralização do Logo "Gramátike"

## Problema
O nome "Gramátike" na barra de navegação estava alinhado à esquerda devido ao uso de `justify-content: space-between` no CSS do elemento `nav`.

## Solução Implementada

### Alteração CSS
Mudança simples e precisa na propriedade de alinhamento do flexbox:

**Antes:**
```css
nav {
  display: flex;
  align-items: center;
  justify-content: space-between;  /* Alinha à esquerda */
  padding: 0 28px;
}
```

**Depois:**
```css
nav {
  display: flex;
  align-items: center;
  justify-content: center;  /* Centraliza horizontalmente */
  padding: 0 28px;
}
```

### Arquivos Modificados

Todos os 6 arquivos HTML com navegação foram atualizados:

1. ✅ `public/feed.html`
2. ✅ `public/post.html`
3. ✅ `public/meu_perfil.html`
4. ✅ `public/perfil.html`
5. ✅ `public/configuracoes.html`
6. ✅ `public/suporte.html`

## Resultado Visual

### Feed Page
O logo "Gramátike" agora aparece centralizado no topo da página:

![Logo centralizado - Feed](https://github.com/user-attachments/assets/5c54b5ad-0649-4d79-9f36-ef52da41594e)

### Configurações Page
Mesmo comportamento em todas as páginas:

![Logo centralizado - Configurações](https://github.com/user-attachments/assets/3bf0d0f0-dadc-4525-9e71-1ff2b440321d)

## Características da Alteração

- ✅ **Minimalista**: Apenas 1 propriedade CSS alterada por arquivo
- ✅ **Consistente**: Aplicada em todas as páginas
- ✅ **Responsiva**: Mantém o comportamento responsivo existente
- ✅ **Sem breaking changes**: Não afeta outras funcionalidades

## Compatibilidade

A alteração é totalmente compatível com:
- Desktop (todas as resoluções)
- Tablet (768px - 992px)
- Mobile (< 768px)
- Mobile Small (< 576px)
- Extra Small Mobile (< 400px)

Todas as media queries existentes foram preservadas.

## Deploy

Nenhuma configuração adicional necessária. A alteração é puramente visual (CSS) e será aplicada automaticamente após o merge.
