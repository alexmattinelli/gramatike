# Testing Checklist

## Pre-requisites
- [ ] Login as admin user
- [ ] Access admin dashboard at `/admin`

## 1. Article Posting Error Messages

### Test 1.1: Word Count Limit
- [ ] Navigate to Admin Panel → Edu → Artigos
- [ ] Click "Publicar Artigo"
- [ ] Fill in:
  - Título: "Teste de Limite de Palavras"
  - Corpo: [paste more than 5000 words]
- [ ] Click "Publicar"
- [ ] **Expected**: Error message showing "O artigo excede o limite de 5000 palavras (atual: XXXX palavras)"

### Test 1.2: Resumo Character Limit
- [ ] Fill in:
  - Título: "Teste de Resumo"
  - Resumo: [paste more than 1000 characters]
- [ ] Click "Publicar"
- [ ] **Expected**: Error message showing "O resumo excede o limite de 1000 caracteres (atual: XXXX caracteres)"

### Test 1.3: Title Character Limit
- [ ] Fill in:
  - Título: [paste more than 220 characters]
- [ ] Click "Publicar"
- [ ] **Expected**: Error message about title limit

### Test 1.4: Successful Post
- [ ] Fill in valid data:
  - Título: "Artigo de Teste" (< 220 chars)
  - Resumo: "Resumo breve" (< 1000 chars)
  - Corpo: "Conteúdo do artigo" (< 5000 words)
- [ ] Click "Publicar"
- [ ] **Expected**: Success message "Conteúdo publicado!"

## 2. User Pagination

### Test 2.1: Pagination Style
- [ ] Navigate to Admin Panel → Geral tab
- [ ] Scroll to user list
- [ ] **Expected**: See numbered pagination buttons [← Anterior] [1] [2] [3] ... [Próxima →]
- [ ] **Expected**: Current page highlighted with purple background

### Test 2.2: Page Navigation
- [ ] Click on page number 2
- [ ] **Expected**: Navigate to page 2, button [2] is highlighted
- [ ] Click [← Anterior]
- [ ] **Expected**: Navigate to page 1
- [ ] Click [Próxima →]
- [ ] **Expected**: Navigate to next page

### Test 2.3: Consistency with Moderation
- [ ] Compare user pagination with moderation pagination (blocked words section)
- [ ] **Expected**: Same visual style (pag-btn class)

## 3. Analytics Graphs

### Test 3.1: Analytics Tab Access
- [ ] Navigate to Admin Panel → Analytics tab
- [ ] **Expected**: See 4 graphs in grid layout

### Test 3.2: User Growth Chart (existing)
- [ ] **Expected**: Line chart with user growth over time
- [ ] **Expected**: Chart title "Crescimento de Usuáries"
- [ ] **Expected**: Purple color (#9B5DE5)

### Test 3.3: Content Creation Chart (NEW)
- [ ] **Expected**: Bar chart showing content by type
- [ ] **Expected**: Chart title "Criação de Conteúdo Edu"
- [ ] **Expected**: Green color (#48bb78)
- [ ] **Expected**: Categories: Artigo, Apostila, Video, Podcast, etc.

### Test 3.4: Posts Chart (NEW)
- [ ] **Expected**: Line chart showing posts in last 7 days
- [ ] **Expected**: Chart title "Posts Criados (últimos 7 dias)"
- [ ] **Expected**: Orange color (#f6ad55)

### Test 3.5: Activity Chart (NEW)
- [ ] **Expected**: Doughnut chart with activity breakdown
- [ ] **Expected**: Chart title "Atividade por Tipo"
- [ ] **Expected**: Multiple colors for different activity types
- [ ] **Expected**: Categories: Posts, Conteúdo Edu, Comentários, Usuários

### Test 3.6: Data Validation
- [ ] Open browser DevTools → Network tab
- [ ] Reload Analytics tab
- [ ] **Expected**: 4 successful API calls:
  - `/admin/stats/users.json`
  - `/admin/stats/content.json`
  - `/admin/stats/posts.json`
  - `/admin/stats/activity.json`
- [ ] Check response format for each:
  - **Expected**: JSON with `labels` and `data` arrays

## 4. 3-Dot Button Styling

### Test 4.1: Visual Appearance
- [ ] Open Admin Panel
- [ ] Look at top-right corner button (3 dots)
- [ ] **Expected**: Subtle transparent button with blur effect
- [ ] **Expected**: NOT a purple gradient
- [ ] **Expected**: Size approximately 42x42px
- [ ] **Expected**: Dots are white/light colored

### Test 4.2: Hover Effect
- [ ] Hover over 3-dot button
- [ ] **Expected**: Slight background color change
- [ ] **Expected**: NO movement/transform effect
- [ ] **Expected**: Smooth transition

### Test 4.3: Click Behavior
- [ ] Click 3-dot button
- [ ] **Expected**: Menu appears with options:
  - Início público
  - Perfil
  - Sair
- [ ] Click outside menu
- [ ] **Expected**: Menu closes

### Test 4.4: Comparison with Public Pages
- [ ] Navigate to a public page (e.g., /artigos)
- [ ] Compare header style with admin dashboard
- [ ] **Expected**: Similar transparent/blur aesthetic
- [ ] **Expected**: Consistent design pattern

## 5. Error Handling

### Test 5.1: Network Error
- [ ] Disconnect internet (or block requests in DevTools)
- [ ] Try to load Analytics tab
- [ ] **Expected**: Graceful error handling in console
- [ ] **Expected**: Empty charts or error message (no page crash)

### Test 5.2: Invalid Data
- [ ] Mock API to return invalid JSON
- [ ] **Expected**: Console error message
- [ ] **Expected**: Chart doesn't render but page remains functional

## 6. Responsive Design

### Test 6.1: Mobile View
- [ ] Resize browser to mobile width (< 720px)
- [ ] **Expected**: Analytics charts stack vertically
- [ ] **Expected**: Pagination buttons wrap properly
- [ ] **Expected**: 3-dot button remains accessible

### Test 6.2: Tablet View
- [ ] Resize to tablet width (720-1024px)
- [ ] **Expected**: Analytics in 2-column grid
- [ ] **Expected**: All elements visible and functional

## Success Criteria

All tests should pass with:
- ✅ Clear, specific error messages for article posting
- ✅ Consistent pagination across admin sections
- ✅ 4 functioning analytics graphs with real data
- ✅ Simplified 3-dot button matching project style
- ✅ No console errors or warnings
- ✅ Responsive design works on all screen sizes

## Known Limitations

- Charts require Chart.js to load from CDN
- Analytics data depends on database content
- Page numbers in pagination might be many if hundreds of users exist
