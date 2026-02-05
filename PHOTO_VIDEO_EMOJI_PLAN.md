# Implementation Plan: Photo/Video/Emoji Features

## Overview
Add support for photos, videos, and emojis in posts to enhance user engagement and content creation.

## Current State Analysis

### Existing Infrastructure
✅ **Cloudflare R2 Storage** - Already configured for file uploads
✅ **Post Model** - Has content field, can be extended for media
✅ **Feed UI** - Can display posts, needs media preview support
✅ **API Endpoints** - Posts API exists, needs media upload support

### Storage Configuration (from README)
- Cloudflare R2 bucket configured
- Environment variables set for R2 access
- Helper functions exist in `gramatike_app/utils/storage.py` (for Flask backend)

## Feature Breakdown

### 1. Emoji Support 🎨
**Priority:** HIGH (Easiest to implement)
**Complexity:** LOW

#### Implementation Steps:
1. **Add Emoji Picker**
   - Option A: Use emoji-picker-element (Web Component, ~40KB)
   - Option B: Use native emoji keyboard (OS-dependent)
   - Option C: Build simple custom picker with common emojis
   
2. **UI Changes**
   - Add emoji button to post creation form
   - Display emoji picker on button click
   - Insert emoji at cursor position in textarea

3. **Files to Modify:**
   - `public/feed.html` - Add emoji picker UI
   - No backend changes needed (emojis are just text)

#### Estimated Time: 2-3 hours

---

### 2. Photo Upload 📷
**Priority:** HIGH
**Complexity:** MEDIUM

#### Implementation Steps:

1. **Frontend Changes**
   - Add file input for image selection
   - Add image preview before posting
   - Add image removal button
   - Show upload progress
   - Display uploaded images in posts
   - Add lightbox for full-size view

2. **Backend Changes**
   - Update Posts API to accept multipart/form-data
   - Implement image upload to Cloudflare R2
   - Validate image format (JPEG, PNG, GIF, WebP)
   - Validate image size (max 10MB)
   - Generate thumbnails (optional)
   - Update posts table schema

3. **Database Schema Changes**
   ```sql
   ALTER TABLE posts ADD COLUMN media_type TEXT; -- 'image', 'video', null
   ALTER TABLE posts ADD COLUMN media_url TEXT;
   ALTER TABLE posts ADD COLUMN media_thumbnail_url TEXT;
   ```

4. **Files to Modify:**
   - `db/schema.sql` - Add media columns
   - `db/migrations/add_media_support.sql` - New migration
   - `functions/api/posts/index.ts` - Handle image upload
   - `public/feed.html` - UI for upload and display

#### Estimated Time: 6-8 hours

---

### 3. Video Upload 🎥
**Priority:** MEDIUM
**Complexity:** HIGH

#### Implementation Steps:

1. **Frontend Changes**
   - Add video file input
   - Add video preview player
   - Show upload progress (videos are larger)
   - Display video player in feed
   - Add video controls (play/pause/volume)

2. **Backend Changes**
   - Accept video files (MP4, WebM, MOV)
   - Validate video size (max 100MB)
   - Generate video thumbnail
   - Upload to Cloudflare R2
   - Consider Cloudflare Stream for video hosting (better performance)

3. **Files to Modify:**
   - Same as photo upload
   - May need `functions/api/posts/upload-video.ts` (separate endpoint)

#### Estimated Time: 8-10 hours

---

## Detailed Implementation: Phase 1 - Emoji Support

### Step 1: Choose Emoji Picker Library

**Recommended: emoji-picker-element**
- Modern Web Component
- No framework dependencies
- Good performance
- Accessibility support

```html
<!-- Add to feed.html -->
<script type="module">
  import 'https://cdn.jsdelivr.net/npm/emoji-picker-element@^1/index.js';
</script>
```

### Step 2: Update Post Creation Form

Add emoji button to post form in `public/feed.html`:

```html
<div class="post-form-card">
  <textarea id="postContent" placeholder="O que você está pensando?"></textarea>
  <div class="post-form-actions">
    <button id="emojiBtn" type="button" class="emoji-btn">
      <i class="far fa-smile"></i> Emoji
    </button>
    <button id="postBtn" class="post-btn">Publicar</button>
  </div>
  <div id="emojiPickerContainer" style="display: none;">
    <emoji-picker></emoji-picker>
  </div>
</div>
```

### Step 3: Add Emoji Picker Logic

