# ✅ SETUP CHECKLIST - Just Follow This

Print this or keep it open on your phone. Takes 5 minutes total.

---

## ☐ STEP 1: Get Anthropic API Key (2 minutes)

1. ☐ Open: **https://console.anthropic.com**
2. ☐ Click **"Sign Up"** (use your email: singthedamnsong@gmail.com)
3. ☐ Check your email → Click confirmation link
4. ☐ Log back in to console.anthropic.com
5. ☐ Click **"Get API Keys"** or **"API Keys"** in the menu
6. ☐ Click **"+ Create Key"**
7. ☐ Name it: "Marketplace Bot"
8. ☐ **COPY THE KEY** (starts with sk-ant-api03-...)
   - Paste it somewhere safe temporarily (Notepad)
9. ☐ Click **"Billing"** in the menu
10. ☐ Click **"Purchase Credits"**
11. ☐ Add **$20** with your credit card
12. ☐ Click **"Purchase"**

**✓ DONE!** You now have: `sk-ant-api03-xxxxxxxxxxxxx`

---

## ☐ STEP 2: Get Facebook Token (3 minutes)

### If you DON'T have a Facebook Page:
1. ☐ Go to: **https://www.facebook.com/pages/create**
2. ☐ Click **"Get Started"**
3. ☐ Choose **"Business or Brand"**
4. ☐ Page name: "Your Name's Sales" (or whatever)
5. ☐ Click **"Create Page"**

### Get Your Token:
1. ☐ Go to: **https://developers.facebook.com/tools/explorer/**
2. ☐ Click **"Meta App"** → **"Create App"** (if you don't have one)
   - ☐ Choose **"Business"**
   - ☐ App name: "Marketplace Bot"
   - ☐ Your email
   - ☐ Click **"Create App"**
3. ☐ Back at Graph API Explorer
4. ☐ Click **"Generate Access Token"**
5. ☐ Check these boxes:
   - ☐ `pages_manage_posts`
   - ☐ `pages_read_engagement`
   - ☐ `catalog_management`
6. ☐ Click **"Generate Token"**
7. ☐ **COPY THE TOKEN** (long string of letters/numbers)
   - Paste it in Notepad with your Anthropic key

### Get Your Page ID:
1. ☐ Go to your Facebook Page
2. ☐ Click **"About"** (left side)
3. ☐ Scroll down to **"Page ID"**
4. ☐ **COPY THE NUMBER** (like 123456789)
   - Paste it in Notepad

**✓ DONE!** You now have:
- Facebook Token: `EAAxxxxxxxxxx`
- Page ID: `123456789`

---

## ☐ STEP 3: Configure .env File (1 minute)

1. ☐ Open folder: `Ditto/backend/`
2. ☐ Find file: `.env.simple`
3. ☐ **Rename it to:** `.env` (remove the .simple part)
4. ☐ Open `.env` with Notepad
5. ☐ Copy/paste your keys from Notepad:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-paste-yours-here
   FACEBOOK_ACCESS_TOKEN=EAA-paste-yours-here
   FACEBOOK_PAGE_ID=123456789
   ```
6. ☐ **Save** the file
7. ☐ Close Notepad

**✓ DONE!** App is configured!

---

## ☐ STEP 4: Start The App (10 seconds)

**Windows:**
1. ☐ Go to `Ditto` folder
2. ☐ **Double-click** `START.bat`
3. ☐ Wait for it to say "started successfully"

**Mac/Linux:**
1. ☐ Open Terminal
2. ☐ `cd Ditto`
3. ☐ `./START.sh`

**✓ DONE!** Server is running!

---

## ☐ STEP 5: Use It! (Ready to sell)

1. ☐ Open browser
2. ☐ Go to: **http://localhost:8000**
3. ☐ Upload photos of item
4. ☐ Click **"Analyze"**
5. ☐ Click **"Post to Facebook Marketplace"**

**✓ DONE!** Your item is live!

---

## 🆘 Problems?

- **"Module not found"** → Re-run START.bat
- **"API key not set"** → Check .env file (no spaces around = signs)
- **"Server won't start"** → Make sure you're in Ditto folder

---

## 📝 Your Keys (fill this in as you go):

```
Anthropic API Key: sk-ant-api03-_______________________________

Facebook Token: EAA____________________________________________

Facebook Page ID: ___________
```

---

**That's it! Just check off each box as you go. 5 minutes and you're selling!**
