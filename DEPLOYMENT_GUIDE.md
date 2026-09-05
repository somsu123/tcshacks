# FraudShield Production Deployment Guide

**Last Updated:** 11 January 2026  
**Estimated Time:** 30-45 minutes

---

## 📋 Pre-Deployment Checklist

- [x] Backend running locally on port 8000
- [x] Frontend running locally on port 3000
- [x] Database migrations created and tested
- [x] All TypeScript errors fixed
- [x] Environment variables documented
- [ ] GitHub repository accessible
- [ ] Render account created
- [ ] Vercel account created

---

## 🔧 Step 1: Prepare Backend for Deployment

### A. Create Production Environment File

Already configured in `.env` - verify it has:
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fraudshield
```

### B. Verify Deployment Files

Check these files exist:
- ✅ `Procfile` - Gunicorn startup command
- ✅ `render.yaml` - Render configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `runtime.txt` - Python version

---

## 🚀 Step 2: Deploy Backend to Render

### Option A: Deploy via GitHub (Recommended)

1. **Push to GitHub** (if not already):
```bash
cd /Users/ved/FraudShieldAI
git add .
git commit -m "Production ready - Phase 1 complete"
git push origin main
```

2. **Create Render Account**:
   - Go to https://render.com
   - Sign up with GitHub (easiest)

3. **Create PostgreSQL Database**:
   - Dashboard → New → PostgreSQL
   - Name: `fraudshield-db`
   - Database: `fraudshield`
   - User: `fraudshield_user`
   - Plan: **Free** (good for MVP)
   - Region: Choose closest to you
   - Click **Create Database**
   - **IMPORTANT**: Copy the "Internal Database URL" (starts with `postgresql://`)

4. **Create Web Service**:
   - Dashboard → New → Web Service
   - Connect your GitHub repository
   - Name: `fraudshield-api`
   - Region: Same as database
   - Branch: `main`
   - Root Directory: `.` (leave blank or dot)
   - Runtime: **Python 3**
   - Build Command: 
     ```
     pip install -r requirements.txt && alembic upgrade head
     ```
   - Start Command:
     ```
     gunicorn --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 -w 2 --timeout 120 app.main:app
     ```
   - Plan: **Free** (1 instance)

5. **Add Environment Variables**:
   - Click "Environment" tab
   - Add variable:
     - Key: `DATABASE_URL`
     - Value: (paste the Internal Database URL from step 3)
   - Click **Save Changes**

6. **Deploy**:
   - Click "Manual Deploy" → "Deploy latest commit"
   - Wait 3-5 minutes for build to complete

7. **Verify Deployment**:
   - Once deployed, you'll see a URL like: `https://fraudshield-api.onrender.com`
   - Visit: `https://fraudshield-api.onrender.com/health`
   - Should see: `{"status":"healthy","service":"FraudShield API"}`
   - Visit: `https://fraudshield-api.onrender.com/docs` (Swagger UI)

### Option B: Deploy via Render Blueprint

If you have `render.yaml`:
- Dashboard → New → Blueprint
- Connect repository
- Render will auto-detect configuration
- Still need to add DATABASE_URL manually

---

## 🌐 Step 3: Deploy Frontend to Vercel

### A. Update Frontend Environment

1. **Create Production Environment File**:
```bash
# Already exists at frontend/.env.production
# Update it with your Render backend URL:
NEXT_PUBLIC_API_URL=https://fraudshield-api.onrender.com
```

2. **Verify it's correct**:
```bash
cat /Users/ved/FraudShieldAI/frontend/.env.production
```

### B. Deploy to Vercel

1. **Create Vercel Account**:
   - Go to https://vercel.com
   - Sign up with GitHub

2. **Import Project**:
   - Dashboard → Add New → Project
   - Import Git Repository → Select `FraudShieldAI`
   - Click **Import**

