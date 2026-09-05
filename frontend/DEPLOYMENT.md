# FraudShield Frontend - Vercel Deployment Instructions

## Environment Variables for Vercel

When deploying to Vercel, configure these environment variables in the Vercel dashboard:

### Required Variables

1. **NEXT_PUBLIC_API_URL**
   - **Description:** Backend API URL (your Render deployment)
   - **Value:** `https://fraudshield-api.onrender.com` (replace with your actual Render URL)
   - **Scope:** Production, Preview, Development

### How to Set Environment Variables in Vercel

1. Go to your project in Vercel dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add `NEXT_PUBLIC_API_URL` with your Render backend URL
4. Select which environments it applies to (Production, Preview, Development)
5. Click **Save**
6. Redeploy your application to apply changes

### Finding Your Render Backend URL

1. Go to your Render dashboard
2. Click on your `fraudshield-api` service
3. Copy the URL at the top (format: `https://fraudshield-api.onrender.com`)
4. Use this URL in Vercel's `NEXT_PUBLIC_API_URL` variable

### Testing Locally

For local development, the frontend uses `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

This is already configured and works when running:
```bash
cd frontend && npm run dev
```

### Troubleshooting

**Problem:** Frontend can't connect to backend
- Check that `NEXT_PUBLIC_API_URL` is set in Vercel
- Verify the Render URL is correct and accessible
- Check Render service is running (green status)
- Ensure backend CORS allows your Vercel domain

**Problem:** Changes not applying
- Redeploy in Vercel after changing env vars
- Clear browser cache
- Check browser console for errors
