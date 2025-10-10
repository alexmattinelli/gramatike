# Testing Guide - Mobile and Education Improvements

## 🧪 Manual Testing Checklist

### Mobile Post Cards (< 980px)

#### Test 1: Card Width on Mobile
- [ ] Open the main feed on a mobile device or browser DevTools mobile view
- [ ] Verify post cards extend slightly beyond the normal container (full-bleed effect)
- [ ] Cards should have `margin: 0 -0.3rem 1.8rem` on mobile
- [ ] Visual: Cards look wider and more immersive

#### Test 2: Action Button Sizes
- [ ] Check Like button (❤️ Curtir / ❤️ Curtido)
- [ ] Check Comment button (💬 Comentar)
- [ ] Verify buttons are smaller with reduced padding
- [ ] Expected sizes:
  - Padding: `.35rem .7rem` (was `.45rem .9rem`)
  - Font size: `.72rem` (was `.8rem`)
  - Gap: `.25rem` (was `.35rem`)

#### Test 3: Menu Button Size
- [ ] Find the three-dot menu button (⋯) on posts
- [ ] Verify it's more compact (28px × 28px, was 34px × 34px)
- [ ] Button should still be easily tappable

### Education Feed Pagination

#### Test 1: Load Education Page
- [ ] Navigate to `/educacao`
- [ ] Verify only 3 items are displayed initially
- [ ] Check pagination controls appear at the bottom

