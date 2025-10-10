# Visual Guide: Posts Per Page Fix

## Before vs After

### BEFORE (Fixed 3 posts for all devices)
```
Desktop (1920px):
┌─────────────────────────────────┐
│  📱 Education Feed              │
│                                 │
│  ┌─────────────────────────┐   │
│  │ Post 1                  │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │ Post 2                  │   │
│  └─────────────────────────┘   │
│                                 │
│  ┌─────────────────────────┐   │
│  │ Post 3                  │   │
│  └─────────────────────────┘   │
│                                 │
│  [← Ant] [1] [2] [3] ... [Próx →]│
│                                 │
│  ❌ Only 3 posts on large screen│
└─────────────────────────────────┘

Mobile (375px):
┌─────────────────┐
│  📱 Education   │
│                 │
│  ┌───────────┐  │
│  │ Post 1    │  │
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │ Post 2    │  │
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │ Post 3    │  │
│  └───────────┘  │
│                 │
│  [← Ant] [1]... │
│                 │
│  ✓ Correct      │
└─────────────────┘
```

### AFTER (Responsive: 10 posts desktop, 3 posts mobile)
```
Desktop (1920px):
┌─────────────────────────────────────────────┐
│  💻 Education Feed                          │
│                                             │
│  ┌─────────────────────────┐               │
│  │ Post 1                  │               │
│  └─────────────────────────┘               │
│  ┌─────────────────────────┐               │
│  │ Post 2                  │               │
│  └─────────────────────────┘               │
│  ┌─────────────────────────┐               │
│  │ Post 3                  │               │
│  └─────────────────────────┘               │
│  ┌─────────────────────────┐               │
│  │ Post 4                  │               │
│  └─────────────────────────┘               │
│  ┌─────────────────────────┐               │
│  │ Post 5                  │               │
│  └─────────────────────────┘               │
│  ┌─────────────────────────┐               │
│  │ Post 6                  │               │
│  └─────────────────────────┘               │
│  ┌─────────────────────────┐               │
│  │ Post 7                  │               │
│  └─────────────────────────┘               │
│  ┌─────────────────────────┐               │
│  │ Post 8                  │               │
│  └─────────────────────────┘               │
│  ┌─────────────────────────┐               │
│  │ Post 9                  │               │
│  └─────────────────────────┘               │
│  ┌─────────────────────────┐               │
│  │ Post 10                 │               │
│  └─────────────────────────┘               │
│                                             │
│  [← Anterior] [1] [2] [3] ... [Próximo →] │
│                                             │
│  ✅ 10 posts on large screen!              │
└─────────────────────────────────────────────┘

Mobile (375px):
┌─────────────────┐
│  📱 Education   │
│                 │
│  ┌───────────┐  │
│  │ Post 1    │  │
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │ Post 2    │  │
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │ Post 3    │  │
│  └───────────┘  │
│                 │
│  [← Ant] [1]... │
│                 │
│  ✅ Still 3     │
└─────────────────┘
```

## How It Works

### 1. Screen Width Detection
```javascript
function getPerPage() {
  const isMobile = window.innerWidth <= 980;
  return isMobile ? 3 : 10;
}
```

### 2. Dynamic API Call
```javascript
async function search(q, page = 1){
  const perPage = getPerPage();  // ← Gets current value
  const resp = await fetch(`...&per_page=${perPage}`);
  // ...
}
```

### 3. Responsive Behavior

| Screen Width | Device Type | Posts Per Page |
|--------------|-------------|----------------|
| 1920px       | Desktop     | **10** ✅      |
| 1440px       | Desktop     | **10** ✅      |
| 1024px       | Desktop     | **10** ✅      |
| 981px        | Desktop     | **10** ✅      |
| **980px**    | **Mobile**  | **3** ✅       |
| 768px        | Mobile      | **3** ✅       |
| 375px        | Mobile      | **3** ✅       |

## Benefits

### Desktop Users 💻
- **See more content**: 10 posts vs 3 posts
- **Less pagination**: Fewer page clicks needed
- **Better experience**: More content visible at once

### Mobile Users 📱
- **Optimized view**: 3 posts fits well on small screens
- **Less scrolling**: Appropriate amount per page
- **Clean interface**: Not overwhelming

## Code Comparison

### Before ❌
```javascript
const perPage = 3; // Fixed for all devices
```

### After ✅
```javascript
function getPerPage() {
  const isMobile = window.innerWidth <= 980;
  return isMobile ? 3 : 10;
}
```

## Testing Example

When you visit `/educacao`:

1. **Desktop (1400px)**:
   - API call: `/api/gramatike/search?...&per_page=10`
   - Shows 10 posts
   
2. **Mobile (375px)**:
   - API call: `/api/gramatike/search?...&per_page=3`
   - Shows 3 posts

3. **Resize window**:
   - Automatically adjusts on next search/page change