```javascript
// Toggle emoji picker
const emojiBtn = document.getElementById('emojiBtn');
const emojiPicker = document.querySelector('emoji-picker');
const postContent = document.getElementById('postContent');

emojiBtn.addEventListener('click', () => {
  const container = document.getElementById('emojiPickerContainer');
  container.style.display = container.style.display === 'none' ? 'block' : 'none';
});

// Insert emoji at cursor
emojiPicker.addEventListener('emoji-click', event => {
  const emoji = event.detail.unicode;
  const start = postContent.selectionStart;
  const end = postContent.selectionEnd;
  const text = postContent.value;
  
  postContent.value = text.substring(0, start) + emoji + text.substring(end);
  postContent.selectionStart = postContent.selectionEnd = start + emoji.length;
  postContent.focus();
});
```

### Step 4: Add Styling

```css
.emoji-btn {
  background: transparent;
  border: none;
  padding: 8px 16px;
  cursor: pointer;
  color: var(--roxo);
  border-radius: 8px;
  transition: background 0.2s;
}

.emoji-btn:hover {
  background: var(--roxo-super-claro);
}

#emojiPickerContainer {
  position: relative;
  margin-top: 10px;
}

emoji-picker {
  width: 100%;
  max-width: 350px;
  --border-radius: 12px;
  --category-emoji-size: 1.5rem;
}
```

---

## Detailed Implementation: Phase 2 - Photo Upload

### Step 1: Update Database Schema

Create `db/migrations/add_media_support.sql`:

```sql
-- Add media support to posts table
ALTER TABLE posts ADD COLUMN media_type TEXT;
ALTER TABLE posts ADD COLUMN media_url TEXT;
ALTER TABLE posts ADD COLUMN media_thumbnail_url TEXT;

-- Index for media posts
CREATE INDEX idx_posts_media_type ON posts(media_type);
```

Update `db/schema.sql` to include these columns in fresh installations.

### Step 2: Update Post Creation Form

```html
<div class="post-form-card">
  <textarea id="postContent" placeholder="O que você está pensando?"></textarea>
  
  <!-- Image Preview -->
  <div id="imagePreview" style="display: none;">
    <img id="previewImg" src="" alt="Preview">
    <button id="removeImage" class="remove-image-btn">×</button>
  </div>
  
  <div class="post-form-actions">
    <label for="imageInput" class="media-btn">
      <i class="far fa-image"></i> Foto
    </label>
    <input type="file" id="imageInput" accept="image/*" style="display: none;">
    
    <button id="emojiBtn" type="button" class="emoji-btn">
      <i class="far fa-smile"></i> Emoji
    </button>
    
    <button id="postBtn" class="post-btn">Publicar</button>
  </div>
</div>
```

### Step 3: Add Image Upload Logic

```javascript
let selectedImage = null;

// Handle image selection
document.getElementById('imageInput').addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (!file) return;
  
  // Validate file type
  if (!file.type.startsWith('image/')) {
    alert('Por favor, selecione uma imagem válida');
    return;
  }
  
  // Validate file size (10MB max)
  if (file.size > 10 * 1024 * 1024) {
    alert('Imagem muito grande! Máximo 10MB');
    return;
  }
  
  selectedImage = file;
  
  // Show preview
  const reader = new FileReader();
  reader.onload = (e) => {
    document.getElementById('previewImg').src = e.target.result;
    document.getElementById('imagePreview').style.display = 'block';
  };
  reader.readAsDataURL(file);
});

// Remove image
document.getElementById('removeImage').addEventListener('click', () => {
  selectedImage = null;
  document.getElementById('imagePreview').style.display = 'none';
  document.getElementById('imageInput').value = '';
});

// Update post creation to handle images
async function createPostWithMedia(content, image) {
  const formData = new FormData();
  formData.append('content', content);
  if (image) {
    formData.append('image', image);
  }
  
  const response = await fetch('/api/posts', {
    method: 'POST',
    body: formData
  });
  
  // ... handle response
}
```

### Step 4: Update Backend API

Modify `functions/api/posts/index.ts`:

