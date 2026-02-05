# Fix: Like Button State on Post Page Reload

## Problem Statement

When reloading an individual post page (`/post.html?id=X`), the like button always appeared as "Curtir" (not liked), even if the user had already liked the post. The like was correctly saved in the database, but the UI didn't reflect the correct state.

## Root Cause

1. **Backend**: The GET endpoint at `functions/api/posts/[id].ts` was not checking if the current user had liked the post
2. **Frontend**: The `renderPost()` function in `public/post.html` always rendered the button in the "not liked" state

## Solution Implemented

### Backend Changes (`functions/api/posts/[id].ts`)

**Added user like check in GET endpoint:**
```typescript
// Check if the current user has liked this post (if authenticated)
let userLiked = false;
const user = data.user as User | null;
if (user && user.id) {
  try {
    const { results: likeCheck } = await env.DB.prepare(
      'SELECT 1 FROM post_likes WHERE post_id = ? AND user_id = ?'
    ).bind(postId, user.id).all();
    userLiked = likeCheck && likeCheck.length > 0;
  } catch (e) {
    // Error checking likes, keep userLiked = false
    console.error('[posts/id] GET - Error checking user like:', e);
  }
}

return new Response(JSON.stringify({ 
  success: true, 
  data: { 
    post,
    userLiked  // ← Added this property
  } 
}), {
  headers: { 'Content-Type': 'application/json' }
});
```

**Key features:**
- Uses authenticated user from middleware context (`data.user`)
- Queries `post_likes` table to check if user has liked the post
- Gracefully handles unauthenticated users (returns `userLiked: false`)
- Handles database errors without breaking the response

### Frontend Changes (`public/post.html`)

**1. Modified `loadPost()` to extract `userLiked`:**
```javascript
async function loadPost(postId) {
  try {
    const response = await fetch(`/api/posts/${postId}`);
    if (!response.ok) {
      throw new Error('Post não encontrado');
    }
    
    const data = await response.json();
    const post = data.data?.post || data.post;
    const userLiked = data.data?.userLiked ?? false;  // ← Added extraction
    
    if (!post) {
      throw new Error('Post não encontrado');
    }
    
    renderPost(post, userLiked);  // ← Pass userLiked to render
    loadComments(postId);
  } catch (error) {
    console.error('Erro ao carregar post:', error);
    showError(error.message || 'Erro ao carregar post');
    document.getElementById('postContainer').innerHTML = '';
  }
}
```

**2. Updated `renderPost()` to accept and use `userLiked`:**
```javascript
function renderPost(post, userLiked = false) {  // ← Added parameter
  // ... existing code ...
  
  // Set like button state based on userLiked
  const likeButtonClass = userLiked ? 'interaction-btn like-btn active' : 'interaction-btn like-btn';
  const likeIcon = userLiked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
  const likeText = userLiked ? 'Curtido' : 'Curtir';
  
  const postHTML = `
    <div class="post-card">
      <!-- ... -->
      <div class="post-interactions">
        <button class="${likeButtonClass}" onclick="likePost()">
          <i class="${likeIcon}"></i> <span class="like-text">${likeText}</span>
        </button>
        <!-- ... -->
      </div>
    </div>
  `;
  
  document.getElementById('postContainer').innerHTML = postHTML;
  document.getElementById('commentsSection').style.display = 'block';
}
```

**Key features:**
- Uses nullish coalescing operator (`??`) for correct fallback behavior
- Conditionally sets button class (adds `active` when liked)
- Uses filled heart icon (`fa-solid fa-heart`) when liked
- Changes text to "Curtido" when liked
- Added `.like-text` span wrapper for consistency with feed.html

### Additional Improvements

1. **Removed unused imports** from `functions/api/posts/[id].ts` to fix TypeScript conflicts
2. **Fixed misleading comment** in error handling to accurately describe the catch block
3. **Improved consistency** by using the same `.like-text` span pattern as in feed.html

## Expected Behavior

✅ **Authenticated user who has liked a post:**
- Button shows "Curtido" with filled heart icon (red when active)
- Button has `active` class for styling

✅ **Authenticated user who hasn't liked a post:**
- Button shows "Curtir" with empty heart icon
- Button does not have `active` class

✅ **Unauthenticated user:**
- Button shows "Curtir" with empty heart icon
- Button does not have `active` class

✅ **State persistence:**
- Like state persists correctly after page reload
- Consistent with feed.html behavior

## Testing Checklist

- [ ] **Authenticated user with liked post**
  1. Like a post from the feed
  2. Click on the post to view individual post page
  3. Verify button shows "Curtido" with filled heart
  4. Reload the page
  5. Verify button still shows "Curtido" with filled heart

- [ ] **Authenticated user with unliked post**
  1. Find a post you haven't liked
  2. Navigate to individual post page
  3. Verify button shows "Curtir" with empty heart
  4. Reload the page
  5. Verify button still shows "Curtir" with empty heart

- [ ] **Unauthenticated user**
  1. Log out
  2. Navigate to individual post page
  3. Verify button shows "Curtir" with empty heart
  4. Reload the page
  5. Verify button still shows "Curtir" with empty heart

- [ ] **Like/unlike interaction**
  1. On individual post page, click like button
  2. Verify button changes to "Curtido" with filled heart
  3. Reload the page
  4. Verify state is preserved
  5. Click unlike
  6. Verify button changes to "Curtir" with empty heart
  7. Reload the page
  8. Verify state is preserved

## Files Modified

1. `functions/api/posts/[id].ts` - Added `userLiked` check in GET endpoint
2. `public/post.html` - Updated `loadPost()` and `renderPost()` to handle like state

## Security Considerations

- ✅ No SQL injection risk (using parameterized queries)
- ✅ No XSS vulnerabilities (proper escaping in place)
- ✅ No authentication bypass (relies on existing middleware)
- ✅ Graceful error handling without exposing sensitive information
- ✅ CodeQL security scan passed

## Deployment Notes

- No database migrations required (uses existing `post_likes` table)
- No environment variable changes needed
- Backward compatible with existing data
- No breaking changes to API contracts

## Related Issues

This fix ensures consistency between the feed (`feed.html`) and individual post page (`post.html`) in terms of like button state persistence after page reload.
