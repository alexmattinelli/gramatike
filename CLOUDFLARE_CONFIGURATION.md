# Cloudflare Pages Configuration Guide

## Purpose

This document provides step-by-step instructions for configuring Cloudflare Pages to deploy Gramátike without Python workers compatibility flags.

## Problem Background

After migrating from Python/Flask to TypeScript, Cloudflare Pages was still showing `python_workers` in the compatibility flags, causing "Invalid request body" errors when trying to save build configurations.

## Solution Summary

This PR implements the following changes to ensure Cloudflare Pages deploys correctly:

1. ✅ Updated `package.json` with simplified build script
2. ✅ Created `.nvmrc` to specify Node.js version 20
3. ✅ Created `.github/workflows/deploy.yml` for GitHub Actions deployment
4. ✅ Verified `wrangler.toml` has no `compatibility_flags` (already clean)
5. ✅ Confirmed no Python files in root directory

## Required Manual Configuration in Cloudflare Dashboard

After this PR is merged, you **MUST** configure the Cloudflare Pages settings manually:

### Step-by-Step Instructions

1. **Navigate to Cloudflare Pages Dashboard**
   - Go to https://dash.cloudflare.com/
   - Select your account
   - Go to **Workers & Pages**
   - Click on the **gramatike** project

2. **Open Build Settings**
   - Click on **Settings** tab
   - Scroll down to **Build configuration** section
   - Click **Edit configuration** (or similar button)

3. **Configure Build Settings**

   Set the following values:

   **Build command:**
   ```
   npm run build
   ```

   **Build output directory:**
   ```
   public
   ```

   **Root directory:** (leave empty or set to `/`)

   **Environment variables:** (should already be set, verify these exist)
   - `SECRET_KEY`
   - `MAIL_SERVER`
   - `MAIL_PORT`
   - `MAIL_USERNAME`
   - `MAIL_PASSWORD`
   - `CLOUDFLARE_ACCOUNT_ID`
   - `CLOUDFLARE_R2_ACCESS_KEY_ID`
   - `CLOUDFLARE_R2_SECRET_ACCESS_KEY`
   - `CLOUDFLARE_R2_BUCKET`

4. **Remove Compatibility Flags**

   This is the **most important step**:

   - Find the **Compatibility flags** section
   - If you see `python_workers` or any other flags listed
   - **Delete/remove ALL compatibility flags**
   - The field should be **completely empty**

5. **Save Configuration**
   - Click **Save** or **Update** button
   - Wait for confirmation message

6. **Trigger New Deployment**
   - Go to **Deployments** tab
   - Click **Retry deployment** on the latest deployment
   - OR push a new commit to `main` branch to trigger GitHub Actions workflow

## Expected Results

After completing these steps, Cloudflare Pages will:

- ✅ Not attempt to use Python runtime
- ✅ Not show `python_workers` in compatibility flags
- ✅ Accept build configuration changes without errors
- ✅ Successfully deploy the TypeScript application
- ✅ Use GitHub Actions for automated deployments (when triggered)

## Verification Steps

1. **Check Deployment Logs**
   - Go to **Deployments** tab in Cloudflare Pages
   - Click on the latest deployment
   - Verify logs show:
     - Node.js version 20 being used
     - `npm install` running successfully
     - `npm run build` outputting: "No build needed - static site with Functions"
     - Deployment completing without errors

2. **Test the Application**
   - Visit your Gramátike URL
   - Verify the homepage loads correctly
   - Test user login/registration
   - Test creating/viewing content
   - Check that all features work as expected

3. **Monitor Performance**
   - Check response times (should be fast, ~10-50ms for most requests)
   - Verify no Python-related errors in logs
   - Confirm cold starts are quick (~50-100ms)

## Troubleshooting

### Issue: "Invalid request body" error when saving settings

**Solution:**
- Double-check that compatibility flags field is **completely empty**
- Remove any hidden or trailing characters
- Try clearing browser cache and trying again

### Issue: Deployment fails with "python_workers" error

**Solution:**
- Verify `wrangler.toml` does not contain `compatibility_flags` line
- Ensure `.github/workflows/deploy.yml` exists and is correct
- Check that no `requirements.txt` or `.py` files exist in root directory

### Issue: Build fails with TypeScript errors

**Solution:**
- The build script no longer compiles TypeScript
- TypeScript is only used for development type checking
- Run `npm run typecheck` locally to catch type errors before pushing

### Issue: Functions not working after deployment

**Solution:**
- Verify that `functions/` directory is intact
- Check that `public/` directory contains all static assets
- Ensure environment variables are set in Cloudflare Dashboard
- Review D1 and R2 bindings in `wrangler.toml`

## GitHub Actions Workflow

The `.github/workflows/deploy.yml` file enables automated deployments:

- **Triggers:** Pushes to `main` branch
- **Process:**
  1. Checks out code
  2. Sets up Node.js 20
  3. Installs npm dependencies
  4. Deploys to Cloudflare Pages using `cloudflare/pages-action@v1`

**Required Secrets:**

Ensure these secrets are configured in GitHub repository settings:
- `CLOUDFLARE_API_TOKEN` - API token with Pages:Edit permission
- `CLOUDFLARE_ACCOUNT_ID` - Your Cloudflare account ID

## Alternative: Manual Deployment

If GitHub Actions is not desired, you can deploy manually:

```bash
# Install dependencies
npm install

# Deploy using Wrangler CLI
npm run deploy
```

## Files Modified in This PR

1. **package.json**
   - Updated `build` script to simple echo command
   - Removed compatibility date from `dev` script

2. **.nvmrc** (new file)
   - Specifies Node.js version 20

3. **.github/workflows/deploy.yml** (new file)
   - GitHub Actions workflow for automated deployment

## Additional Notes

- The TypeScript compilation (`tsc`) is no longer part of the build process
- TypeScript is still available for development via `npm run typecheck`
- The application uses Cloudflare Pages Functions (file-based routing in `functions/` directory)
- Static assets are served from `public/` directory
- No build step is needed because TypeScript is only for type checking, not transpilation

## Questions or Issues?

If you encounter any problems after following these steps:

1. Check Cloudflare Pages deployment logs for specific errors
2. Verify all environment variables are set correctly
3. Ensure GitHub secrets are configured (for GitHub Actions)
4. Review this guide and confirm all steps were followed
5. Check `wrangler.toml` for correct D1 and R2 bindings

## Success Criteria

You'll know the configuration is successful when:

- ✅ Cloudflare Pages dashboard shows no compatibility flags
- ✅ Deployments complete successfully without errors
- ✅ Application loads and functions correctly
- ✅ No Python-related errors in logs
- ✅ Response times are fast (TypeScript performance gains)
- ✅ GitHub Actions deploys automatically on push to main (if using workflow)
