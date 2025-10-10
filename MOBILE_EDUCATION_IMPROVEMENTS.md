# Mobile and Education Section Improvements

## Summary of Changes

This document outlines the improvements made to the mobile experience and the education section of Gramátike.

## 1. Mobile Post Cards Enhancement

### Changes Made:
- **Wider Cards on Mobile**: Post cards now expand slightly beyond the container margin for a more immersive mobile experience
  - Added negative margin: `margin: 0 -0.3rem 1.8rem;`
  - Adjusted padding: `padding: 1.4rem 1.6rem 1.2rem;`

- **Smaller Action Buttons**: Reduced the size of like, comment, and share buttons for better mobile UX
  - Button padding reduced: `.post-actions button { padding: .35rem .7rem; }`
  - Font size reduced: `font-size: .72rem;`
  - Gap between icon and text reduced: `gap: .25rem;`

- **Smaller Menu Button**: The three-dot post menu button is now more compact
  - Width/height reduced to: `28px x 28px`
  - Font size adjusted to: `.95rem`

### Location:
- File: `gramatike_app/templates/index.html`
- Media query: `@media (max-width: 980px)`

## 2. Education Feed Pagination

### Changes Made:
- **API Enhancement**: Added pagination support to the Gramátike search API
  - New parameters: `page`, `per_page`
  - Returns: `{ items: [], total: N, page: N, per_page: N, total_pages: N }`
  
- **Responsive Items Per Page**: Education feed displays different amounts based on device
  - **UPDATE (Oct 2025)**: Changed to responsive: Desktop 10 posts, Mobile 3 posts
  - Implementation: `getPerPage()` function checks screen width
  - Previous: `const perPage = 3;` (fixed for all devices)

- **Admin-Style Pagination**: Numbered pagination controls with Previous/Next buttons
  - Style matches the admin dashboard pagination
  - Purple (#9B5DE5) buttons with hover effects
  - Current page highlighted with solid purple background
  - Smooth scroll to top when changing pages

### Pagination UI Features:
- Previous button (← Anterior): Shows when not on first page
- Numbered page buttons: All pages displayed
- Next button (Próximo →): Shows when not on last page
- Current page: Highlighted in purple, non-clickable
- Smooth page transitions with scroll to top

### Location:
- API: `gramatike_app/routes/__init__.py` (api_gramatike_search function)
- Frontend: `gramatike_app/templates/gramatike_edu.html` (JavaScript section)
- Styles: `.pag-btn` class added to gramatike_edu.html

## 3. Menu Dropdown Replacement

### Changes Made:
- **Replaced "Painel" Button**: The single "Painel" (Panel) button has been replaced with a comprehensive dropdown menu
  
- **Menu Button Design**: 
  - Icon: Three horizontal lines (hamburger menu)
  - Label: "Menu"
  - Style: Semi-transparent white background with border
  - Position: Top-right corner of education header

- **Dropdown Menu Options** (with icons):
  1. 📑 **Artigos** (Articles) - Document icon
  2. 🧠 **Exercícios** (Exercises) - Star icon
  3. 📚 **Apostilas** (Study Materials) - Book icon
  4. 🎲 **Dinâmicas** (Dynamics) - Globe icon
  5. 🛠️ **Painel** (Panel) - Grid icon

### Menu Features:
- **Click to Toggle**: Opens/closes on button click
- **Click Outside to Close**: Menu automatically closes when clicking elsewhere
- **Hover Effects**: Items highlight in light purple (#f7f2ff) on hover
- **Visual Icons**: Each option has both an emoji and an SVG icon in purple (#9B5DE5)
- **Clean Design**: White background with subtle shadow and rounded corners

### Location:
- File: `gramatike_app/templates/gramatike_edu.html`
- HTML: In the header section (replaces old Painel link)
- JavaScript: `toggleMenu()` function and click-outside handler

## Technical Implementation Details

### API Changes (`routes/__init__.py`)
```python
# Added pagination parameters
page = max(int(request.args.get('page', 1) or 1), 1)
per_page = min(int(request.args.get('per_page', 15) or 15), 40)

# Implemented pagination logic
total = len(items)
total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1
start_idx = (page - 1) * per_page
end_idx = start_idx + per_page
paginated_items = items[start_idx:end_idx]

# Return pagination metadata
return jsonify({
    'items': paginated_items,
    'total': total,
    'page': page,
    'per_page': per_page,
    'total_pages': total_pages
})
```

### Frontend Pagination (`gramatike_edu.html`)
```javascript
// State management
let currentPage = 1;
let totalPages = 1;

// Dynamic posts per page (UPDATE Oct 2025)
function getPerPage() {
  const isMobile = window.innerWidth <= 980;
  return isMobile ? 3 : 10;
}

// Fetch with pagination
async function search(q, page = 1) {
  const perPage = getPerPage();
  const resp = await fetch(`/api/gramatike/search?q=${encodeURIComponent(q||'')}&include_edu=0&page=${page}&per_page=${perPage}`);
  // ...
}

// Render pagination controls
function renderPagination() {
  // Creates Previous, numbered pages, and Next buttons
  // Highlights current page
  // Updates on each search
}

// Page change handler
window.changePage = function(page) {
  search(input.value.trim(), page);
  window.scrollTo({ top: 0, behavior: 'smooth' });
};
```

## User Experience Benefits

### Mobile Users:
- ✅ More immersive card experience with wider posts
- ✅ Easier interaction with appropriately sized buttons
- ✅ Better use of screen real estate
- ✅ Reduced visual clutter with compact controls

### Education Section Users:
- ✅ Easier navigation with paginated content (3 items at a time)
- ✅ Clear page indicators and navigation controls
- ✅ Quick access to all educational resources via dropdown menu
- ✅ Consistent design with admin panel pagination
- ✅ Organized menu with clear categories and visual icons

### Admin Users:
- ✅ All panel functions still accessible
- ✅ Additional quick links to educational sections
- ✅ Consistent navigation experience

## Testing Checklist

- [ ] Mobile view (< 980px): Cards are wider, buttons are smaller
- [ ] Education page: Shows 3 items per page
- [ ] Pagination: Previous/Next buttons work correctly
- [ ] Pagination: Page numbers are clickable and highlight current page
- [ ] Menu dropdown: Opens on click, closes on outside click
- [ ] Menu items: All links navigate correctly
- [ ] Menu hover: Background changes to light purple
- [ ] Responsive: Works on various screen sizes

## Files Modified

1. `gramatike_app/templates/index.html`
   - Added mobile-specific styles for wider cards and smaller buttons

2. `gramatike_app/templates/gramatike_edu.html`
   - Replaced Painel button with Menu dropdown
   - Added dropdown menu HTML with 5 options
   - Updated JavaScript for pagination support
   - Added pagination button styles

3. `gramatike_app/routes/__init__.py`
   - Enhanced API endpoint with pagination support
   - Added page, per_page, total, total_pages to API response

## Design Consistency

All changes maintain the existing Gramátike design language:
- Purple primary color (#9B5DE5)
- Consistent button styles and hover effects
- Rounded corners and smooth transitions
- Clean, modern aesthetic
- Accessible navigation patterns
