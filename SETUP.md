# 🚀 Quick Setup Guide - Facebook Marketplace Auto-Poster

This guide will get you up and running in **15 minutes**.

## What You'll Need

1. **Anthropic API Key** ($5-20/month)
   - Powers the AI that analyzes photos and writes listings
   - Sign up: https://console.anthropic.com
   - Add $20 credit to start

2. **Facebook Page & Developer Account** (FREE)
   - For auto-posting to Marketplace
   - 10 minutes to set up

3. **Python 3.9+** (FREE)
   - Already on most computers

---

## Step 1: Install Dependencies (2 minutes)

### On Windows:
```bash
cd Ditto\backend
pip install -r requirements.txt
```

### On Mac/Linux:
```bash
cd Ditto/backend
pip3 install -r requirements.txt
```

---

## Step 2: Get Your Anthropic API Key (3 minutes)

1. Go to https://console.anthropic.com
2. Sign up or log in
3. Click "Get API Keys"
4. Create a new key
5. **Copy it** - you'll need it in Step 4

**Add Credits:**
- Click "Billing" → "Add Credits"
- Add $20 to start (lasts 1-2 months typically)

---

## Step 3: Set Up Facebook API (10 minutes)

### A. Create a Facebook Page (if you don't have one)
1. Go to https://www.facebook.com/pages/create
2. Choose "Business or Brand"
3. Fill in details (use your name/business)
4. Click "Create Page"

### B. Create a Facebook App
1. Go to https://developers.facebook.com/apps/create
2. Choose "Business" app type
3. Fill in:
   - **App Name:** "My Marketplace Poster" (or anything)
   - **Contact Email:** Your email
4. Click "Create App"

### C. Get Your Access Token
1. In your new app, go to **Settings** → **Basic**
2. Copy your **App ID** and **App Secret** (save these)
3. Go to **Tools** → **Graph API Explorer**
4. Click "Generate Access Token"
5. Grant these permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `catalog_management` (for Marketplace)
6. Copy the access token
7. **Make it long-lived:**
   - Go to https://developers.facebook.com/tools/accesstoken
   - Click "Extend Access Token"
   - Copy the new long-lived token (this won't expire)

### D. Get Your Page ID
1. Go to your Facebook Page
2. Click "About"
3. Scroll down to find "Page ID" (it's a number like 123456789)
4. Copy it

---

## Step 4: Configure Your Environment (2 minutes)

1. In the `Ditto/backend` folder, create a file called `.env`
2. Copy this template and fill in YOUR values:

```bash
# REQUIRED: Your Anthropic API key from Step 2
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx

# REQUIRED: Your Facebook credentials from Step 3
FACEBOOK_ACCESS_TOKEN=your_long_lived_access_token_here
FACEBOOK_PAGE_ID=123456789

# Server settings (leave these as-is)
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

3. Save the file

---

## Step 5: Start the App! (1 minute)

### On Windows:
```bash
cd Ditto\backend
python main.py
```

### On Mac/Linux:
```bash
cd Ditto/backend
python3 main.py
```

You should see:
```
✓ Marketplace Bot Analyzer API started successfully
INFO: Uvicorn running on http://0.0.0.0:8000
```

---

## Step 6: Open the App

1. Open your web browser
2. Go to: **http://localhost:8000**
3. Or open `Ditto/frontend/marketplace-app.html` directly

---

## 🎉 You're Done!

### How to Use:
1. **Upload photos** of item you want to sell
2. **Select condition** (New, Good, etc.)
3. Click **"Analyze & Generate Listing"**
4. Review the AI-generated listing
5. Click **"Post to Facebook Marketplace"**
6. Done! It's live on Facebook!

---

## ⚠️ Troubleshooting

### "Module not found" error
- Run: `pip install -r requirements.txt` again

### "ANTHROPIC_API_KEY not set"
- Check your `.env` file is in the `backend/` folder
- Make sure there are no spaces around the `=` sign
- Restart the server

### "Facebook posting failed"
- Check your access token is long-lived (not expired)
- Make sure you granted all permissions
- Check your Page ID is correct (just numbers)

### App won't start
- Make sure you're in the `backend/` folder
- Check Python version: `python --version` (need 3.9+)
- Try: `python3 main.py` instead of `python main.py`

---

## 💡 Pro Tips

- **First time?** Test with one item to make sure posting works
- **Keep your .env file private** - never share your API keys
- **Running low on credits?** Check usage at console.anthropic.com
- **Want to stop?** Press `Ctrl+C` in the terminal

---

## Need Help?

1. Check the error message in the terminal
2. Make sure all API keys are correct in `.env`
3. Restart the server after changing `.env`

That's it! You're ready to automate your marketplace listings! 🚀
