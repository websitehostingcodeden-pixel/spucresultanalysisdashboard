# CORS & Deployment Troubleshooting Guide

## Current Setup

**Frontend**: https://spucresultanalysisdashboard.vercel.app (Vercel)
**Backend**: https://spucresultanalysisdashboard.onrender.com (Render)

## If CORS Still Fails

### Step 1: Verify Render Settings

Go to **Render Dashboard** → Your Service → **Settings** → **Environment Variables**

Make sure these are set:

```
DEBUG=False
SECRET_KEY=7u#!10y_1tjs2$&bccbi@@80aeh_g*(1d5uojj#2*)k_$4w0=q
ALLOWED_HOSTS=spucresultanalysisdashboard.onrender.com,localhost,127.0.0.1
FRONTEND_URL=https://spucresultanalysisdashboard.vercel.app
```

Optional (for explicit CORS control):
```
CORS_ALLOWED_ORIGINS=https://spucresultanalysisdashboard.vercel.app,https://spucresultanalysisdashboard.*.vercel.app
```

### Step 2: Force Redeploy

1. Go to Render Dashboard
2. Find your service
3. Click **Manual Deploy** → **Deploy latest commit**
4. Wait for deployment to complete (5-10 minutes)

### Step 3: Test CORS

Open browser DevTools → Network tab → Try uploading a file

You should see:
```
Request Headers:
  Origin: https://spucresultanalysisdashboard.vercel.app

Response Headers:
  Access-Control-Allow-Origin: https://spucresultanalysisdashboard.vercel.app
  Access-Control-Allow-Methods: GET, POST, OPTIONS, ...
```

### Step 4: If Still Failing

Check Render logs for errors:
1. Render Dashboard → Your Service
2. Click **Logs** tab
3. Look for error messages mentioning CORS, middleware, or django-cors-headers

## Common Issues

| Error | Solution |
|-------|----------|
| "No 'Access-Control-Allow-Origin' header" | Run Manual Deploy on Render |
| "CSRF token verification failed" | Tokens are not needed for API (exempted) |
| "File upload shows 400 error" | Check file format - must be .xlsx or .xls |
| "Upload succeeds but no data appears" | Check file has SCIENCE/COMMERCE sheets |

## How CORS Works (Technical)

1. **Preflight Request**: Browser sends OPTIONS request before actual POST
2. **Backend Returns**: CORS headers allowing request
3. **Actual Request**: Browser sends POST with file
4. **Backend Processes**: File is processed and analytics computed

Our configuration:
- Allows: `https://*.vercel.app` (all Vercel deployments)
- Allows: `https://spucresultanalysisdashboard.onrender.com`
- Allows: All localhost variants for testing

## Files Modified for CORS

- `aris_backend/config/settings/base.py` - CORS configuration
- `aris_backend/apps/results/api/views.py` - CSRF endpoint
- `frontend/src/api/client.js` - API client with CORS support
