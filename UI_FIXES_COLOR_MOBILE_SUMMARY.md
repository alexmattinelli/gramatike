# UI Fixes: Color Scheme and Mobile Layout Improvements

## Summary of Changes

This PR addresses multiple UI issues related to color scheme consistency and mobile layout problems.

## 1. Color Scheme Updates (Blue → Purple)

### Files Changed:
- `gramatike_app/templates/esqueci_senha.html`
- `gramatike_app/templates/admin/dashboard.html`

### Changes Made:

#### esqueci_senha.html
**Before:**
- Submit button: `#007bff` (blue)
- Button hover: `#0056b3` (dark blue)
- Back link: `#007bff` (blue)

**After:**
- Submit button: `#9B5DE5` (purple)
- Button hover: `#7d3dc9` (dark purple)
- Back link: `#9B5DE5` (purple)

#### admin/dashboard.html
**Before:**
- Light mode gradient: `linear-gradient(120deg,#79b6ff,#9a8bff 55%,#ff9ac2)` (blue to pink)
- Dark mode accent: `#6d8dff` (blue)
- Dark mode accent-hover: `#5477f0` (blue)
- Dark mode gradient: `linear-gradient(120deg,#325f8f,#4b48a3 55%,#a84672)` (blue gradient)

**After:**
- Light mode gradient: `linear-gradient(120deg,#9B5DE5,#b896e8 55%,#d8b5f0)` (purple gradient)
- Dark mode accent: `#9B5DE5` (purple)
- Dark mode accent-hover: `#7d3dc9` (dark purple)
- Dark mode gradient: `linear-gradient(120deg,#7d3dc9,#8a5dd4 55%,#9B5DE5)` (purple gradient)

## 2. Mobile Layout Fixes

### Painel de Controle (Admin Dashboard)
**File:** `gramatike_app/templates/admin/dashboard.html`

**Issues Fixed:**
- Header was too large on mobile
- Tab links (Geral, Analytics, Edu, Gramátike, Publi) were not aligned properly

**Changes:**
```css
/* Mobile: Header mais compacto */
@media (max-width: 900px){ 
  header.site-head { padding:18px clamp(12px,3vw,24px) 28px; }
  .logo { font-size:1.8rem !important; }
}

/* Mobile: Smaller tabs, keep in same line */
@media (max-width: 900px){ 
  .tabs { gap:.4rem; margin-top:.8rem; padding:0 12px; }
  .tab-link { font-size:.6rem; padding:.5rem .75rem .48rem; letter-spacing:.4px; }
}
```

### Perfil and Meu Perfil
**Files:** 
- `gramatike_app/templates/perfil.html`
- `gramatike_app/templates/meu_perfil.html`

**Issues Fixed:**
- Large header on mobile
- Profile cards overflowing screen
- Content cards overflowing screen

**Changes:**
```css
/* Mobile: Header mais compacto */
@media (max-width: 900px){ 
  header.site-head { padding:14px clamp(12px,3vw,20px) 22px; }
  .logo { font-size:1.8rem !important; }
}

@media (max-width: 900px) {
  .profile-header, .tabs, .tab-content { width: 100%; padding: 1.2rem; }
  .profile-header { flex-direction: column; text-align: center; }
  .avatar { width: 80px; height: 80px; font-size: 2rem; }
  .profile-info h2 { font-size: 1.1rem; }
  main { padding: 0 16px; margin: 1rem 0; }
}
```

### Dinâmicas View
**File:** `gramatike_app/templates/dinamica_view.html`

**Issues Fixed:**
- Cards overflowing on mobile
- Deformed layout elements

**Changes:**
```css
/* Mobile: Header e layout mais compactos */
@media (max-width:768px){ 
  header.site-head { padding:18px 16px 28px; }
  .logo { font-size:1.7rem; } 
  main { padding:0 16px; margin:1.5rem auto 2rem; }
  .card { padding:.9rem; border-radius:16px; max-width:100%; overflow-x:hidden; }
  .poll-label { min-width:80px; font-size:.7rem; }
  .cloud { padding:.8rem; gap:.4rem .6rem; }
}
```

### Post Detail Page
**File:** `gramatike_app/templates/post_detail.html`

**Issues Fixed:**
- Profile picture not properly displayed
- Layout misaligned on mobile

**Changes:**
```css
/* Mobile: Header e layout mais compactos */
@media (max-width: 768px) {
  header.site-head { padding:18px 16px 28px; }
  .logo { font-size:1.8rem; }
  main { padding:0 16px; margin:1.5rem auto 2rem; }
  .card { padding:.9rem 1rem; border-radius:18px; }
  .post-header { gap:.7rem; flex-wrap:wrap; }
  .post-avatar { width:42px; height:42px; }
  .post-username { font-size:.9rem; }
  .post-date { font-size:.7rem; width:100%; margin-left:0; }
  .post-content { font-size:1rem; }
}
```

## 3. Portal Gramátike - Rich Text Formatting

**File:** `gramatike_app/templates/gramatike_edu.html`

**Issues Fixed:**
- Text posted in Portal Gramátike was not showing formatting (bold, italic, paragraphs)

**Changes:**

1. Changed from `textContent` to `innerHTML` to preserve HTML formatting:
```javascript
// Before:
node.querySelector('.fi-body').textContent = it.snippet || (it.resumo||'');

// After:
node.querySelector('.fi-body').innerHTML = it.snippet || (it.resumo||'');
```

2. Added CSS to properly style HTML elements within fi-body:
```css
/* Preserve HTML formatting in novidade descriptions */
.fi-body p { margin:.4rem 0; }
.fi-body strong, .fi-body b { font-weight:800; color:var(--text); }
.fi-body em, .fi-body i { font-style:italic; }
.fi-body ul, .fi-body ol { margin:.4rem 0; padding-left:1.5rem; }
.fi-body li { margin:.2rem 0; }
.fi-body h1, .fi-body h2, .fi-body h3 { font-size:.85rem; font-weight:800; margin:.6rem 0 .4rem; color:#6233B5; }
```

## Testing Checklist

### Color Changes
- [ ] Test esqueci_senha page - verify button color is purple
- [ ] Test admin dashboard in light mode - verify gradient is purple
- [ ] Test admin dashboard in dark mode - verify accent colors are purple

### Mobile Layout
- [ ] Test Painel de Controle on mobile (< 900px width)
  - [ ] Verify header is compact
  - [ ] Verify all tab links are in the same line
- [ ] Test Perfil page on mobile
  - [ ] Verify header is compact
  - [ ] Verify profile card doesn't overflow
  - [ ] Verify posts don't overflow
- [ ] Test Meu Perfil page on mobile
  - [ ] Verify same fixes as Perfil
- [ ] Test Dinâmicas View on mobile
  - [ ] Verify cards don't overflow
  - [ ] Verify layout is not deformed
- [ ] Test Post detail page on mobile
  - [ ] Verify profile picture is displayed
  - [ ] Verify layout is properly aligned

### Portal Gramátike
- [ ] Create a test novidade with bold text
- [ ] Create a test novidade with italic text
- [ ] Create a test novidade with paragraphs
- [ ] Create a test novidade with lists
- [ ] Verify all formatting is preserved on PC
- [ ] Verify all formatting is preserved on mobile

## Notes

- All changes maintain backward compatibility
- No database migrations required
- Changes are purely CSS and minor JavaScript
- Purple color scheme (#9B5DE5) is now consistent across all components
- Mobile responsive breakpoints set at 900px and 768px depending on component
