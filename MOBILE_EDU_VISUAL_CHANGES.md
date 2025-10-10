# Visual Changes Guide - Mobile and Education Improvements

## 📱 Mobile Post Cards

### Before:
```css
/* Posts had standard padding */
#feed-list article.post {
  padding: 1.6rem 1.9rem 1.3rem;
  margin: 0 0 2rem;
}

/* Action buttons were larger */
.post-actions button {
  padding: .45rem .9rem;
  font-size: .8rem;
  gap: .35rem;
}

/* Menu button was larger */
.post-menu-btn {
  width: 34px;
  height: 34px;
}
```

### After (Mobile < 980px):
```css
/* Cards are now wider with negative margin for full-bleed effect */
#feed-list article.post {
  padding: 1.4rem 1.6rem 1.2rem;
  margin: 0 -0.3rem 1.8rem;  /* ← Negative margin makes cards wider */
}

/* Action buttons are smaller and more compact */
.post-actions button {
  padding: .35rem .7rem;     /* ← Reduced padding */
  font-size: .72rem;         /* ← Smaller font */
  gap: .25rem;               /* ← Less gap between icon and text */
}

/* Menu button is more compact */
.post-menu-btn {
  width: 28px;                /* ← Smaller */
  height: 28px;               /* ← Smaller */
  font-size: .95rem;
}
```

### Visual Impact:
- 🎨 Cards extend slightly beyond container for immersive mobile experience
- 🔽 Buttons are ~20% smaller, reducing visual clutter
- 📐 Better use of mobile screen real estate

---

## 📚 Education Feed Pagination

### Before:
```javascript
// No pagination - all items loaded at once
async function search(q) {
  const resp = await fetch(`/api/gramatike/search?q=${q}&include_edu=0`);
  const data = await resp.json();
  render(data.items || []);  // Renders ALL items
}
```

### After:
```javascript
// Pagination with 3 items per page
let currentPage = 1;
let totalPages = 1;
const perPage = 3;  // ← Show only 3 items per page

async function search(q, page = 1) {
  const resp = await fetch(
    `/api/gramatike/search?q=${q}&include_edu=0&page=${page}&per_page=${perPage}`
  );
  const data = await resp.json();
  currentPage = data.page || 1;
  totalPages = data.total_pages || 1;
  render(data.items || []);
  renderPagination();  // ← Shows page controls
}
```

### Pagination UI:
```html
<!-- Dynamically generated pagination -->
<div id="pagination-container" style="margin-top:1.5rem; display:flex; gap:.4rem; justify-content:center;">
  <button onclick="changePage(1)" class="pag-btn">← Anterior</button>
  <span class="pag-btn" style="background:#9B5DE5; color:#fff;">1</span>
  <button onclick="changePage(2)" class="pag-btn">2</button>
  <button onclick="changePage(3)" class="pag-btn">3</button>
  <button onclick="changePage(2)" class="pag-btn">Próximo →</button>
</div>
```

### Pagination Button Style:
```css
.pag-btn {
  padding: .55rem .9rem;
  border-radius: 18px;
  background: #9B5DE5;
  color: #fff;
  font-weight: 600;
  font-size: .7rem;
  letter-spacing: .3px;
  cursor: pointer;
}

.pag-btn:hover {
  background: #7d3dc9;
}

/* Current page (non-clickable) */
.pag-btn[style*="background:#9B5DE5"] {
  pointer-events: none;
}
```

### Visual Impact:
- 📄 Shows exactly 3 educational items per page
- 🔢 Numbered page indicators (1, 2, 3...)
- ⏮️ Previous/Next navigation buttons
- 🎨 Same purple style as admin dashboard
- ⬆️ Smooth scroll to top when changing pages

---

## 🍔 Menu Dropdown in Education Section

### Before:
```html
<!-- Single "Painel" button -->
<a href="{{ url_for('admin.dashboard') }}" 
   style="position:absolute; top:14px; right:16px; ...">
  🛠️ Painel
</a>
```

### After:
```html
<!-- Menu button with dropdown -->
<div style="position:absolute; top:14px; right:16px;">
  <button id="menu-toggle" onclick="toggleMenu()" style="...">
    <!-- Hamburger icon (3 lines) -->
    <svg width="16" height="16" viewBox="0 0 24 24" ...>
      <line x1="3" y1="12" x2="21" y2="12"></line>
      <line x1="3" y1="6" x2="21" y2="6"></line>
      <line x1="3" y1="18" x2="21" y2="18"></line>
    </svg>
    Menu
  </button>
  
  <!-- Dropdown menu -->
  <div id="menu-dropdown" style="display:none; position:absolute; ...">
    <a href="/artigos">
      <svg>...</svg>
      📑 Artigos
    </a>
    <a href="/exercicios">
      <svg>...</svg>
      🧠 Exercícios
    </a>
    <a href="/apostilas">
      <svg>...</svg>
      📚 Apostilas
    </a>
    <a href="/dinamicas">
      <svg>...</svg>
      🎲 Dinâmicas
    </a>
    <a href="/admin/dashboard">
      <svg>...</svg>
      🛠️ Painel
    </a>
  </div>
</div>
```