```typescript
export const onRequestPost: PagesFunction<{ DB: any, R2_BUCKET: any }> = async ({ request, env, data }) => {
  try {
    const user = data.user as User | null;
    if (!user) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Não autorizado'
      }), { status: 401, headers: { 'Content-Type': 'application/json' }});
    }
    
    const formData = await request.formData();
    const content = formData.get('content') as string;
    const image = formData.get('image') as File | null;
    
    let mediaUrl = null;
    let mediaThumbnailUrl = null;
    let mediaType = null;
    
    // Handle image upload
    if (image) {
      // Generate unique filename
      const timestamp = Date.now();
      const filename = `posts/${user.id}/${timestamp}_${image.name}`;
      
      // Upload to R2
      await env.R2_BUCKET.put(filename, image.stream(), {
        httpMetadata: {
          contentType: image.type
        }
      });
      
      // Generate public URL
      mediaUrl = `https://your-r2-bucket-url/${filename}`;
      mediaType = 'image';
    }
    
    // Create post with media
    const { success, meta } = await env.DB.prepare(
      `INSERT INTO posts (user_id, content, media_type, media_url, likes, comments) 
       VALUES (?, ?, ?, ?, 0, 0)`
    ).bind(user.id, content, mediaType, mediaUrl).run();
    
    // ... rest of the code
  }
};
```

### Step 5: Display Images in Feed

Update `createPostElement()` in `public/feed.html`:

```javascript
function createPostElement(post) {
  // ... existing code ...
  
  let mediaHTML = '';
  if (post.media_type === 'image' && post.media_url) {
    mediaHTML = `
      <div class="post-media">
        <img src="${post.media_url}" alt="Post image" onclick="openLightbox('${post.media_url}')">
      </div>
    `;
  }
  
  postElement.innerHTML = `
    <div class="post-header">...</div>
    <div class="post-content">${content}</div>
    ${mediaHTML}
    ${likesText}
    <div class="post-interactions">...</div>
  `;
  
  return postElement;
}
```

### Step 6: Add Lightbox for Full-Size Images

```html
<!-- Add to feed.html -->
<div id="lightbox" class="lightbox" onclick="closeLightbox()">
  <span class="lightbox-close">&times;</span>
  <img class="lightbox-content" id="lightboxImg">
</div>
```

```javascript
function openLightbox(imageUrl) {
  document.getElementById('lightbox').style.display = 'block';
  document.getElementById('lightboxImg').src = imageUrl;
}

function closeLightbox() {
  document.getElementById('lightbox').style.display = 'none';
}
```

---

## Implementation Timeline

### Week 1: Emoji Support
- Day 1-2: Implement emoji picker
- Day 3: Testing and polish

### Week 2: Photo Upload
- Day 1-2: Frontend UI and preview
- Day 3-4: Backend upload to R2
- Day 5: Display in feed + lightbox

### Week 3: Video Upload (Optional)
- Day 1-2: Frontend video upload
- Day 3-4: Backend video processing
- Day 5: Video player in feed

---

## Testing Checklist

### Emoji Support
- [ ] Emoji picker opens/closes correctly
- [ ] Emojis insert at cursor position
- [ ] Multiple emojis can be added
- [ ] Works on mobile devices
- [ ] Emojis display correctly in feed

### Photo Upload
- [ ] File picker opens
- [ ] Image preview shows correctly
- [ ] Invalid files rejected
- [ ] Large files rejected
- [ ] Upload progress shown
- [ ] Image displays in feed
- [ ] Lightbox works
- [ ] Mobile responsive

### Video Upload
- [ ] Video preview works
- [ ] Video uploads to R2
- [ ] Video player works in feed
- [ ] Controls functional
- [ ] Mobile compatible

---

## Dependencies

### Frontend Libraries
- `emoji-picker-element` - Emoji picker
- (Optional) `uppy` - File upload UI
- (Optional) `plyr` - Video player

### Backend
- Cloudflare R2 - Already configured
- (Optional) Cloudflare Stream - For video hosting

---

## Security Considerations

1. **File Validation**
   - Validate MIME types
   - Check file signatures (magic numbers)
   - Limit file sizes
   - Sanitize filenames

2. **Storage Security**
   - Use unique filenames (prevent overwrite)
   - Implement rate limiting
   - Set upload quotas per user
   - Scan for malware (optional)

3. **Privacy**
   - User owns their uploads
   - Delete media when post deleted
   - GDPR compliance (delete on request)

---

## Next Steps

Ready to begin implementation? Choose which feature to implement first:

1. ✅ **Emoji Support** (Recommended first - easiest, high impact)
2. **Photo Upload** (Second - core feature)
3. **Video Upload** (Third - advanced feature)

Let me know which feature to start with!