#### Test 2: Pagination Controls
- [ ] Verify "← Anterior" button is hidden on first page
- [ ] Check numbered page buttons appear (1, 2, 3...)
- [ ] Current page should be highlighted in purple (#9B5DE5)
- [ ] Verify "Próximo →" button is hidden on last page

#### Test 3: Page Navigation
- [ ] Click "Próximo →" button
- [ ] Verify page changes to page 2
- [ ] Check exactly 3 new items are displayed
- [ ] Verify page scrolls to top smoothly
- [ ] Click on a numbered page button
- [ ] Verify correct page loads

#### Test 4: Search with Pagination
- [ ] Enter a search term in the education search box
- [ ] Verify results are paginated (3 per page)
- [ ] Check pagination updates with search results
- [ ] Clear search, verify pagination resets

### Menu Dropdown in Education

#### Test 1: Menu Button Display
- [ ] Navigate to `/educacao` as an admin user
- [ ] Verify "Menu" button appears in top-right corner
- [ ] Button should have hamburger icon (3 lines) + "Menu" text
- [ ] Button should have semi-transparent white background

#### Test 2: Menu Dropdown
- [ ] Click "Menu" button
- [ ] Verify dropdown opens below the button
- [ ] Check all 5 options are visible:
  - 📑 Artigos (with document icon)
  - 🧠 Exercícios (with star icon)
  - 📚 Apostilas (with book icon)
  - 🎲 Dinâmicas (with globe icon)
  - 🛠️ Painel (with grid icon)

#### Test 3: Menu Interactions
- [ ] Hover over each menu item
- [ ] Verify background changes to light purple (#f7f2ff)
- [ ] Click on "Artigos"
- [ ] Verify navigation to `/artigos`
- [ ] Go back and test other menu items
- [ ] Verify all links work correctly

#### Test 4: Menu Close Behavior
- [ ] Open menu dropdown
- [ ] Click outside the menu (on the page background)
- [ ] Verify menu closes automatically
- [ ] Open menu again
- [ ] Click menu button again
- [ ] Verify menu closes (toggle behavior)

#### Test 5: Mobile Menu (< 480px)
- [ ] Resize browser to < 480px width
- [ ] Open menu dropdown
- [ ] Verify menu is responsive:
  - Min-width: 180px
  - Smaller font size: .7rem
  - Smaller padding: 9px 12px
  - Smaller icons: 16px × 16px

### API Pagination Testing

#### Test 1: API Request
- [ ] Open browser DevTools Network tab
- [ ] Navigate to `/educacao`
- [ ] Find the API request to `/api/gramatike/search`
- [ ] Verify query parameters:
  - `page=1`
  - `per_page=3`
  - `include_edu=0`

#### Test 2: API Response
- [ ] Check the JSON response structure:
  ```json
  {
    "items": [...],  // Array of 3 items
    "total": N,      // Total number of items
    "page": 1,       // Current page
    "per_page": 3,   // Items per page
    "total_pages": N // Total pages
  }
  ```
- [ ] Verify `items` array has exactly 3 items (or fewer on last page)
- [ ] Check `total_pages` matches expected count

#### Test 3: Page Changes
- [ ] Click "Próximo →"
- [ ] Check network request has `page=2`
- [ ] Verify response has `page: 2`
- [ ] Verify `items` array contains next 3 items

### Responsive Design Testing

#### Desktop (> 980px)
- [ ] Cards: Standard padding, no negative margin
- [ ] Buttons: Normal size (larger)
- [ ] Menu: Visible if admin
- [ ] Bottom nav: Hidden
- [ ] Pagination: Visible and functional

#### Tablet (768px - 980px)
- [ ] Cards: Mobile styles applied
- [ ] Buttons: Smaller
- [ ] Menu: Visible if admin
- [ ] Bottom nav: Visible
- [ ] Pagination: Visible and functional

#### Mobile (< 768px)
- [ ] Cards: Wide with negative margin
- [ ] Buttons: Smallest size
- [ ] Menu: Compact dropdown if admin
- [ ] Bottom nav: Visible
- [ ] Pagination: Visible and functional

#### Small Mobile (< 480px)
- [ ] Menu dropdown: Responsive size (180px min-width)
- [ ] Menu items: Smaller padding and font
- [ ] Menu icons: 16px × 16px
- [ ] All features still accessible

### Browser Compatibility

#### Test on:
- [ ] Chrome/Edge (desktop)
- [ ] Safari (desktop)
- [ ] Firefox (desktop)
- [ ] Chrome (mobile)
- [ ] Safari (iOS)
- [ ] Samsung Internet (Android)

### Accessibility Testing

#### Keyboard Navigation
- [ ] Tab to menu button
- [ ] Press Enter to open menu
- [ ] Tab through menu items
- [ ] Press Enter on a menu item to navigate

#### Screen Reader
- [ ] Menu button has clear label
- [ ] Menu items are announced correctly
- [ ] Pagination buttons are descriptive

## 🐛 Known Issues / Edge Cases

### Potential Issues to Watch For:

1. **Empty Results**
   - [ ] When no items match search, verify "Nada encontrado" message
   - [ ] Pagination should hide when no results

2. **Single Page Results**
   - [ ] When total items ≤ 3, pagination should not appear
   - [ ] Or show single page without navigation

3. **Menu on Non-Admin**
   - [ ] Regular users should not see menu button
   - [ ] Only admins and superadmins see it

4. **Menu Z-Index**
   - [ ] Menu should appear above other elements
   - [ ] Check z-index: 100

5. **Mobile Card Overflow**
   - [ ] Negative margin shouldn't cause horizontal scroll
   - [ ] Container should handle overflow properly

## 📸 Visual Verification

### Screenshots to Take:

1. **Desktop Feed**
   - [ ] Normal post cards (not mobile)
   - [ ] Standard button sizes

2. **Mobile Feed (< 980px)**
   - [ ] Wider post cards
   - [ ] Smaller buttons (like, comment)
   - [ ] Compact menu button

3. **Education Page**
   - [ ] First page with 3 items
   - [ ] Pagination controls visible

4. **Pagination States**
   - [ ] First page (no Previous)
   - [ ] Middle page (both Previous and Next)
   - [ ] Last page (no Next)

5. **Menu States**
   - [ ] Menu button closed
   - [ ] Menu dropdown open
   - [ ] Menu item hovered (purple background)

6. **Mobile Menu (< 480px)**
   - [ ] Compact menu dropdown
   - [ ] Smaller icons and text

## ✅ Success Criteria

### Mobile Posts:
✅ Cards are visually wider on mobile  
✅ Buttons are smaller and less cluttered  
✅ Layout is more immersive  
✅ No horizontal scroll  

### Education Pagination:
✅ Exactly 3 items per page  
✅ Numbered pagination controls  
✅ Matches admin panel style  
✅ Smooth page transitions  
✅ Scroll to top on page change  

### Menu Dropdown:
✅ Hamburger icon with "Menu" label  
✅ All 5 options with icons  
✅ Purple icon colors (#9B5DE5)  
✅ Hover effects work  
✅ Click outside closes menu  
✅ Responsive on mobile  

### API:
✅ Pagination parameters work  
✅ Response includes metadata  
✅ Items array is correctly sliced  
✅ Page navigation is accurate  

## 🚀 Deployment Verification

After deploying to production:

1. [ ] Verify all changes are live
2. [ ] Test on real mobile devices
3. [ ] Check performance (pagination improves load time)
4. [ ] Monitor for any console errors
5. [ ] Gather user feedback

## 📝 Rollback Plan

If issues occur:

1. Revert commits:
   ```bash
   git revert 36d2f76  # Visual docs
   git revert b1ee1f9  # Responsive menu
   git revert 73a5ad3  # Main changes
   ```

2. Or merge previous stable branch

3. Redeploy

## 🔗 Related Documentation

- [MOBILE_EDUCATION_IMPROVEMENTS.md](MOBILE_EDUCATION_IMPROVEMENTS.md) - Implementation details
- [MOBILE_EDU_VISUAL_CHANGES.md](MOBILE_EDU_VISUAL_CHANGES.md) - Visual code examples
- [MOBILE_TESTING_CHECKLIST.md](MOBILE_TESTING_CHECKLIST.md) - Previous mobile tests

---

**Last Updated**: 2025-10-10  
**Changes By**: GitHub Copilot  
**Status**: Ready for Testing ✅
