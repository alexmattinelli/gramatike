# Visual Mockup - Mobile & Education Changes

## 📱 Mobile Post Cards - Before & After

### BEFORE (Desktop/Large Mobile):
```
┌─────────────────────────────────────────────┐
│  👤 @username  •  há 2 horas    [Seguir] [⋯]│
│                                             │
│  Este é o conteúdo do post...              │
│                                             │
│  ❤️ Curtir    💬 Comentar                  │
│                                             │
│  usuário1, usuário2 e mais 3 curtiram      │
└─────────────────────────────────────────────┘
```

### AFTER (Mobile < 980px):
```
┌──────────────────────────────────────────────────┐ ← Wider card
│  👤 @username  •  há 2 horas  [Seguir] [⋯]      │   (negative margin)
│                                                  │
│  Este é o conteúdo do post...                   │
│                                                  │
│  ❤️ Curtir  💬 Comentar                         │ ← Smaller buttons
│  (smaller)  (smaller)                            │
│                                                  │
│  usuário1, usuário2 e mais 3 curtiram           │
└──────────────────────────────────────────────────┘
```

**Changes**:
- Cards extend beyond normal container (full-bleed)
- Buttons reduced ~20% in size
- Menu button (⋯) more compact (28px vs 34px)

---

## 📚 Education Feed Pagination - Before & After

### BEFORE (No Pagination):
```
Gramátike Edu
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Buscar...]

┌─────────────────────────────────────────────┐
│ POST                                        │
│ Confira                                     │
│ Novo conteúdo educacional...                │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ DINÂMICA                                    │
│ Quiz de Português                           │
│ Teste seus conhecimentos...                 │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ NOVIDADE                                    │
│ Nova funcionalidade                         │
│ Confira as últimas atualizações...         │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ POST                                        │
│ Confira                                     │
│ Dicas de gramática...                       │
└─────────────────────────────────────────────┘

... (all items at once)
```

### AFTER (With Pagination - 3 Items):
```
Gramátike Edu
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Buscar...]

┌─────────────────────────────────────────────┐
│ POST                                        │
│ Confira                                     │
│ Novo conteúdo educacional...                │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ DINÂMICA                                    │
│ Quiz de Português                           │
│ Teste seus conhecimentos...                 │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ NOVIDADE                                    │
│ Nova funcionalidade                         │
│ Confira as últimas atualizações...         │
└─────────────────────────────────────────────┘

           ┌────────────────────────────────┐
           │  [1]  [2]  [3]  [4]  Próximo → │  ← Pagination
           └────────────────────────────────┘
            ^current (purple)
```

**Pagination Controls**:
```
Page 1:  [1] [2] [3] [4] Próximo →
         ^purple (current)

Page 2:  ← Anterior [1] [2] [3] [4] Próximo →
                        ^purple (current)

Page 4:  ← Anterior [1] [2] [3] [4]
                                 ^purple (current)
```

---

## 🍔 Menu Dropdown - Before & After

### BEFORE:
```
Gramátike Edu                    [🛠️ Painel]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           ^single button in corner
```

### AFTER (Closed):
```
Gramátike Edu                      [≡ Menu]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           ^hamburger icon + label
```

### AFTER (Open):
```
Gramátike Edu                      [≡ Menu]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┌──────────────┐
                                      │ 📄 📑 Artigos   │
                                      ├──────────────┤
                                      │ ⭐ 🧠 Exercícios│
                                      ├──────────────┤
                                      │ 📚 📚 Apostilas│
                                      ├──────────────┤
                                      │ 🌐 🎲 Dinâmicas│
                                      ├──────────────┤
                                      │ ⚙️ 🛠️ Painel   │
                                      └──────────────┘
           ^dropdown menu (white bg, purple icons)
```

**Menu Item Structure**:
```
┌────────────────────────────┐
│  [SVG]  📑 Artigos        │ ← Hover: light purple bg
│   ^purple icon  ^emoji     │
└────────────────────────────┘
```

---

## 🎨 Color Reference

```css
/* Main Colors */
--primary: #9B5DE5;        /* Purple (buttons, icons) */
--primary-dark: #7d3dc9;   /* Dark Purple (hover) */
--hover-bg: #f7f2ff;       /* Light Purple (menu hover) */

/* Pagination Buttons */
.pag-btn {
  background: #9B5DE5;     /* Normal */
}
.pag-btn:hover {
  background: #7d3dc9;     /* Hover */
}
.pag-btn[current] {
  background: #9B5DE5;     /* Current (non-clickable) */
}
```

---

## 📐 Size Reference

