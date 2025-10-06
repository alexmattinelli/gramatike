# Fix: Imagens e PDFs não estão aparecendo

## 🐛 Problemas Identificados

1. **Imagens dos posts não aparecem no feed**
   - Causa: O código JavaScript em `index.html` sempre adicionava `/static/` como prefixo aos caminhos de imagem
   - Isso quebrava URLs completas do Supabase Storage (que começam com `https://`)

2. **PDFs não abrem em Apostilas**
   - Causa: O template `apostilas.html` usava `url_for('static', filename=...)` para todos os caminhos
   - Isso não funciona quando o caminho é uma URL completa do Supabase

## ✅ Soluções Implementadas

### 1. Fix no `index.html` - Função `renderPostImages()`

**Antes:**
```javascript
function renderPostImages(raw){
  // ...
  return `<div class="post-media"><img data-src="/static/${parts[0]}" .../></div>`;
}
```

**Depois:**
```javascript
function renderPostImages(raw){
  // ...
  // Helper: determinar src correto (URL ou path local)
  const getSrc = (path) => /^https?:\/\//i.test(path) ? path : `/static/${path}`;
  return `<div class="post-media"><img data-src="${getSrc(parts[0])}" .../></div>`;
}
```

**O que mudou:**
- Adicionada função helper `getSrc()` que detecta se o caminho é uma URL (começa com `http://` ou `https://`)
- Se for URL: usa diretamente
- Se for caminho local: adiciona o prefixo `/static/`

### 2. Fix no `apostilas.html` - Links de PDF

**Antes:**
```jinja2
{% if c.file_path %}
    {% set pdf_src = url_for('static', filename=c.file_path) %}
    <a href="{{ pdf_src }}" ...>{{ c.titulo }}</a>
{% endif %}
```

**Depois:**
```jinja2
{% if c.file_path %}
    {% if c.file_path.startswith('http://') or c.file_path.startswith('https://') %}
        <a href="{{ c.file_path }}" ...>{{ c.titulo }}</a>
    {% else %}
        {% set pdf_src = url_for('static', filename=c.file_path) %}
        <a href="{{ pdf_src }}" ...>{{ c.titulo }}</a>
    {% endif %}
{% endif %}
```

**O que mudou:**
- Verifica se `file_path` é uma URL completa (começa com `http://` ou `https://`)
- Se for URL: usa diretamente
- Se for caminho local: usa `url_for('static', filename=...)`

### 3. Fix no `apostilas.html` - Thumbnails de PDF

**Antes:**
```jinja2
<img class="pdf-thumb" src="{{ url_for('static', filename=extra.thumb) }}" ... />
```

**Depois:**
```jinja2
{% if extra.thumb.startswith('http://') or extra.thumb.startswith('https://') %}
    <img class="pdf-thumb" src="{{ extra.thumb }}" ... />
{% else %}
    <img class="pdf-thumb" src="{{ url_for('static', filename=extra.thumb) }}" ... />
{% endif %}
```

**O que mudou:**
- Mesma lógica aplicada aos thumbnails
- Detecta URLs completas vs caminhos locais

## 🔍 Como Funciona

### Detecção de URL vs Caminho Local

**JavaScript (index.html):**
```javascript
/^https?:\/\//i.test(path)  // true se começar com http:// ou https://
```

**Jinja2 (apostilas.html):**
```jinja2
path.startswith('http://') or path.startswith('https://')
```

### Exemplos

| Entrada | Tipo | Output |
|---------|------|--------|
| `https://supabase.co/storage/v1/object/public/avatars/posts/123_file.jpg` | URL Supabase | `https://supabase.co/storage/...` |
| `uploads/posts/file.jpg` | Caminho local | `/static/uploads/posts/file.jpg` |
| `img/perfil.png` | Caminho local | `/static/img/perfil.png` |
| `http://example.com/file.pdf` | URL externa | `http://example.com/file.pdf` |

## 🧪 Testes Realizados

✅ Templates compilam sem erros (Jinja2)  
✅ Sintaxe Python válida  
✅ Lógica de detecção de URL funciona corretamente  
✅ Suporte tanto para caminhos locais quanto URLs do Supabase  

## 📋 Arquivos Modificados

1. `gramatike_app/templates/index.html`
   - Função `renderPostImages()` atualizada

2. `gramatike_app/templates/apostilas.html`
   - Links de PDF atualizados
   - Thumbnails atualizados
   - Detecção de PDF source (_pdf_src) atualizada

## 🚀 Compatibilidade

Estas mudanças são **100% compatíveis** com ambos os cenários:

### ✅ Com Supabase configurado
- URLs completas do Supabase funcionam corretamente
- Arquivos persistem entre deploys
- Funciona em produção (Vercel/serverless)

### ✅ Sem Supabase (desenvolvimento local)
- Caminhos locais continuam funcionando
- `/static/` é adicionado automaticamente
- Funciona em ambiente de desenvolvimento

## 🔗 Links Relacionados

- [QUICK_FIX_SUMMARY.md](QUICK_FIX_SUMMARY.md) - Resumo geral das correções
- [SUPABASE_UPLOAD_FIX.md](SUPABASE_UPLOAD_FIX.md) - Configuração do Supabase
- [FIXES_APPLIED.md](FIXES_APPLIED.md) - Detalhes técnicos

## ✨ Resultado Final

Agora o sistema suporta **automaticamente**:
- ✅ Imagens de posts do Supabase Storage
- ✅ Imagens de posts locais (desenvolvimento)
- ✅ PDFs de apostilas do Supabase Storage
- ✅ PDFs de apostilas locais (desenvolvimento)
- ✅ Thumbnails de PDFs (ambos os tipos)
- ✅ URLs externas (http/https)

**Sem necessidade de configuração adicional** - o código detecta automaticamente o tipo de caminho!