3. **Configure Project**:
   - Framework Preset: **Next.js** (auto-detected)
   - Root Directory: Click "Edit" → Set to `frontend`
   - Build Command: `npm run build` (default, don't change)
   - Output Directory: `.next` (default, don't change)

4. **Add Environment Variables**:
   - Click "Environment Variables"
   - Add variable:
     - Key: `NEXT_PUBLIC_API_URL`
     - Value: `https://fraudshield-api.onrender.com` (your Render backend URL)
     - Environment: **Production** (check this box)
   - Click "Add"

5. **Deploy**:
   - Click **Deploy**
   - Wait 2-3 minutes for build

6. **Verify Deployment**:
   - Once complete, you'll see: "Your project is ready!"
   - Click "Visit" or open the assigned URL (e.g., `https://fraudshield-ai.vercel.app`)
   - Dashboard should load with 20 seed transactions

---

## ✅ Step 4: Verification Checklist

### Backend Tests
Visit your Render backend URL and test:

- [ ] **Health Check**: `/health` returns `{"status":"healthy"}`
- [ ] **API Docs**: `/docs` shows Swagger UI with all endpoints
- [ ] **List Transactions**: `/transactions` returns JSON array with 20 items
- [ ] **Get Single Transaction**: `/transactions/{id}` returns transaction detail
- [ ] **CORS Working**: No CORS errors in browser console

### Frontend Tests
Visit your Vercel frontend URL and test:

- [ ] **Dashboard loads** with transaction list
- [ ] **Search works** - type a payee name
- [ ] **Filter works** - click risk level chips
- [ ] **Financial summary** shows £ at risk
- [ ] **Create transaction** - click "Add Transaction", fill form, submit
- [ ] **Transaction detail** - click a transaction, see risk analysis
- [ ] **Approve/Reject buttons** - click, confirm, see toast
- [ ] **Audit trail** - see timeline at bottom of detail page
- [ ] **CSV Upload** - click "Import CSV", test with sample
- [ ] **Settings page** - click settings icon, controls render
- [ ] **Dark mode** - toggle works throughout app

---

## 🐛 Troubleshooting

### Backend Issues

**Problem**: `alembic: command not found` during build
**Solution**: Add to `requirements.txt`:
```
alembic==1.13.1
```

**Problem**: Database connection fails
**Solution**: 
- Verify `DATABASE_URL` is set in Render environment variables
- Check it starts with `postgresql://` (not `postgres://`)
- If it starts with `postgres://`, Render auto-converts

**Problem**: 502 Bad Gateway
**Solution**:
- Check Render logs (Dashboard → Your Service → Logs)
- Verify gunicorn start command is correct
- Ensure port 8000 is in the command

**Problem**: No seed data
**Solution**:
- Seed data loads on startup automatically from `app/data/demo_transactions.json`
- Check logs for "FraudShield: Loaded X seed transactions"

### Frontend Issues

**Problem**: "Failed to fetch" errors
**Solution**:
- Verify `NEXT_PUBLIC_API_URL` is set in Vercel environment variables
- Check it points to your Render backend URL (without trailing slash)
- Redeploy after changing env vars (Vercel → Deployments → Redeploy)

**Problem**: CORS errors
**Solution**:
- Backend already has `allow_origins=["*"]` in CORS middleware
- For production, update to: `allow_origins=["https://fraudshield-ai.vercel.app"]`

**Problem**: Dark mode not working
**Solution**:
- This is client-side only, should work automatically
- Clear browser cache and hard refresh (Cmd+Shift+R)

---

## 🔐 Post-Deployment Security

### Immediate Actions
- [ ] Update CORS to specific domain (not wildcard)
- [ ] Add rate limiting (future)
- [ ] Set up monitoring (Sentry optional)

### Update Backend CORS (Optional):
```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fraudshield-ai.vercel.app"],  # Your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Monitoring

### Render Monitoring
- Dashboard → Your Service → Metrics
- View: CPU, Memory, Request count
- Logs: Real-time application logs

### Vercel Analytics
- Dashboard → Your Project → Analytics
- View: Page views, performance, errors
- Free tier: 100K requests/month

---

## 🚀 Next Steps After Deployment

1. **Test Everything** - Go through verification checklist above
2. **Share with Users** - Send Vercel URL to beta testers
3. **Monitor Logs** - Check for errors in first 24 hours
4. **Plan Phase 2** - Authentication, email alerts, analytics

---

## 📞 Useful URLs

**Documentation**:
- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)

**Your Services** (after deployment):
- Backend: `https://fraudshield-api.onrender.com`
- Frontend: `https://fraudshield-ai.vercel.app` (or your custom domain)
- Backend Logs: Render Dashboard → fraudshield-api → Logs
- Frontend Logs: Vercel Dashboard → fraudshield-ai → Logs

---

## ✨ Success Criteria

✅ Backend health check returns 200  
✅ Frontend loads without errors  
✅ Can create new transactions  
✅ Can approve/reject transactions  
✅ Search and filters work  
✅ Dark mode toggles  
✅ No console errors  

**Once all checks pass, you're live! 🎉**