### Menu JavaScript:
```javascript
// Toggle menu on button click
function toggleMenu() {
  const dropdown = document.getElementById('menu-dropdown');
  if (dropdown) {
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
  }
}

// Close menu when clicking outside
document.addEventListener('click', function(e) {
  const menuToggle = document.getElementById('menu-toggle');
  const dropdown = document.getElementById('menu-dropdown');
  if (dropdown && menuToggle && 
      !menuToggle.contains(e.target) && 
      !dropdown.contains(e.target)) {
    dropdown.style.display = 'none';
  }
});
```

### Menu Item Styling:
```html
<a href="..." style="
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  text-decoration: none;
  color: #333;
  font-size: .75rem;
  font-weight: 600;
  border-bottom: 1px solid #f0f0f0;
  transition: background .2s;
" 
onmouseover="this.style.background='#f7f2ff'" 
onmouseout="this.style.background='transparent'">
  <svg width="18" height="18" stroke="#9B5DE5" ...>...</svg>
  📑 Artigos
</a>
```

### Menu Features:
- 🍔 **Hamburger Icon**: Clear menu indicator with 3-line icon
- 📱 **5 Menu Options**: All with emoji + SVG icons
  - 📑 Artigos (Articles)
  - 🧠 Exercícios (Exercises)
  - 📚 Apostilas (Study Materials)
  - 🎲 Dinâmicas (Dynamics)
  - 🛠️ Painel (Admin Panel)
- 💜 **Purple Icons**: All SVGs use #9B5DE5 color
- ✨ **Hover Effect**: Light purple background (#f7f2ff)
- 🎯 **Click Outside**: Auto-closes when clicking elsewhere
- 📱 **Responsive**: Smaller on mobile (<480px)

### Responsive Menu Styles:
```css
@media (max-width:480px) { 
  #menu-dropdown { 
    min-width: 180px;
    font-size: .7rem;
  }
  #menu-dropdown a { 
    padding: 9px 12px;
    font-size: .7rem;
  }
  #menu-dropdown svg { 
    width: 16px;
    height: 16px;
  }
}
```

---

## 🎯 API Enhancement

### Before:
```python
@bp.route('/api/gramatike/search')
def api_gramatike_search():
    q = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 15) or 15), 40)
    
    # ... build items list ...
    
    return jsonify({'items': items})
```

### After:
```python
@bp.route('/api/gramatike/search')
def api_gramatike_search():
    q = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 15) or 15), 40)
    page = max(int(request.args.get('page', 1) or 1), 1)
    per_page = min(int(request.args.get('per_page', 15) or 15), 40)
    
    # ... build items list ...
    
    # Apply pagination
    total = len(items)
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_items = items[start_idx:end_idx]
    
    return jsonify({
        'items': paginated_items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    })
```

### API Response Example:
```json
{
  "items": [
    {
      "id": "nov-1",
      "title": "Nova funcionalidade...",
      "snippet": "Confira as novidades...",
      "tags": [],
      "url": "/novidade/1",
      "created_at": "2025-10-10T13:00:00",
      "source": "novidade"
    },
    {
      "id": "dyn-5",
      "title": "Dinâmica de Português",
      "snippet": "Teste seus conhecimentos...",
      "tags": ["quiz"],
      "url": "/dinamica/5",
      "created_at": "2025-10-09T15:30:00",
      "source": "dinamica"
    },
    {
      "id": 123,
      "title": "Novo post sobre gramática",
      "snippet": "Aprenda sobre...",
      "tags": ["gramática", "educação"],
      "url": "/post/123",
      "created_at": "2025-10-08T10:00:00",
      "source": "post"
    }
  ],
  "total": 45,
  "page": 1,
  "per_page": 3,
  "total_pages": 15
}
```

---

## 📊 Summary of Changes

### Files Modified:
1. ✅ `gramatike_app/templates/index.html`
   - Mobile-specific styles for wider cards
   - Smaller action buttons on mobile

2. ✅ `gramatike_app/templates/gramatike_edu.html`
   - Replaced Painel button with Menu dropdown
   - Added 5-option menu with icons
   - Implemented pagination UI (3 items per page)
   - Added pagination JavaScript
   - Added responsive menu styles

3. ✅ `gramatike_app/routes/__init__.py`
   - Enhanced API with pagination support
   - Added pagination metadata to response

### Design Consistency:
- 💜 All changes use purple (#9B5DE5) primary color
- 🎨 Consistent button styles and hover effects
- 📐 Rounded corners (border-radius: 18px, 12px, 8px)
- ✨ Smooth transitions (0.2s)
- 📱 Responsive design patterns
- ♿ Accessible navigation

### User Benefits:
1. **Mobile Users**: Better visual experience with optimized card sizes and button dimensions
2. **Education Users**: Easier content browsing with paginated feed (3 items at a time)
3. **Admin Users**: Quick access to all sections via organized dropdown menu
4. **All Users**: Consistent, polished UI matching the existing design system
