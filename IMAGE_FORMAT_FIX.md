# Correção de Formato de Imagens no Feed e Perfis

## Problema Relatado

"quando publico uma imagem, no feed o formato dela deveria ser 4x4. E a imagem não aparece em meu_perfil e perfil, apenas o texto."

## Problemas Identificados

1. **No feed (index.html/feed.js)**: As imagens não estavam sendo renderizadas pelo `feed.js`, apenas pela versão em `index.html`
2. **Em meu_perfil.html**: As imagens não apareciam nas postagens
3. **Em perfil.html**: As imagens não apareciam nas postagens
4. **APIs de perfil**: Os endpoints `/api/posts/me` e `/api/posts/usuario/<user_id>` não retornavam o array `images` necessário para renderização

## Solução Implementada

### 1. Feed Principal (`feed.js`)

**Adicionado:**
- Função `renderPostImages()` para processar e renderizar imagens com aspect-ratio 1:1 (formato 4x4)
- Suporte para imagens únicas e múltiplas (grid 2, 3 ou 4 imagens)
- Integração na função `renderPost()` para exibir imagens automaticamente

```javascript
function renderPostImages(raw){
  if(!raw) return '';
  const parts = raw.split('|').filter(Boolean);
  if(!parts.length) return '';
  
  const getSrc = (path) => /^https?:\/\//i.test(path) ? path : `/static/${path}`;
  
  if(parts.length === 1){
    return `<div class="post-media"><img src="${getSrc(parts[0])}" alt="Imagem do post" onerror="this.style.display='none'"/></div>`;
  }
  
  const cls = parts.length===2? 'grid-2' : (parts.length===3? 'grid-3':'grid-4');
  const imgs = parts.map(p=>`<div class="pm-item"><img src="${getSrc(p)}" alt="Imagem do post" onerror="this.style.display='none'"/></div>`).join('');
  return `<div class="post-media multi ${cls}">${imgs}</div>`;
}
```

### 2. Página Meu Perfil (`meu_perfil.html`)

**Adicionado:**
- Estilos CSS para `.post-media` com `aspect-ratio: 1/1` (formato 4x4)
- Função `renderPostImages()` no script da página
- Integração na renderização de posts para exibir imagens

**CSS adicionado:**
```css
.post-media img { 
  width:100%; 
  display:block; 
  border-radius:24px; 
  margin:.6rem 0 1.1rem; 
  object-fit:cover; 
  background:#f3f4f6; 
  max-height:380px; 
  aspect-ratio:1/1; /* Formato 4x4 */
}
.post-media { position:relative; overflow:hidden; }
.post-media.multi { display:grid; gap:8px; margin:.6rem 0 1.1rem; }
.post-media.multi.grid-2 { grid-template-columns:repeat(2,1fr); }
.post-media.multi.grid-3 { grid-template-columns:repeat(3,1fr); }
.post-media.multi.grid-4 { grid-template-columns:repeat(2,1fr); }
.post-media.multi .pm-item img { margin:0; height:180px; border-radius:16px; object-fit:cover; }
```

### 3. Página Perfil de Outro Usuário (`perfil.html`)

**Adicionado:**
- Mesmos estilos CSS e função `renderPostImages()`
- Substituição da renderização antiga de imagens pela nova função

**Antes:**
```javascript
${p.imagem ? `<img src='/static/${p.imagem}' style='max-width:100%;border-radius:8px;margin-top:4px;'>` : ''}
```

**Depois:**
```javascript
${ (p.images && p.images.length) ? renderPostImages(p.images.join('|')) : (p.imagem ? renderPostImages(p.imagem) : '') }
```

### 4. APIs de Perfil (`routes/__init__.py`)

**Atualizado `/api/posts/me`:**
```python
imagens_concat = p.imagem or ''
imagens_list = [seg for seg in imagens_concat.split('|') if seg]
result.append({
    # ... outros campos
    'imagem': imagens_concat,
    'images': imagens_list,  # NOVO: array de imagens
    # ...
})
```

**Atualizado `/api/posts/usuario/<user_id>`:**
- Mesma lógica aplicada para retornar o array `images`

## Formato das Imagens

### Imagem Única
- **Aspect Ratio**: 1:1 (formato quadrado/4x4)
- **Max Height**: 380px
- **Object Fit**: cover (mantém proporção, corta excesso)
- **Border Radius**: 24px

### Múltiplas Imagens
- **2 imagens**: Grid de 2 colunas (2x1)
- **3 imagens**: Grid de 3 colunas (3x1)
- **4+ imagens**: Grid de 2x2
- **Altura fixa**: 180px por imagem
- **Border Radius**: 16px
- **Gap entre imagens**: 8px

## Estrutura de Dados

As imagens são armazenadas no campo `imagem` do Post como string separada por pipes (`|`):
- Uma imagem: `"uploads/post123.jpg"`
- Múltiplas: `"uploads/post123_1.jpg|uploads/post123_2.jpg|uploads/post123_3.jpg"`

A API converte isso em:
```json
{
  "imagem": "uploads/post123_1.jpg|uploads/post123_2.jpg",
  "images": ["uploads/post123_1.jpg", "uploads/post123_2.jpg"]
}
```

## Consistência Entre Páginas

Agora todas as páginas usam a mesma lógica de renderização:
- ✅ `index.html` (feed principal)
- ✅ `feed.js` (feed dinâmico)
- ✅ `meu_perfil.html` (meu perfil)
- ✅ `perfil.html` (perfil de outros usuários)

## Compatibilidade

- Funciona com URLs absolutas (https://) e paths locais (/static/)
- Tratamento de erros com `onerror="this.style.display='none'"`
- Suporte a imagens únicas e múltiplas
- Aspect ratio 1:1 mantém formato 4x4 independente da resolução original

## Screenshot de Exemplo

![Layout de Imagens 4x4](https://github.com/user-attachments/assets/982a6700-3f30-41d1-887c-cb7996664306)

A imagem acima mostra:
1. **Exemplo 1**: Imagem única com aspect-ratio 1:1 (formato 4x4)
2. **Exemplo 2**: Duas imagens em grid 2 colunas
3. **Exemplo 3**: Três imagens em grid 3 colunas
4. **Exemplo 4**: Quatro imagens em grid 2x2

## Testes Recomendados

- [ ] Publicar post com 1 imagem no feed - verificar formato 4x4
- [ ] Publicar post com 2 imagens - verificar grid 2 colunas
- [ ] Publicar post com 3 imagens - verificar grid 3 colunas
- [ ] Publicar post com 4+ imagens - verificar grid 2x2
- [ ] Verificar exibição em meu_perfil
- [ ] Verificar exibição em perfil de outro usuário
- [ ] Testar com imagens de diferentes proporções (vertical, horizontal, quadrada)
- [ ] Verificar responsividade mobile
