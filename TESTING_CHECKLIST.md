# FraudShield AI - Testing Checklist
**Date:** January 12, 2026  
**Purpose:** Verify all Phase 1 features work in production

---

## 🔍 **Current Testing Status**

### **Backend Production (Render)**
- **URL:** https://fraudshield-api.onrender.com
- **Status:** ❌ **RUNNING OLD CODE**
- **Issue:** Still using in-memory storage (not database integration)
- **Evidence:** Created transaction ID `8f65d9b3-95b0-4fae-8338-487b4cbea8aa` but it disappeared from list
- **Last Deploy:** Unknown (needs manual trigger or auto-deploy verification)

### **Frontend Production (Vercel)**
- **URL:** Unknown (need to check Vercel dashboard)
- **Status:** ⏳ **DEPLOYMENT PENDING**
- **Last Push:** Cache clear commit `2b0d2a4`
- **Next Push:** Database integration commit `a355825`

### **Database**
- **Render PostgreSQL:** ✅ Provisioned (from render.yaml)
- **Connection Test:** ⏳ Not yet verified
- **Seed Data:** ⏳ Not loaded yet
- **Migrations:** ⏳ Need to verify if ran on Render

---

## 📋 **Complete Testing Protocol**

### **Phase 1: Infrastructure Verification**

#### **Backend API Tests**
```bash
# 1. Health Check
curl https://fraudshield-api.onrender.com/health
# Expected: {"status":"healthy","service":"FraudShield API"}

# 2. List Transactions (should have seed data)
curl https://fraudshield-api.onrender.com/transactions
# Expected: 20 demo transactions with full details

# 3. Get Single Transaction Detail
curl https://fraudshield-api.onrender.com/transactions/demo_001
# Expected: Full transaction with risk_factors, confidence, explanation

# 4. Create New Transaction
curl -X POST https://fraudshield-api.onrender.com/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 3000,
    "payee": "ACME Corp",
    "timestamp": "2026-01-12T10:00:00Z",
    "reference": "Invoice 123",
    "payee_is_new": true
  }'
# Expected: New transaction ID with risk_score

# 5. Verify Persistence
curl https://fraudshield-api.onrender.com/transactions
# Expected: Previous transaction still in list

# 6. Approve Transaction
curl -X POST https://fraudshield-api.onrender.com/transactions/{ID}/approve
# Expected: Status updated to "approved"

# 7. Get Audit Trail
curl https://fraudshield-api.onrender.com/transactions/{ID}/audit
# Expected: Array with "created" and "approved" entries
```

#### **Frontend Tests**
```bash
# 1. Homepage Loads
curl -I https://[your-vercel-url]
# Expected: 200 OK

# 2. Check API Connection
# Open browser dev tools → Network tab → Check fetch calls
# Expected: Calls to fraudshield-api.onrender.com

# 3. Environment Variable
curl https://[your-vercel-url]/_next/static/
# Check if NEXT_PUBLIC_API_URL is set correctly
```

---

### **Phase 2: Feature Testing (Manual)**

#### **Test Case 1: Dashboard View**
- [ ] Open frontend URL
- [ ] See list of transactions
- [ ] Verify stats row shows: Total count, At risk £, Fraud rate %
- [ ] Check dark/light theme toggle works
- [ ] Verify responsive design on mobile size

#### **Test Case 2: Search & Filters**
- [ ] Type payee name in search bar
- [ ] Verify filtered results
- [ ] Click "High" risk filter chip
- [ ] Verify only high-risk transactions shown
- [ ] Clear filters → all transactions return

#### **Test Case 3: Transaction Detail**
- [ ] Click on a high-risk transaction
- [ ] Verify risk badge shows correct level
- [ ] Check confidence meter displays
- [ ] See "Why This Was Flagged" section with factor cards
- [ ] Verify recommended action text
- [ ] Check audit trail timeline displays

#### **Test Case 4: Create Transaction**
- [ ] Click "Add Transaction" button
- [ ] Fill form: Amount £1500, Payee "Test Corp", etc
- [ ] Submit form
- [ ] Verify redirect to detail page
- [ ] Check transaction appears in dashboard list

#### **Test Case 5: CSV Upload**
- [ ] Navigate to /transactions/upload
- [ ] Drag CSV file into dropzone
- [ ] See progress bar
- [ ] Verify success message "X transactions imported"
- [ ] Check transactions appear in dashboard

#### **Test Case 6: Action Buttons**
- [ ] Open transaction detail page
- [ ] Click "Mark as Legitimate"
- [ ] See confirmation dialog
- [ ] Confirm action
- [ ] Verify success toast notification
- [ ] Check audit trail shows "approved" entry

#### **Test Case 7: Reject Transaction**
- [ ] Open different transaction
- [ ] Click "Mark as Fraud"
- [ ] Confirm in dialog
- [ ] Verify rejected status
- [ ] Check audit trail updated

#### **Test Case 8: Settings Page**
- [ ] Navigate to /settings
- [ ] See fraud detection preferences
- [ ] Toggle email alerts
- [ ] Verify saved (localStorage)

---

### **Phase 3: Edge Cases & Error Handling**

