# Vercel Configuration Update

## Issue Fixed

Resolved Vercel deployment warning:
```
WARN! Due to `builds` existing in your configuration file, the Build and Development Settings 
defined in your Project Settings will not apply.
```

## What Changed

### Updated `vercel.json`

**Before:**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "api/index.py" }
  ]
}
```

**After:**
```json
{
  "version": 2,
  "rewrites": [
    { "source": "/(.*)", "destination": "/api/index" }
  ]
}
```

## Why This Works

1. **Removed deprecated `builds` field**: Vercel now uses automatic framework detection for Python serverless functions
2. **Used modern `rewrites` instead of `routes`**: The `rewrites` field is the current recommended approach for routing
3. **Simplified configuration**: Vercel automatically detects Python files in the `api/` directory and builds them appropriately
4. **Respects Project Settings**: Without the `builds` field, the Build and Development Settings in the Vercel Project Settings will now be applied

## How Vercel Handles This

- **Automatic Detection**: Vercel automatically detects `api/index.py` as a Python serverless function
- **Runtime**: Python runtime version is detected from the environment or can be specified in Project Settings
- **Build Process**: Vercel automatically installs dependencies from `requirements.txt`
- **Routing**: The `rewrites` configuration routes all requests to `/api/index`

## Benefits

✅ **No more warnings**: Build settings work as expected
✅ **Cleaner configuration**: Less boilerplate in `vercel.json`
✅ **Better maintainability**: Follows current Vercel best practices
✅ **Flexible settings**: Can now use Vercel Project Settings for build configuration

## Testing

All existing tests pass:
- ✅ App import works
- ✅ Health endpoint functional
- ✅ Pillow 10+ compatibility maintained
- ✅ Read-only filesystem handling works

## Deployment

The application will deploy normally on Vercel with this configuration. The change is backward compatible and does not affect functionality.

## References

- [Vercel Configuration Documentation](https://vercel.com/docs/projects/project-configuration)
- [Vercel Python Runtime](https://vercel.com/docs/functions/runtimes/python)
- [Vercel Rewrites](https://vercel.com/docs/projects/project-configuration#rewrites)
