# Testing Guide - Mobile Improvements

## 🧪 Manual Testing Checklist

### Prerequisites
- Browser with responsive design mode (Chrome DevTools, Firefox DevTools)
- Or actual mobile device for testing

### Test Cases

#### 1. Index Page (Main Feed)

**Desktop View (> 980px):**
- [ ] Verify quick nav shows "Em breve" button (non-clickable)
- [ ] Verify sidebar shows Suporte icon (this should remain for desktop)

**Mobile View (< 980px):**
- [ ] **Post Cards:**
  - [ ] Cards appear larger than before
  - [ ] More padding around content
  - [ ] Wider appearance (extends beyond margins)
  
- [ ] **Mobile Actions Card:**
  - [ ] First button shows Dinâmicas icon (puzzle pieces with gradient)
  - [ ] Click Dinâmicas → redirects to `/dinamicas_home`
  - [ ] Other buttons: Jogo da Velha, Notificações, Amigues still present
  
- [ ] **Mobile Bottom Nav:**
  - [ ] Shows: Início | Educação | + | Em breve | Perfil
  - [ ] "Em breve" has clock icon
  - [ ] "Em breve" is NOT clickable (no hover effect)
  - [ ] Other nav items work correctly

#### 2. Educação Page (gramatike_edu.html)

**Mobile View (< 980px):**
- [ ] Mobile bottom nav shows: Início | Educação | + | Em breve | Perfil
- [ ] "Educação" item is highlighted (active)
- [ ] No "Suporte" button visible
- [ ] "Em breve" is in 4th position (before Perfil)

#### 3. Apostilas Page

**Mobile View (< 980px):**
- [ ] Mobile bottom nav shows: Início | Educação | + | Em breve | Perfil
- [ ] No "Suporte" button visible
- [ ] All navigation items work correctly

#### 4. Exercícios Page

**Mobile View (< 980px):**
- [ ] Mobile bottom nav shows: Início | Educação | + | Em breve | Perfil
- [ ] No "Suporte" button visible
- [ ] All navigation items work correctly

#### 5. Artigos Page

**Mobile View (< 980px):**
- [ ] Mobile bottom nav shows: Início | Educação | + | Em breve | Perfil
- [ ] No "Suporte" button visible
- [ ] All navigation items work correctly

#### 6. Criar Post Page

**Mobile View (< 980px):**
- [ ] Mobile bottom nav shows: Início | Educação | + | Em breve | Perfil
- [ ] "+" button is highlighted/active (create post page)
- [ ] No "Suporte" button visible

#### 7. Perfil Page

**Mobile View (< 980px):**
- [ ] Mobile bottom nav shows: Início | Educação | + | Em breve | Perfil
- [ ] "Perfil" item is highlighted (active)
- [ ] No "Suporte" button visible

---

## 🔍 Visual Verification

### Expected Mobile Bottom Nav Layout:

```
┌─────────────────────────────────────────────┐
│                                             │
│  🏠         📚          ⊕         🕐       👤  │
│ Início   Educação      +      Em breve  Perfil│
│                                             │
└─────────────────────────────────────────────┘
```

### Expected Dinâmicas Icon (Mobile Actions Card):

```
╔════════════════════════════════════╗
║  🧩   🎮   🔔   👥                 ║
║  Din  Jogo Not  Ami                ║
╚════════════════════════════════════╝
```

Where 🧩 = Dinâmicas (puzzle icon with purple gradient)

---

## 📏 Responsive Breakpoints

### Mobile View Activation:
- **Width:** < 980px
- **Changes:**
  - Sidebar hidden
  - Mobile bottom nav visible
  - Post cards enlarged
  - Mobile actions card visible

### Desktop View:
- **Width:** ≥ 980px
- **Changes:**
  - Sidebar visible (with Suporte icon)
  - Mobile bottom nav hidden
  - Post cards normal size
  - Mobile actions card hidden

---

## 🐛 Known Issues / Edge Cases

None identified. All changes are CSS-based and use existing patterns.

---

## ✅ Success Criteria

All tests pass when:
1. ✅ Post cards are visibly larger on mobile (Index page)
2. ✅ Dinâmicas icon appears in mobile actions card with correct gradient
3. ✅ All 7 pages show identical mobile bottom nav
4. ✅ "Em breve" appears in all mobile bottom navs (4th position)
5. ✅ No "Suporte" in any mobile bottom nav
6. ✅ Desktop sidebar still shows Suporte (Index page only)
7. ✅ All navigation links work correctly

---

## 📱 Device Testing Matrix

| Device Type | Screen Size | Status |
|-------------|-------------|--------|
| iPhone SE   | 375px       | ⬜ Not tested |
| iPhone 12   | 390px       | ⬜ Not tested |
| iPhone 14 Pro Max | 430px | ⬜ Not tested |
| iPad Mini   | 768px       | ⬜ Not tested |
| iPad Pro    | 1024px      | ⬜ Not tested |
| Android Small | 360px    | ⬜ Not tested |
| Android Medium | 412px   | ⬜ Not tested |

---

## 🎯 Quick Test URLs (after deployment)

- Index: `/`
- Educação: `/educacao`
- Apostilas: `/apostilas`
- Exercícios: `/exercicios`
- Artigos: `/artigos`
- Criar Post: `/criar-post`
- Perfil: `/perfil/@username`

---

## 📸 Screenshots Needed

For documentation:
1. [ ] Mobile view - Index page showing enlarged post cards
2. [ ] Mobile view - Mobile actions card with Dinâmicas icon
3. [ ] Mobile view - Bottom nav on Index
4. [ ] Mobile view - Bottom nav on Educação
5. [ ] Mobile view - Bottom nav on any other page (to show consistency)
6. [ ] Desktop view - Sidebar with Suporte icon (to show it still exists)

---

## 🔄 Rollback Plan

If issues arise:
1. Revert commit: `git revert 107bae9`
2. All changes are in template files only
3. No database migrations affected
4. No backend logic changed

---

## 📝 Notes

- Changes are purely visual (CSS + HTML)
- No JavaScript functionality modified
- No database schema changes
- Backward compatible with existing features
