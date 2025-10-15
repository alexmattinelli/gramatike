# Manual Testing Guide - Image Display Fix

## Objetivo
Verificar que as imagens agora aparecem **completas** (sem cortes) mantendo o formato 4x4 (1:1).

## Setup
1. Certifique-se de que a aplicação está rodando localmente ou em staging
2. Faça login com uma conta de teste
3. Prepare imagens de teste com diferentes proporções

## Imagens de Teste Recomendadas

### 1. Imagem Horizontal (16:9)
- **Exemplo**: Foto de paisagem, screenshot de vídeo
- **Dimensões sugeridas**: 1920x1080 ou 1600x900
- **Expectativa**: Imagem completa com barras cinza em cima/baixo

### 2. Imagem Vertical (9:16)
- **Exemplo**: Foto de celular em pé, story do Instagram
- **Dimensões sugeridas**: 1080x1920 ou 720x1280
- **Expectativa**: Imagem completa com barras cinza nas laterais

### 3. Imagem Quadrada (1:1)
- **Exemplo**: Foto do Instagram, avatar
- **Dimensões sugeridas**: 1000x1000 ou 800x800
- **Expectativa**: Imagem completa sem barras cinza

## Checklist de Testes

### Feed Principal (index.html)
- [ ] Criar post com imagem horizontal → verificar imagem completa
- [ ] Criar post com imagem vertical → verificar imagem completa
- [ ] Criar post com imagem quadrada → verificar sem distorção
- [ ] Criar post com 2 imagens → verificar grid 2 colunas com imagens completas
- [ ] Criar post com 3 imagens → verificar grid 3 colunas com imagens completas
- [ ] Criar post com 4+ imagens → verificar grid 2x2 com imagens completas

### Meu Perfil (meu_perfil.html)
- [ ] Acessar "Meu Perfil" → Aba "Postagens"
- [ ] Verificar posts com imagens horizontais
- [ ] Verificar posts com imagens verticais
- [ ] Verificar posts com múltiplas imagens
- [ ] Confirmar que todas as imagens aparecem completas

### Perfil de Outro Usuário (perfil.html)
- [ ] Acessar perfil de outro usuário
- [ ] Ir para aba "Postagens"
- [ ] Verificar posts com diferentes tipos de imagens
- [ ] Confirmar exibição completa das imagens

## Comportamento Esperado

### ✅ CORRETO (object-fit: contain)
```
Container 4x4:              Imagem 16:9:
┌──────────────┐           ┌──────────────┐
│              │           │▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ ← Espaço cinza
│              │     →     │              │
│              │           │    IMAGEM    │
│              │           │              │
└──────────────┘           │▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ ← Espaço cinza
                           └──────────────┘
```
- Imagem completa visível
- Nenhuma parte cortada
- Espaços preenchidos com #f3f4f6 (cinza claro)

### ❌ INCORRETO (se voltar a cortar)
```
Container 4x4:              Imagem 16:9:
┌──────────────┐           ┌──────────────┐
│              │           │   [CORTADA]  │ ← Laterais cortadas
│              │     →     │              │
│              │           │              │
│              │           │              │
└──────────────┘           └──────────────┘
```
- Partes da imagem não visíveis
- Imagem cortada nas laterais ou topo/base

## Validação Visual

### Desktop (> 980px)
- [ ] Imagens no feed aparecem completas
- [ ] Imagens em perfis aparecem completas
- [ ] Background cinza visível quando necessário
- [ ] Bordas arredondadas (24px para única, 16px para grid)

### Mobile (< 980px)
- [ ] Layout responsivo funciona corretamente
- [ ] Imagens completas em telas pequenas
- [ ] Touch/scroll funciona normalmente

## Casos de Borda

- [ ] Imagem muito larga (ex: 3000x500) → deve aparecer completa com muito espaço em cima/baixo
- [ ] Imagem muito alta (ex: 500x3000) → deve aparecer completa com muito espaço nas laterais
- [ ] Imagem pequena (ex: 100x100) → deve aparecer sem pixelização
- [ ] Post sem imagem → não deve quebrar o layout

## Ferramentas de Teste

### Chrome DevTools
1. Abrir DevTools (F12)
2. Ir para Elements tab
3. Inspecionar `.post-media img`
4. Verificar computed style: `object-fit: contain`

### Screenshot Comparison
1. Tirar screenshot de post com imagem horizontal ANTES
2. Tirar screenshot de post com imagem horizontal DEPOIS
3. Comparar: antes cortava, depois mostra completa

## Critérios de Aceitação

✅ **PASSOU** se:
- Todas as imagens aparecem completas (sem cortes)
- Formato 4x4 (1:1) é mantido
- Background #f3f4f6 preenche espaços vazios
- Não há distorção nas imagens

❌ **FALHOU** se:
- Alguma imagem aparece cortada
- Imagens ficam distorcidas
- Layout quebra em alguma página
- Aspecto ratio não é respeitado

## Regressão

Verificar que a mudança **NÃO** afetou:
- [ ] Avatares de usuário (devem continuar com object-fit: cover)
- [ ] Outras imagens do site (logos, ícones, etc.)
- [ ] Performance de carregamento
- [ ] Funcionalidade de curtir/comentar posts

## Notas

- A cor de fundo #f3f4f6 é intencional para áreas vazias
- O formato 4x4 (1:1) é mantido conforme requisito do usuário
- `object-fit: contain` mostra a imagem completa, `cover` cortaria
