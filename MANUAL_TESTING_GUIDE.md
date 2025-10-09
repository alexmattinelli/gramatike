# 🧪 Manual Testing Guide - Notification & Email Fixes

## Pre-requisites

- Application running locally or deployed
- User account with notifications
- SMTP configured for email testing (optional)

---

## Test 1: Notification Badge Persistence

### Steps to Test

1. **Initial State**
   - [ ] Login to the application
   - [ ] Navigate to index page (`/`)
   - [ ] Verify notification badge shows count (e.g., "3")

2. **View Notifications**
   - [ ] Click on the notification bell (🔔)
   - [ ] Panel opens with notification list
   - [ ] After 500ms, badge disappears

3. **Test Persistence - Same Session**
   - [ ] Navigate to another page (e.g., `/edu`)
   - [ ] Navigate back to index (`/`)
   - [ ] ✅ **Expected:** Badge does NOT reappear
   - [ ] Click bell again
   - [ ] ✅ **Expected:** Same notifications shown

4. **Test Persistence - Page Reload**
   - [ ] Press F5 or Ctrl+R to reload page
   - [ ] ✅ **Expected:** Badge does NOT reappear
   - [ ] ✅ **Expected:** localStorage has `notificationsViewed: 'true'`

5. **Test New Notifications**
   - [ ] Have another user like your post or follow you
   - [ ] Reload the page
   - [ ] ✅ **Expected:** Badge reappears with new count
   - [ ] ✅ **Expected:** localStorage has `notificationsViewed` removed

### Debug via Browser Console

```javascript
// Check localStorage state
console.log('Viewed:', localStorage.getItem('notificationsViewed'));
console.log('Hash:', localStorage.getItem('lastNotifHash'));

// Reset state for testing
localStorage.removeItem('notificationsViewed');
localStorage.removeItem('lastNotifHash');
location.reload();
```

---

## Test 2: Email Logo Color

### Method 1: Send Test Email (Requires SMTP)

```bash
# From repository root
python3 scripts/send_test_email.py your-email@example.com
```

1. **Check Email Inbox**
   - [ ] Open received email
   - [ ] Look at header with purple background
   - [ ] ✅ **Expected:** Logo appears WHITE, not purple/dark
   - [ ] ✅ **Expected:** Logo is clearly visible

### Method 2: Visual Inspection (No SMTP needed)

1. **View Generated HTML**
   ```python
   from gramatike_app.utils.emailer import render_test_email
   html = render_test_email("Test", "<p>Test content</p>")
   print(html)
   ```

2. **Check for Filter**
   - [ ] Search for `filter:brightness(0) invert(1)` in output
   - [ ] ✅ **Expected:** Filter present in img tag

3. **Browser Preview**
   - [ ] Save HTML to file: `email_test.html`
   - [ ] Open in browser
   - [ ] ✅ **Expected:** Logo appears white on purple background

### Expected Visual Result

**Before:**
```
┌─────────────────────────┐
│   [Purple/Dark Logo]    │  ← Problem: Dark pixels visible
│      Gramátike          │
└─────────────────────────┘
```

**After:**
```
┌─────────────────────────┐
│   [White Logo]          │  ← Fixed: Pure white logo
│      Gramátike          │
└─────────────────────────┘
```

---

## Test 3: Cross-Browser Compatibility

### Notification Badge Test

Test in multiple browsers:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge

✅ **Expected:** localStorage works in all modern browsers

### Email Logo Test

Test email appearance in:
- [ ] Gmail (web)
- [ ] Outlook.com (web)
- [ ] Yahoo Mail (web)
- [ ] Apple Mail
- [ ] Outlook Desktop (may not support CSS filters)

✅ **Expected:** Logo appears white in most modern email clients

---

## Verification Checklist

### Notifications
- [ ] Badge shows on initial page load with notifications
- [ ] Badge disappears when notifications are opened
- [ ] Badge stays hidden after page reload (same notifications)
- [ ] Badge reappears with new notifications
- [ ] Badge state persists across browser sessions
- [ ] No JavaScript errors in console

### Email Logo
- [ ] Logo appears white on purple background
- [ ] Logo is clearly visible
- [ ] No purple/dark pixels visible
- [ ] Filter CSS is present in HTML source
- [ ] Works in major email clients

---

## Troubleshooting

### Badge Still Reappearing?

1. **Clear localStorage:**
   ```javascript
   localStorage.clear();
   location.reload();
   ```

2. **Check browser console** for errors

3. **Verify code changes:**
   ```bash
   grep -n "localStorage.setItem" gramatike_app/templates/index.html
   grep -n "notificationsViewed" gramatike_app/templates/index.html
   ```

### Logo Not White in Email?

1. **Check email client support** for CSS filters
2. **View HTML source** to confirm filter is present
3. **Test in webmail** (better CSS support than desktop clients)

---

## Success Criteria

✅ All tests pass
✅ No console errors
✅ Visual appearance matches expected results
✅ Works across browsers/email clients
