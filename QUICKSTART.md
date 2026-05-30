# ⚡ QUICKSTART - Get Running in 5 Minutes

**Don't have time to read documentation? Follow these steps:**

## 🎯 What This Does

Upload photos → AI analyzes item → AI writes listing → Auto-posts to Facebook Marketplace

**That's it. You're done selling.**

---

## ✅ Step 1: Get API Keys (5 min)

### Anthropic API ($5-20/month):
1. Go to: **https://console.anthropic.com**
2. Sign up
3. Click "Get API Keys" → Create key
4. **Copy the key** (starts with `sk-ant-api03-...`)
5. Add $20 credits (Billing → Add Credits)

### Facebook API (FREE):
**Simple version (if you have a Facebook Page):**
1. Go to: **https://developers.facebook.com/tools/explorer**
2. Select your Page
3. Click "Generate Access Token"
4. Select permissions: `pages_manage_posts`, `catalog_management`
5. **Copy the token**
6. Get Page ID: Go to your Page → About → Page ID

**Don't have a Page?** See [SETUP.md](SETUP.md) for detailed instructions.

---

## ✅ Step 2: Configure

1. Open `Ditto/backend/.env.simple`
2. Rename it to `.env`
3. Fill in your keys:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY-HERE
   FACEBOOK_ACCESS_TOKEN=YOUR-TOKEN-HERE
   FACEBOOK_PAGE_ID=123456789
   ```
4. Save

---

## ✅ Step 3: Run It

### Windows:
Double-click `START.bat`

### Mac/Linux:
```bash
./START.sh
```

### Or manually:
```bash
cd backend
pip install -r requirements.txt
python main.py
```

---

## ✅ Step 4: Use It

1. Open **http://localhost:8000** in your browser
   - OR open `frontend/marketplace-app.html`
2. Upload photos of your item
3. Click "Analyze"
4. Click "Post to Facebook Marketplace"
5. **DONE!**

---

## ❌ Problems?

### "Can't find module"
```bash
cd backend
pip install -r requirements.txt
```

### "API key not set"
- Check `.env` file is in `backend/` folder
- Make sure no spaces around `=` signs
- Restart the server

### "Facebook posting failed"
- Token might be expired (get a new one)
- Check Page ID is correct
- Make sure you granted permissions

---

## 💡 That's It!

**See [SETUP.md](SETUP.md) for detailed guide**
**See [README.md](README.md) for full documentation**
