# Fix: Responsive Posts Per Page in Education Section

## Problem Statement (Portuguese)
> aqui não era para ser assim:Desktop: Paginação deveria ter limite de 10 números de página
> Mobile: Paginação deveria ter limite de 3 números de página. Era para ser Limites de posts por pagina no educação. !0 para pc e 3 para mobille

**Translation**: This shouldn't be like this: Desktop: Pagination should have a limit of 10 page numbers, Mobile: Pagination should have a limit of 3 page numbers. It was supposed to be limits of posts per page in education. 10 for pc and 3 for mobile.

## Issue Analysis

The issue was about **posts per page**, not just the number of page buttons displayed. The previous implementation had:
- ❌ Fixed 3 posts per page for ALL devices
- ✅ Already had responsive page number display (3 numbers mobile, 10 numbers desktop)

## Solution Implemented

Changed the education section (`gramatike_edu.html`) to use responsive posts per page:

### Before:
```javascript
const perPage = 3; // Show 3 items per page
```

### After:
```javascript
// Dynamic posts per page based on screen size
function getPerPage() {
  const isMobile = window.innerWidth <= 980;
  return isMobile ? 3 : 10;
}

async function search(q, page = 1){
  try {
    const perPage = getPerPage();
    const resp = await fetch(`/api/gramatike/search?q=${encodeURIComponent(q||'')}&include_edu=0&page=${page}&per_page=${perPage}`);
    // ...
  }
}
```

## Configuration

| Device Type | Screen Width | Posts Per Page | Page Numbers Displayed |
|-------------|--------------|----------------|------------------------|
| Desktop     | > 980px      | **10 posts**   | Max 10 page numbers    |
| Mobile      | ≤ 980px      | **3 posts**    | Max 3 page numbers     |

## Technical Details

### Breakpoint
- **980px** - Same breakpoint used throughout the application
- Consistent with existing mobile detection logic

### Implementation
1. Created `getPerPage()` function to dynamically calculate posts per page
2. Function checks `window.innerWidth` against 980px breakpoint
3. Returns 10 for desktop, 3 for mobile
4. Called in `search()` function to get current value for API request

### Files Changed
- `gramatike_app/templates/gramatike_edu.html` - Updated pagination logic

## Testing

### Automated Test Results
```
Width (px) | Expected | Actual | Status
-----------|----------|--------|--------
1920       | 10       | 10     | ✓ PASS (Desktop HD)
1440       | 10       | 10     | ✓ PASS (Desktop)
1024       | 10       | 10     | ✓ PASS (Tablet Landscape)
981        | 10       | 10     | ✓ PASS (Just above breakpoint)
980        | 3        | 3      | ✓ PASS (Exactly at breakpoint)
768        | 3        | 3      | ✓ PASS (Tablet Portrait)
480        | 3        | 3      | ✓ PASS (Mobile)
375        | 3        | 3      | ✓ PASS (Small Mobile)

✓ All tests passed!
```

### Manual Testing Checklist
- [ ] Desktop (> 980px): Verify 10 posts displayed per page
- [ ] Mobile (≤ 980px): Verify 3 posts displayed per page
- [ ] Resize browser: Confirm posts per page updates on resize
- [ ] Pagination controls: Verify page numbers update correctly
- [ ] API calls: Confirm correct per_page parameter sent

## User Impact

### Desktop Users
- ✅ See more content (10 posts) without scrolling
- ✅ Fewer page loads needed to browse content
- ✅ More efficient browsing experience

### Mobile Users
- ✅ Cleaner, more focused view (3 posts)
- ✅ Less scrolling per page
- ✅ Optimized for smaller screens

## Related Features

The pagination system has two independent responsive features:

1. **Posts Per Page** (THIS FIX)
   - Desktop: 10 posts
   - Mobile: 3 posts

2. **Page Numbers Displayed** (Already implemented)
   - Desktop: Max 10 page numbers
   - Mobile: Max 3 page numbers

Both use the same 980px breakpoint for consistency.
