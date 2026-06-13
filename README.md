# neurapulse-seo-automation
AI-powered SEO automation platform for backlink building, content optimization, and digital growth.
# 🖼️ NeuraPulse SEO Automation — Image Submission Bot

Automatically submit images to **96 sites** and build backlinks for your website.

## 📁 Repo Structure

```
neurapulse-seo-automation/
│
├── config/
│   ├── config.json          ← Your website, email, password
│   ├── accounts.json        ← Auto-saved logins (bot fills this)
│   └── sites.json           ← All 96 sites with selectors
│
├── data/
│   ├── pages.csv            ← All your 300+ blog URLs
│   └── submission_log.json  ← Auto-created, tracks progress
│
├── images/
│   ├── master/              ← Put your original images here
│   └── processed/           ← Bot saves resized images here
│
├── modules/
│   ├── image_processor.py   ← Auto resize/convert images
│   ├── account_manager.py   ← Signup/login handler
│   ├── submitter.py         ← Main bot engine
│   └── dashboard.py         ← Live terminal progress
│
├── logs/
│   └── errors.log           ← Auto-created error log
│
├── dashboard.html           ← Open in browser to track progress
├── START.bat                ← Double click to run on Windows
├── requirements.txt         ← Python packages
└── README.md
```

## ⚡ Quick Start

### Step 1 — Install Python
Download from https://www.python.org/downloads/
**Check "Add Python to PATH"** during install!

### Step 2 — Install packages
```
pip install selenium webdriver-manager pillow requests
```

### Step 3 — Edit config/config.json
```json
{
  "website_url": "https://yourwebsite.com",
  "email": "youremail@gmail.com",
  "password": "YourPassword",
  "username": "yourusername"
}
```

### Step 4 — Add your image
Put your image in `images/master/` folder and name it `myimage.jpg`

### Step 5 — Add your pages
Edit `data/pages.csv` and add all your blog URLs

### Step 6 — Run
Double click `START.bat` OR run:
```
cd modules
python submitter.py
```

## 🤖 How It Works

| Type | Sites | How |
|------|-------|-----|
| ⚡ Auto | 12 sites | 100% automatic, no login needed |
| 🔑 Signup | 10 sites | Bot creates account once, saves login |
| 👤 Assist | 74 sites | Bot opens site, you submit |

## 📋 CAPTCHA Handling
Bot **pauses** when CAPTCHA appears → you solve it → press Enter → bot continues.
This only happens **once per site** during first signup.

## 📊 Image Auto-Processing
- Bot reads each site's max size (KB/MB limit)
- Auto-compresses your image to fit
- Auto-converts JPG/PNG as needed
- You give one master image — bot handles everything

## 📅 Daily Workflow (for 300+ pages)
1. Add new image to `images/master/`
2. Add new page URL to `data/pages.csv`
3. Run bot → it picks the next pending page automatically
4. Mark done in `dashboard.html`

## 💰 For Client Work
Change just 3 lines in `config/config.json`:
```json
"website_url": "https://clientsite.com",
"email": "client@gmail.com",
"password": "clientpassword"
```

---
Built by NeuraPulse AI — https://neuraplus-ai.github.io