### Mobile Post Cards:
```
Desktop:
  padding: 1.6rem 1.9rem 1.3rem
  margin: 0 0 2rem

Mobile (< 980px):
  padding: 1.4rem 1.6rem 1.2rem
  margin: 0 -0.3rem 1.8rem  ← Negative margin makes wider
```

### Action Buttons:
```
Desktop:
  .post-actions button {
    padding: .45rem .9rem;
    font-size: .8rem;
    gap: .35rem;
  }

Mobile (< 980px):
  .post-actions button {
    padding: .35rem .7rem;   ← Smaller
    font-size: .72rem;       ← Smaller
    gap: .25rem;             ← Smaller
  }
```

### Menu Button:
```
Desktop:
  .post-menu-btn {
    width: 34px;
    height: 34px;
  }

Mobile (< 980px):
  .post-menu-btn {
    width: 28px;   ← Smaller
    height: 28px;  ← Smaller
  }
```

### Menu Dropdown:
```
Desktop/Tablet:
  min-width: 200px
  font-size: .75rem
  padding: 10px 14px
  svg: 18px × 18px

Mobile (< 480px):
  min-width: 180px   ← Smaller
  font-size: .7rem   ← Smaller
  padding: 9px 12px  ← Smaller
  svg: 16px × 16px   ← Smaller
```

---

## 📱 Responsive Breakpoints

```
Desktop (> 980px):
  ✓ Standard post cards
  ✓ Larger buttons
  ✓ Menu dropdown (if admin)
  ✓ No bottom nav
  ✓ Pagination visible

Tablet (768px - 980px):
  ✓ Mobile card styles
  ✓ Smaller buttons
  ✓ Menu dropdown (if admin)
  ✓ Bottom nav visible
  ✓ Pagination visible

Mobile (< 768px):
  ✓ Wide cards
  ✓ Smallest buttons
  ✓ Compact menu (if admin)
  ✓ Bottom nav visible
  ✓ Pagination visible

Small Mobile (< 480px):
  ✓ Wide cards
  ✓ Smallest buttons
  ✓ Extra compact menu
  ✓ Bottom nav visible
  ✓ Pagination visible
```

---

## 🔄 User Flow Examples

### 1. Browsing Education Feed (Mobile):
```
User opens /educacao
  ↓
Page loads with 3 items
  ↓
Pagination shows: [1] [2] [3] ... Próximo →
  ↓
User clicks "Próximo →"
  ↓
Page 2 loads (3 new items)
  ↓
Page scrolls to top smoothly
  ↓
Pagination shows: ← Anterior [1] [2] [3] ...
```

### 2. Using Menu Dropdown (Admin):
```
Admin on /educacao page
  ↓
Sees [≡ Menu] button in corner
  ↓
Clicks menu button
  ↓
Dropdown opens with 5 options
  ↓
Hovers over "Artigos"
  ↓
Background turns light purple
  ↓
Clicks "Artigos"
  ↓
Navigates to /artigos
```

### 3. Viewing Posts (Mobile):
```
User scrolls feed on mobile
  ↓
Sees wider post cards
  ↓
Posts feel immersive (full-bleed)
  ↓
Clicks smaller "❤️ Curtir" button
  ↓
Post is liked
  ↓
Button changes to "❤️ Curtido"
```

---

## ✨ Visual Highlights

### Post Cards:
```
┌──────────────────────────────────────┐
│  WIDER ON MOBILE                     │ ← Extends beyond container
│  (negative margin effect)            │
│                                      │
│  ❤️ SMALLER   💬 SMALLER            │ ← Compact buttons
└──────────────────────────────────────┘
```

### Pagination:
```
           ┌─────────────────────┐
           │  ← Anterior         │ ← Purple buttons
           │  [1] [2] [3]        │   (admin panel style)
           │  Próximo →          │
           └─────────────────────┘
```

### Menu:
```
                        [≡ Menu]
                           ↓
                    ┌──────────────┐
                    │ 📄 Artigos   │ ← Icons + emojis
                    │ ⭐ Exercícios│
                    │ 📚 Apostilas │ ← Purple SVGs
                    │ 🌐 Dinâmicas │
                    │ ⚙️ Painel    │ ← Hover: light purple
                    └──────────────┘
```

---

## 🎯 Key Visual Improvements

1. **Mobile Posts**: Wider, more immersive cards with compact buttons
2. **Education Feed**: Clean, paginated view (3 items) with clear navigation
3. **Menu Access**: Organized dropdown replacing single button, with visual icons

All changes maintain the purple (#9B5DE5) Gramátike brand color and smooth, polished aesthetic! ✨
