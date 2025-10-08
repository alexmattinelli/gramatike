# Cache Implementation for CPU Usage Optimization

## Problem
The Gramátike application was consuming 75% of Vercel's free tier CPU usage (4 hours). This document describes the caching solution implemented to reduce CPU usage.

## Solution Overview
Implemented caching for static and semi-static API responses using the existing `web_cache.py` utility. This reduces database queries and CPU usage for frequently accessed endpoints.

## Cached Endpoints

### 1. `/api/palavra-do-dia` - Word of the Day
**Cache Duration:** 1 hour (3600 seconds)
**Cache Key:** `palavra_do_dia:{day_of_year}:{user_id}`

- **Why cache?** The word rotates only once per day, but the endpoint is called frequently
- **User-specific:** Each user gets their own cache to track interaction status
- **Auto-invalidation:** Cache naturally expires daily when the day changes

```python
# Example usage
GET /api/palavra-do-dia
# First request: DB query, cached for 1 hour
# Subsequent requests: Served from cache
```

### 2. `/api/redacao/temas` - Essay Topics
**Cache Duration:** 10 minutes (600 seconds)
**Cache Key:** `redacao_temas:list`

- **Why cache?** Content is static and rarely updated
- **Global cache:** All users see the same content
- **Fresh enough:** 10 minutes balances freshness with performance

```python
# Example usage
GET /api/redacao/temas
# Cached for 10 minutes for all users
```

### 3. `/api/gramatike/search` - Search Feed
**Cache Duration:** 5 minutes (300 seconds)
**Cache Key:** `gramatike_search:q={query}:limit={limit}:edu={include_edu}`

- **Why cache?** Complex queries with joins and sorting
- **Query-specific:** Different queries have separate cache entries
- **Parameters included:** Query string, limit, and edu flag in cache key

```python
# Example usage
GET /api/gramatike/search?q=gramática&limit=15
# Cache key: gramatike_search:q=gramática:limit=15:edu=False

GET /api/gramatike/search?q=verbo&limit=20&include_edu=1
# Cache key: gramatike_search:q=verbo:limit=20:edu=True
```

### 4. `/api/novidades` - News Feed
**Cache Duration:** 5 minutes (300 seconds)
**Cache Key:** `novidades:list`

- **Why cache?** News updates are infrequent
- **Global cache:** All users see the same news
- **Timely updates:** 5 minutes ensures recent news appears quickly

```python
# Example usage
GET /api/novidades
# Cached for 5 minutes for all users
```

### 5. `/` - Index/Home Page
**Cache Duration:** 3 minutes (180 seconds)
**Cache Key:** `index:trending_commented`

- **Why cache?** Complex aggregation queries for trending/commented posts
- **Partial caching:** Only trending/commented sections are cached
- **Fresh divulgações:** Admin curated content is always fresh (not cached)
- **Short TTL:** 3 minutes keeps content relatively current

```python
# Example usage
GET /
# Trending and commented posts cached for 3 minutes
# Divulgações (promotional content) always fresh
```

## Cache Implementation Details

### Cache Storage
- **Type:** File-based JSON cache
- **Location:** `instance/app_web_cache.json` (gitignored)
- **Format:** JSON with TTL per entry
- **Serverless compatible:** Works in Vercel serverless environment

### Cache Key Strategy
1. **Static content:** Simple key (e.g., `redacao_temas:list`)
2. **User-specific:** Include user ID (e.g., `palavra_do_dia:123:user456`)
3. **Parameterized:** Include query params (e.g., `gramatike_search:q=test:limit=10:edu=False`)

### TTL Selection Guidelines
- **Daily rotation:** 1 hour (palavra do dia)
- **Static content:** 10 minutes (redação temas)
- **Semi-dynamic:** 5 minutes (novidades, search)
- **Dynamic aggregations:** 3 minutes (index trending/commented)

## Expected Results

### CPU Usage Reduction
- **Palavra do dia:** ~70% reduction (most repeated endpoint)
- **Search:** ~60% reduction (complex queries avoided)
- **Index:** ~50% reduction (heavy aggregations cached)
- **Overall:** Estimated 50-70% CPU usage reduction

### Response Time Improvement
- **Cache hit:** < 10ms (instant JSON retrieval)
- **Cache miss:** Normal DB query time
- **User experience:** Noticeably faster for cached responses

### Database Load
- **Queries saved:** Hundreds to thousands per hour
- **Connection pool:** Less pressure on serverless DB connections
- **Scalability:** Better handling of traffic spikes

## Monitoring & Maintenance

### Cache Health Checks
To verify cache is working:
```python
from gramatike_app.utils import web_cache

# Check if cache file exists and has entries
cached_data = web_cache._load()
print(f"Cached entries: {len(cached_data)}")
```

### Cache Invalidation
The cache automatically invalidates based on TTL. For manual invalidation:
```python
# Clear entire cache
import os
from gramatike_app.utils.web_cache import CACHE_PATH

if os.path.exists(CACHE_PATH):
    os.remove(CACHE_PATH)
```

### When to Update TTLs
Consider increasing TTL if:
- Content changes even less frequently
- CPU usage is still high
- Users don't mind slightly stale data

Consider decreasing TTL if:
- Users report seeing outdated content
- Real-time updates are critical
- Content changes frequently

## Testing

### Cache Functionality Test
Run the test suite:
```bash
python test_cache.py
```

Expected output:
```
✓ Basic cache set/get works
✓ Value available before expiration
✓ Value expired after TTL
✓ Multiple cache keys work independently

✅ All cache tests passed!
```

### Production Verification
After deployment, verify caching is working:
1. Make first request to an endpoint (cache miss)
2. Check response time
3. Make second request immediately (cache hit)
4. Response should be faster
5. Check Vercel analytics for CPU usage reduction

## Files Changed
- `gramatike_app/routes/__init__.py` - Added caching to 5 endpoints
- `.gitignore` - Added `instance/app_web_cache.json`
- `test_cache.py` - Test suite for cache functionality

## Deployment Notes

### Vercel Configuration
No changes needed. The file-based cache works in Vercel serverless:
- Each serverless function instance has its own cache
- Cache is rebuilt on cold starts (minimal impact)
- Warm instances benefit from cache

### Environment Variables
No new environment variables required. The cache uses existing app configuration.

### Rollback Plan
If caching causes issues:
1. Revert the commit that added caching
2. Or temporarily disable by setting TTL to 0 in the code
3. Cache file is gitignored and won't affect deployments

## Future Enhancements

### Potential Improvements
1. **Redis integration:** For shared cache across serverless instances
2. **Cache warming:** Pre-populate cache on deployment
3. **Smart invalidation:** Invalidate specific keys when content changes
4. **Cache metrics:** Log cache hit/miss ratios for monitoring
5. **Edge caching:** Use Vercel Edge Cache for static assets

### Additional Endpoints to Cache
Consider caching these in the future if needed:
- `/api/posts` - User posts (user-specific, 2-5 min)
- `/api/seguindo/<user_id>` - Following list (user-specific, 5 min)
- `/api/amigues` - Friends/connections (user-specific, 5 min)
- Exercise lists - `/exercicios` (topic-specific, 10 min)

## Conclusion
The caching implementation significantly reduces CPU usage while maintaining a good user experience with fresh content. The short TTLs ensure users see updates quickly while the cache prevents redundant database queries.

**Expected outcome:** Stay within Vercel free tier by reducing CPU usage by 50-70%.