#### **Error Scenarios**
- [ ] **Invalid Transaction ID:** GET /transactions/invalid-uuid → 404
- [ ] **Missing Required Field:** POST /transactions without amount → 422
- [ ] **Network Failure:** Disconnect internet → Show error message
- [ ] **Large CSV Upload:** Upload 1000+ rows → Handle properly
- [ ] **Duplicate Transaction:** Try creating same transaction twice
- [ ] **Backend Down:** Stop Render → Frontend shows graceful error

#### **Performance Tests**
- [ ] Dashboard loads in <2 seconds
- [ ] Detail page loads in <1 second
- [ ] CSV upload processes 100 rows in <5 seconds
- [ ] Search filters respond instantly (<200ms)
- [ ] No memory leaks (check DevTools over 5 minutes)

---

### **Phase 4: Production Data Verification**

#### **Database Checks**
```bash
# Check if migrations ran on Render
# (Need to access Render shell or check logs)
alembic current
# Expected: 20260111_2324 (beaf29a77558)

# Count transactions in database
# Expected: 20 seed transactions after first deploy
```

#### **Seed Data Validation**
- [ ] 20 demo transactions loaded
- [ ] All have risk_score calculated
- [ ] All have explanations generated
- [ ] Audit logs created for each
- [ ] Timestamps are recent

---

## 🐛 **Known Issues Found During Testing**

### **Critical Issues**
1. ❌ **Render backend not auto-deploying**
   - Status: Git push didn't trigger Render rebuild
   - Impact: Production running old code
   - Fix: Manual deploy or check Render webhook

2. ⏳ **Vercel frontend deployment status unknown**
   - Status: Need to check Vercel dashboard
   - Impact: Users may see old frontend
   - Fix: Verify auto-deploy or trigger manual

3. ⏳ **Database integration not deployed**
   - Status: New code pushed but not live
   - Impact: Transactions not persisting
   - Fix: Trigger Render redeploy

### **Medium Issues**
- [ ] None yet (will update during testing)

### **Low Priority**
- [ ] None yet (will update during testing)

---

## ✅ **Testing Completion Criteria**

**Definition of Done:**
- [ ] Backend health check returns 200
- [ ] All 7 API endpoints work correctly
- [ ] Frontend loads without errors
- [ ] Can create transaction and see it persist
- [ ] Can approve/reject and see audit trail
- [ ] Search and filters work
- [ ] CSV upload processes successfully
- [ ] Dashboard stats calculate correctly
- [ ] All 11 Phase 1 features verified
- [ ] No console errors in browser
- [ ] No 500 errors in API logs
- [ ] Database has seed data
- [ ] Migrations applied successfully

---

## 🚨 **Current Action Items**

### **Immediate (Next 30 Minutes)**
1. **Check Render Dashboard**
   - Verify auto-deploy is enabled
   - Check last deployment timestamp
   - Review build logs for errors

2. **Check Vercel Dashboard**
   - Verify build succeeded
   - Get production URL
   - Check environment variables set

3. **Trigger Manual Deploys**
   - Render: Click "Manual Deploy" → Deploy latest commit
   - Vercel: Should auto-deploy on git push

4. **Re-test Production Endpoints**
   - Run all 7 API endpoint tests
   - Verify database integration works
   - Check seed data loaded

5. **Frontend End-to-End Test**
   - Open production URL
   - Test all 11 Phase 1 features
   - Document any failures

---

## 📊 **Testing Results Log**

### **Test Run 1 - Jan 12, 2026 11:45 AM**
- **Backend Health:** ✅ PASS
- **List Transactions:** ❌ FAIL - Returns empty array (old code)
- **Create Transaction:** ✅ PASS - Returns ID
- **Persistence:** ❌ FAIL - Transaction lost (in-memory storage)
- **Conclusion:** Backend needs redeploy

### **Test Run 2 - Pending**
- Will run after Render redeploys latest code

---

## 🔄 **Continuous Testing Strategy**

### **Pre-Deployment Checks**
Before every git push:
```bash
# 1. Local build test
cd frontend && npm run build

# 2. Backend syntax check
python -m py_compile app/main.py

# 3. Run local integration test
./scripts/test_integration.sh

# 4. Check for errors
npm run lint
```

### **Post-Deployment Verification**
After every deploy:
```bash
# 1. Health check
curl https://fraudshield-api.onrender.com/health

# 2. Smoke test
curl https://fraudshield-api.onrender.com/transactions | jq '.total'

# 3. Frontend check
curl -I https://[vercel-url]
```

### **Weekly Production Tests**
- [ ] Run full testing checklist
- [ ] Check error tracking dashboard (Sentry)
- [ ] Review API response times
- [ ] Verify database size/performance
- [ ] Test backup/restore procedures

---

## 📝 **Notes for Future**

### **Testing Tools to Add**
1. **Playwright** - E2E frontend tests
2. **pytest** - Backend unit tests
3. **Postman Collection** - API regression tests
4. **GitHub Actions** - CI/CD pipeline
5. **k6** - Load testing

### **Monitoring to Add**
1. **Sentry** - Error tracking
2. **Uptime Robot** - Availability monitoring
3. **Vercel Analytics** - Frontend performance
4. **Render Metrics** - Backend performance
5. **Database monitoring** - Query performance

---

**Last Updated:** January 12, 2026, 11:45 AM  
**Next Review:** After Render/Vercel redeployments complete
