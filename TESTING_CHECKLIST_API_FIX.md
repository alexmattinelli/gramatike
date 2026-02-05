# API and Like Button Fix - Testing Checklist

## Issues Addressed

### 1. API Error: `/api/users/me` returning 500
**Symptoms:**
- Error: `Error loading profile: Error: Erro ao carregar perfil`
- HTTP 500 Internal Server Error from `/api/users/me`
- User unable to access `meu_perfil.html` page

**Root Cause:**
- API was querying `banned` column which doesn't exist (should be `is_banned`)
- Missing `last_active` and `updated_at` columns that the API tried to update

**Fix:**
- ✅ Updated `functions/api/users/me.ts` to use `is_banned` instead of `banned`
- ✅ Added `last_active` and `updated_at` columns to database schema
- ✅ Created migration file for existing databases

### 2. Like Button Not Persisting
**Symptoms:**
- User likes a post
- After page reload, like button doesn't show as "liked" (not active/highlighted)
- Optimistic UI update works, but state doesn't persist

**Root Cause:**
- Feed page wasn't fetching current user info before loading posts
- `window.currentUserId` was never set when using API (non-server-rendered)
- Posts API only returned top 3 users who liked, not checking if current user liked
- Frontend relied on `liked_by` array which might not include current user

**Fix:**
- ✅ Added `fetchCurrentUser()` to get user info before loading posts
- ✅ Enhanced Posts API to include `user_liked` boolean flag for each post
- ✅ Updated frontend to use `user_liked` flag instead of checking `liked_by` array
- ✅ Added authentication redirect if user not logged in

## Testing Instructions

### Pre-requisites
1. Run database migration:
   ```bash
   npx wrangler d1 execute gramatike --remote --file=./db/migrations/add_missing_columns.sql
   ```

2. Verify columns exist:
   ```bash
   npx wrangler d1 execute gramatike --remote --command="PRAGMA table_info(users);"
   ```

### Test 1: User Profile Loading
1. Navigate to `https://gramatike.com.br/meu_perfil`
2. ✅ **Expected:** Page loads successfully showing user profile
3. ✅ **Expected:** No 500 error in network tab for `/api/users/me`
4. ✅ **Expected:** User information displays correctly

### Test 2: Like Button Immediate Feedback
1. Navigate to feed: `https://gramatike.com.br/feed.html`
2. Find a post that you haven't liked
3. Click the "Curtir" (Like) button
4. ✅ **Expected:** Button immediately becomes active (filled heart icon)
5. ✅ **Expected:** Like count increases by 1
6. ✅ **Expected:** No errors in console

### Test 3: Like Button Persistence
1. Like a post (if not already liked)
2. **Reload the page** (F5 or Ctrl+R)
3. ✅ **Expected:** Liked post still shows as liked (filled heart, active state)
4. ✅ **Expected:** Like count is correct
5. ✅ **Expected:** `window.currentUserId` is set (check in DevTools console)

### Test 4: Unlike Functionality
1. Click a liked post's "Curtir" button again
2. ✅ **Expected:** Button becomes inactive (outline heart icon)
3. ✅ **Expected:** Like count decreases by 1
4. Reload the page
5. ✅ **Expected:** Post still shows as not liked

### Test 5: Multiple Posts
1. Like 3-4 different posts
2. Reload the page
3. ✅ **Expected:** All liked posts show as liked
4. ✅ **Expected:** All non-liked posts show as not liked
5. ✅ **Expected:** Like counts are accurate

### Test 6: Authentication Flow
1. Open feed in incognito/private window (or logout first)
2. Try to access `/feed.html`
3. ✅ **Expected:** Redirect to login page
4. ✅ **Expected:** Toast message: "Por favor, faça login para acessar o feed"

### Test 7: API Response Validation
1. Open DevTools > Network tab
2. Reload feed page
3. Find `/api/users/me` request
4. ✅ **Expected:** Status 200 OK
5. ✅ **Expected:** Response includes `user.id`, `user.username`, etc.

6. Find `/api/posts` request
7. ✅ **Expected:** Status 200 OK
8. ✅ **Expected:** Each post has `user_liked: true/false` field
9. ✅ **Expected:** Posts you liked have `user_liked: true`

## Known Limitations
- The `liked_by` array in posts still only shows top 3 users (for display purposes)
- This is separate from `user_liked` which correctly tracks all users

## Rollback Plan
If issues occur:
1. Revert code changes via git
2. Optionally remove added database columns (see DB_MIGRATION_FEB_2026.md)

## Success Criteria
✅ `/api/users/me` returns 200 OK
✅ User profile page loads without errors
✅ Like button shows correct state on page load
✅ Like button state persists after page reload
✅ Like/unlike functionality works correctly
✅ Authentication properly redirects unauthenticated users
