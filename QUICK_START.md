# Quick Start Guide - AI Company Analysis

## Problem Solved ✓
Company searches now return **unique, AI-powered analysis for each company** instead of generic responses.

## Quick Setup (2 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Get an AI API Key (Choose ONE)

**Option A: Google Gemini (Easiest - Recommended)**
1. Visit https://ai.google.dev/
2. Click "Get API Key"
3. Copy the key

**Option B: Groq (Fastest)**
1. Visit https://console.groq.com/
2. Sign up and get API key
3. Very generous free tier

**Option C: OpenAI (Most Powerful)**
1. Visit https://platform.openai.com/api-keys
2. Create new API key
3. Requires credit card

### Step 3: Set Up Environment
Create a `.env` file in your project root:

```env
# Choose ONE:
GEMINI_API_KEY=your_key_here
# GROQ_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here
```

### Step 4: Install AI Provider Package
Choose based on which API you selected:

**For Gemini:**
```bash
pip install google-generativeai
```

**For Groq:**
```bash
pip install groq
```

**For OpenAI:**
```bash
pip install openai
```

### Step 5: Run the App
```bash
python app.py
```

Visit: http://localhost:5000/

## Test It!

### Search for a company:
1. Go to home page
2. Enter a company name (e.g., "Maxgen Technologies", "CleverTap")
3. Click "Scan Company"
4. See unique AI-powered analysis for that specific company!

## What Changed?

### Company 1: Maxgen Technologies
```
Risk: HIGH (72%)
⚠️ Multiple negative reviews, registration fee demands detected
Recommendation: AVOID
```

### Company 2: CleverTap
```
Risk: LOW (15%)
✓ Positive online presence, no scam indicators
Recommendation: Safe to apply
```

**Before:** Both showed generic info
**After:** Each gets unique, company-specific analysis ✨

## Features Added

✅ **AI-Powered Analysis** - Real LLM-based insights
✅ **Industry Detection** - Identifies company type automatically
✅ **Risk Categorization** - CRITICAL/HIGH/MEDIUM/LOW/VERY LOW
✅ **Specific Warnings** - Detects fees, fraud, fake certificates
✅ **Works Without API** - Falls back to smart template analysis
✅ **Multiple AI Options** - Gemini, Groq, or OpenAI

## Troubleshooting

### No API key? No problem!
The system automatically falls back to enhanced template-based analysis. You'll still get much better company differentiation than before!

### Still seeing generic responses?
1. Make sure `.env` file is in project root (same folder as `app.py`)
2. Restart the Flask app
3. Check `.env` file format (no quotes around API key)
4. Try a different company name

### API key not working?
- Verify key has no extra spaces
- Check API provider's status page
- Try another provider (Groq is most reliable)

## API Key Recommendations

| Provider | Free Tier | Speed | Accuracy | Setup |
|----------|-----------|-------|----------|-------|
| Gemini   | ✓ Yes     | Good  | Excellent| 1 min |
| Groq     | ✓ Generous| ⚡ Fast | Very Good| 2 min |
| OpenAI   | ✗ Paid    | Good  | Best     | 5 min |

## Full Documentation

For detailed setup and advanced config, see: `AI_SETUP_GUIDE.md`

## Next Step

1. Choose your AI provider
2. Get API key (takes 1 minute)
3. Create `.env` file with key
4. Install provider package
5. Run `python app.py`
6. Try searching for companies!

Your company analysis system is now powered by AI! 🚀
