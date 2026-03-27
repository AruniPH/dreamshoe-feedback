# 🚀 Deployment Instructions

## Quick Start

### Run the Unified Application

```bash
cd /mnt/e/Msc/Research/product_feedback_analyzer
streamlit run main.py
```

Access at: **http://localhost:8501**

## Login Credentials

### Customer Access
```
Username: customer1
Password: customer123
```
**Pages:** Feedback Collector, Collective Intelligence

### Owner Access
```
Username: owner1
Password: owner123
```
**Pages:** All pages (Feedback Collector, Collective Intelligence, Owner Dashboard, Statistical Analysis)

## What Changed

### Before
- **app.py** → Customer dashboard (Port 8501)
- **owner_dashboard.py** → Owner dashboard (Port 8502)
- **pages/1_Collective_Intelligence.py** → Separate page

### After
- **main.py** → Everything in one app (Port 8501)
- Role-based navigation
- Automatic page filtering

## File Structure

```
product_feedback_analyzer/
├── main.py                    ← NEW: Run this file
├── database.py                ← Database operations
├── auth.py                    ← Authentication
├── .env                       ← Database credentials
├── models/
│   ├── model.pkl             ← ML model (unchanged)
│   └── vectorizer.pkl        ← Vectorizer (unchanged)
└── logo.png                   ← Logo image
```

## Access Control Matrix

| Page | Customer | Owner |
|------|----------|-------|
| Feedback Collector | ✅ | ✅ |
| Collective Intelligence | ✅ | ✅ |
| Owner Dashboard | ❌ | ✅ |
| Statistical Analysis | ❌ | ✅ |

## Features by Page

### 1. Feedback Collector (Both)
- AI chatbot interaction
- Product/feature selection
- Automatic ML classification
- Database storage

### 2. Collective Intelligence (Both)
- Submit improvement ideas
- Vote on ideas (👍/👎)
- Real-time vote counts
- Community prioritization

### 3. Owner Dashboard (Owner Only)
- Feature improvement charts
- Sub-feature breakdown
- Percentage analysis
- Auto-refresh (60s)

### 4. Statistical Analysis (Owner Only)
- ANOVA test results
- Tukey HSD comparisons
- Confidence intervals
- Feature comparison tool

## Testing Steps

1. **Start PostgreSQL**
   ```bash
   sudo service postgresql start
   ```

2. **Run Application**
   ```bash
   streamlit run main.py
   ```

3. **Test Customer Access**
   - Login as customer1
   - Verify only 2 menu items visible
   - Submit feedback
   - Submit and vote on ideas
   - Try accessing owner pages (should not be visible)

4. **Test Owner Access**
   - Logout
   - Login as owner1
   - Verify all 4 menu items visible
   - Check all pages load correctly
   - Verify analytics display properly

## Advantages

✅ **Single URL** - One application, one port  
✅ **Unified Navigation** - Consistent sidebar menu  
✅ **Role-Based Security** - Automatic access control  
✅ **Easy Deployment** - One command to start  
✅ **Better UX** - No switching between apps  
✅ **Simplified Maintenance** - One codebase  

## Production Deployment

For production, consider:

1. **Environment Variables**
   - Move OpenAI API key to .env
   - Use strong passwords
   - Enable PostgreSQL SSL

2. **Streamlit Cloud**
   ```bash
   # Add to .streamlit/config.toml
   [server]
   enableCORS = false
   enableXsrfProtection = true
   ```

3. **Database**
   - Use managed PostgreSQL (AWS RDS, etc.)
   - Enable connection pooling
   - Set up backups

## Rollback (If Needed)

If you need to go back to separate apps:

```bash
# Use the old files
streamlit run app_backup.py
streamlit run owner_dashboard_backup.py
```

## Support

- **Setup Issues**: See INSTALLATION_COMPLETE.md
- **Database Issues**: See QUICKSTART.md
- **App Guide**: See UNIFIED_APP_GUIDE.md

---

**You're all set! Run `streamlit run main.py` to start.**
