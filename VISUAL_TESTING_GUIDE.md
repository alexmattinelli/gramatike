# Visual Testing Guide - UI Fixes

## How to Test the Changes

### Setup
1. Deploy the changes to a test environment
2. Open browser DevTools (F12)
3. Use responsive design mode to test mobile layouts
4. Test both desktop and mobile views

## 1. Testing Color Changes

### Esqueci Senha Page
**URL:** `/esqueci_senha`

**Desktop Test:**
1. Navigate to the forgot password page
2. Verify the "Enviar link de recuperação" button is purple (#9B5DE5)
3. Hover over the button - it should darken to #7d3dc9
4. Verify the "Voltar ao login" link is purple (#9B5DE5)

**Expected Result:**
- No blue colors should appear
- All interactive elements should be purple

### Admin Dashboard
**URL:** `/admin/dashboard`

**Desktop Test (Light Mode):**
1. Log in as admin
2. Navigate to Painel de Controle
3. Look for gradient colors in any decorative elements
4. Verify purple gradient appears instead of blue

**Desktop Test (Dark Mode):**
1. If dark mode is available, enable it
2. Verify accent colors are purple (#9B5DE5) not blue
3. Check hover states on buttons - should use purple (#7d3dc9)

**Expected Result:**
- All gradients use purple tones
- No blue (#79b6ff, #6d8dff, #5477f0) colors visible
- Accent colors consistently purple

---

## 2. Testing Mobile Layouts

### Painel de Controle (Admin Dashboard)
**URL:** `/admin/dashboard`

**Mobile Test (Screen width < 900px):**
1. Set browser width to 375px (mobile phone size)
2. Verify header "Painel de Controle" is readable but compact
3. Check that all 5 tabs (Geral, Analytics, Edu, Gramátike, Publi) are visible
4. Verify tabs are in a single line (may wrap if needed, but should fit reasonably)
5. Verify tabs are not cut off or overlapping

**Visual Checkpoints:**
- ✅ Header padding: should be smaller (~18px top/bottom)
- ✅ Logo font size: ~1.8rem (smaller than desktop's 2.6rem)
- ✅ Tabs: smaller font (~0.6rem), reduced padding
- ✅ All tabs visible and clickable

### Perfil Page
**URL:** `/perfil/<username>`

**Mobile Test (Screen width < 900px):**
1. Set browser width to 375px
2. Navigate to any user profile
3. Verify header is compact
4. Verify profile card is centered and doesn't overflow
5. Check that profile avatar, username, and info are visible
6. Verify posts list doesn't overflow screen
7. Scroll to check all content is accessible

**Visual Checkpoints:**
- ✅ Header: compact with ~14px padding
- ✅ Logo: 1.8rem font size
- ✅ Profile card: 100% width with 1.2rem padding
- ✅ Avatar: 80px × 80px (smaller than desktop's 120px)
- ✅ Profile layout: switches to column layout on mobile
- ✅ No horizontal scrolling

### Meu Perfil Page
**URL:** `/meu_perfil`

**Mobile Test (Screen width < 900px):**
1. Log in and navigate to your profile
2. Perform the same checks as the Perfil page above
3. Verify edit profile functionality still works
4. Check that all sections (profile info, posts, etc.) are accessible

**Visual Checkpoints:**
- ✅ Same as Perfil page
- ✅ Edit buttons remain accessible
- ✅ Modal forms display properly on mobile

### Dinâmicas View
**URL:** `/dinamicas/<id>`

**Mobile Test (Screen width < 768px):**
1. Set browser width to 375px
2. Navigate to any dinâmica
3. Verify header is compact
4. Check that poll options or word cloud cards don't overflow
5. Verify all interactive elements (buttons, inputs) are accessible
6. Test voting/interaction on mobile

**Visual Checkpoints:**
- ✅ Header padding: 18px 16px 28px
- ✅ Logo: 1.7rem font size
- ✅ Cards: 0.9rem padding, don't overflow
- ✅ Poll labels: min-width 80px with smaller font
- ✅ Word cloud: compact padding, proper word wrapping
- ✅ No horizontal scrolling

### Post Detail Page
**URL:** `/post/<id>`

**Mobile Test (Screen width < 768px):**
1. Set browser width to 375px
2. Navigate to any post
3. **CRITICAL:** Verify profile picture/avatar is visible
4. Check username is displayed
5. Verify date is on its own line (not crowded with other info)
6. Check post content is readable and doesn't overflow
7. Verify any images in the post scale properly

**Visual Checkpoints:**
- ✅ Header: compact (18px 16px 28px padding)
- ✅ Logo: 1.8rem font size
- ✅ **Profile avatar: 42px × 42px and VISIBLE**
- ✅ Post header: wraps properly with 0.7rem gap
- ✅ Date: displays on separate line with 100% width
- ✅ Post content: 1rem font size
- ✅ No horizontal scrolling

---

## 3. Testing Portal Gramátike Rich Text

### Creating Test Content
**URL:** `/admin/dashboard` (Gramátike tab)

**Preparation:**
1. Log in as admin
2. Navigate to Painel de Controle
3. Click on "Gramátike" tab
4. Find "Postar Novidade" form

**Test Cases:**

#### Test 1: Bold Text
1. In the rich text editor, type: "Esta palavra está em **negrito**"
2. Select "negrito" and click Bold button (B)
3. Click "Adicionar"
4. Navigate to `/gramatike_edu`
5. Find your novidade in the feed
6. **Verify:** The word "negrito" appears bold and darker

#### Test 2: Italic Text
1. Create a new novidade: "Esta palavra está em *itálico*"
2. Select "itálico" and click Italic button (I)
3. Click "Adicionar"
4. Navigate to `/gramatike_edu`
5. **Verify:** The word "itálico" appears in italic style

#### Test 3: Paragraphs
1. Create a new novidade with multiple paragraphs:
```
Primeiro parágrafo.

Segundo parágrafo.

Terceiro parágrafo.
```
2. Press Enter between paragraphs to create spacing
3. Click "Adicionar"
4. Navigate to `/gramatike_edu`
5. **Verify:** Paragraphs have proper spacing (0.4rem between them)

#### Test 4: Lists
1. Create a new novidade with a list:
```
Itens importantes:
- Item 1
- Item 2  
- Item 3
```
2. Use the bullet list button in the editor
3. Click "Adicionar"
4. Navigate to `/gramatike_edu`
5. **Verify:** List appears with bullets and proper indentation

#### Test 5: Headings
1. Create a new novidade with headings:
```
# Título Principal
Este é o conteúdo.
## Subtítulo
Mais conteúdo aqui.
```
2. Use heading dropdown in editor
3. Click "Adicionar"
4. Navigate to `/gramatike_edu`
5. **Verify:** Headings are larger, bold, and purple-colored

**Visual Checkpoints for Rich Text:**
- ✅ Bold text: font-weight 800, darker color
- ✅ Italic text: font-style italic
- ✅ Paragraphs: 0.4rem margin between them
- ✅ Lists: indented 1.5rem with proper bullets
- ✅ Headings: 0.85rem font, 800 weight, purple color (#6233B5)
- ✅ Formatting preserved on both desktop AND mobile

### Mobile Test for Rich Text
1. Set browser width to 375px
2. Navigate to `/gramatike_edu`
3. Find a novidade with formatting
4. **Verify:** All formatting (bold, italic, paragraphs, lists) remains visible and readable on mobile

---

## Troubleshooting

### If colors are still blue:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh the page (Ctrl+Shift+R)
3. Check browser DevTools to see which CSS is being applied

### If mobile layouts still overflow:
1. Check actual screen width in DevTools
2. Verify the media query breakpoints are being triggered
3. Check for any inline styles that might override the CSS
4. Look for `max-width: 100%` and `overflow-x: hidden` being applied

### If rich text formatting doesn't show:
1. Check browser console for JavaScript errors
2. Verify the content in database has HTML tags (not plain text)
3. Inspect the `.fi-body` element to confirm innerHTML is being used
4. Check that CSS rules for `.fi-body strong`, `.fi-body p`, etc. are applied

---

## Success Criteria

### All tests pass when:
1. **No blue colors** visible in esqueci_senha or admin dashboard
2. **All mobile layouts** fit within screen width without horizontal scrolling
3. **Headers are compact** on mobile (< 900px)
4. **Profile pictures appear** on post detail page (both PC and mobile)
5. **Rich text formatting** (bold, italic, paragraphs, lists) displays correctly in Portal Gramátike feed
6. **No regressions** - existing functionality continues to work

### Browser Testing
Test on:
- Chrome/Edge (desktop and mobile view)
- Firefox (desktop and mobile view)
- Safari (iOS if possible)
- Actual mobile device (recommended)

### Screen Sizes to Test
- 320px (small mobile)
- 375px (standard mobile - iPhone)
- 768px (tablet)
- 1024px (desktop)
- 1920px (large desktop)
