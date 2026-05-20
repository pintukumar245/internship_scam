# 🛡️ Internship Scam Shield - AI-Powered Company Analyzer

**Advanced company analysis system with AI-powered unique insights to help students avoid internship scams.**

> **NEW:** Now with AI! Each company search returns **unique, intelligent analysis** instead of generic responses.

---

## 🎯 Problem Solved

Students often can't distinguish between legitimate internships and scams. This system analyzes companies for:
- 💰 Hidden fee demands
- 📜 Fake certificates
- 🚩 Scam complaints  
- ⚠️ Red flags in hiring practices

**Our Enhancement:** AI now generates **company-specific insights** using advanced language models.

---

## ✨ What's New (AI Upgrade)

### Before ❌
- All companies showed similar generic information
- Hard to distinguish scams from legitimate companies
- Vague recommendations

### After ✅
- **Unique analysis for each company**
- **Industry-specific insights** (Ed-Tech, SaaS, Finance, etc.)
- **Risk categorization** (CRITICAL/HIGH/MEDIUM/LOW)
- **Specific warnings** (fees, fraud, certificates)
- **Actionable recommendations**

---

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Free AI API Key
Choose ONE:
- **Gemini** (Recommended): https://ai.google.dev/
- **Groq** (Fast): https://console.groq.com/
- **OpenAI** (Paid): https://platform.openai.com/

### 3. Create `.env` File
```env
GEMINI_API_KEY=your_key_here
# Or:
# GROQ_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here
```

### 4. Install AI Provider
```bash
# For Gemini:
pip install google-generativeai

# For Groq:
pip install groq

# For OpenAI:
pip install openai
```

### 5. Run
```bash
python app.py
```

Visit: **http://localhost:5000/**

---

## 📋 Features

### 🤖 AI-Powered Analysis
- Uses LLM (Large Language Models) for company analysis
- Generates unique insights per company
- Understands context and nuances
- Works with or without API key

### 🎯 Smart Risk Detection
- **CRITICAL RISK** (80%+): Multiple scam indicators
- **HIGH RISK** (60-79%): Significant concerns found
- **MEDIUM RISK** (40-59%): Mixed signals detected
- **LOW RISK** (20-39%): Few red flags
- **VERY LOW RISK** (0-19%): Appears safe

### 🏢 Industry Detection
Automatically identifies company type:
- 🎓 Ed-Tech (Training, Courses)
- 💻 SaaS (Software/Cloud)
- 💰 Finance (Banking, Crypto)
- 📱 Ecommerce (Online Stores)
- 🎨 Marketing (Digital Marketing)
- 💼 IT Services (Development, Outsourcing)
- 🏥 Healthcare (Medical)
- And more...

### ⚠️ Threat Detection
Flags specific risks:
- 💸 Fee/Registration Charge Demands
- 📜 Fake Certificate Issues
- 🚩 Fraud Allegations
- 💬 Student Complaints
- 📊 Low Online Presence

### ✅ Verification Features
- **Web Search Integration**: Real-time company data
- **Wikipedia Info**: Official company descriptions
- **Local Database**: Historical scam records
- **DuckDuckGo API**: Company overview & logos
- **Student Reviews**: Community feedback

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **QUICK_START.md** | 5-minute setup guide (START HERE!) |
| **AI_SETUP_GUIDE.md** | Detailed AI configuration |
| **BEFORE_AFTER_COMPARISON.md** | See the improvements |
| **IMPLEMENTATION_SUMMARY.md** | Technical overview |

---

## 🛠️ How It Works

```
User enters company name
         ↓
Scrapes web data (Bing, Wikipedia, DuckDuckGo)
         ↓
Calculates scam risk indicators
         ↓
Sends to AI (if API key available)
         ↓
AI Generates unique company-specific analysis ← NEW!
         ↓
Returns risk score, warnings, and recommendations
         ↓
User sees detailed company profile
```

---

## 📊 Example Analysis

### Example 1: Maxgen Technologies (Scam)
```
AI Analysis: Maxgen Technologies - Ed-Tech Company
Team Size: 51-200 employees

🚨 CRITICAL RISK (72%): Multiple red flags detected
- Registration fee demands reported
- Fake certificate allegations
- Student complaints found

⚠️ Specific Threats:
- Money/fee demands found
- Scam/fraud allegations detected

📌 Recommendation:
AVOID this company. Search for better alternatives.
```

### Example 2: CleverTap (Legitimate)
```
AI Analysis: CleverTap - SaaS Platform  
Team Size: 201-500 employees

✓ VERY LOW RISK (12%): Safe to apply
- Strong online presence
- No active scam indicators
- Positive reviews found

✅ No major red flags detected
👍 Positive student feedback found

📌 Recommendation:
Company appears safe. Always verify independently
before joining.
```

---

## 🔧 Configuration

### Environment Variables (.env)
```env
# Choose ONE AI provider:

# Google Gemini (Recommended)
GEMINI_API_KEY=your_key_here

# Groq (Alternative)
# GROQ_API_KEY=your_key_here

# OpenAI (Paid)
# OPENAI_API_KEY=your_key_here
```

### AI Provider Comparison

| Feature | Gemini | Groq | OpenAI |
|---------|--------|------|--------|
| Free Tier | ✓ | ✓ | ✗ |
| Speed | Good | ⚡ Very Fast | Good |
| Accuracy | Excellent | Very Good | Best |
| Setup Time | 1 min | 2 min | 5 min |
| Recommended | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 📱 Usage

### Search for a Company
1. Visit http://localhost:5000/
2. Enter company name
3. Click "Scan Company"
4. Get instant AI-powered analysis

### View Public Reports
- Reports from other students
- Community feedback
- Scam complaints

### Submit Your Report
- Share your experience
- Help other students
- Report scams

---

## 🐛 Troubleshooting

### Issue: Generic analysis shown
**Solution:** 
1. Check `.env` file exists in project root
2. Verify API key is correct (no extra spaces)
3. Restart Flask app

### Issue: API not responding
**Solution:**
1. Check internet connection
2. Try different AI provider
3. Verify API key validity
4. System will auto-fallback to template analysis

### Issue: Want to use without API key?
**Solution:** Works fine! Enhanced template analysis activates automatically.

---

## 🎓 Learning Resources

### For Setup:
- See `QUICK_START.md` for fast setup
- See `AI_SETUP_GUIDE.md` for detailed guide

### To See Improvements:
- See `BEFORE_AFTER_COMPARISON.md` for examples

### Technical Details:
- See `IMPLEMENTATION_SUMMARY.md` for architecture
- See `search_engine.py` for code

---

## 📦 Requirements

- Python 3.7+
- Flask
- Beautiful Soup 4 (web scraping)
- TensorFlow/Keras (diabetes predictor)
- Requests (HTTP library)
- python-dotenv (environment config)

Optional (for AI):
- google-generativeai (Gemini)
- groq (Groq API)
- openai (OpenAI)

See `requirements.txt` for complete list.

---

## 🗂️ Project Structure

```
project/
├── app.py                          # Flask application
├── search_engine.py                # AI analysis engine (enhanced!)
├── requirements.txt                # Dependencies
├── .env.example                    # Configuration template
├── QUICK_START.md                  # Setup guide ⭐ START HERE
├── AI_SETUP_GUIDE.md              # Detailed AI setup
├── BEFORE_AFTER_COMPARISON.md     # Shows improvements
├── IMPLEMENTATION_SUMMARY.md      # Technical overview
├── templates/                      # HTML templates
│   ├── index.html                 # Home page
│   ├── dashboard.html             # Company analysis
│   ├── diabetes.html              # Diabetes predictor
│   └── reports_list.html          # Public reports
├── static/                        # CSS, JavaScript
│   └── css/
│       └── style.css              # Styling
├── data/                          # Database files
│   ├── user_reviews.json          # Student reviews
│   └── scam_reports.json          # Scam complaints
└── templates/
    └── internship_scam_analysis_data.csv  # Company database
```

---

## 🚀 Deployment

### Local Development
```bash
python app.py
# http://localhost:5000/
```

### Production (Example with Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 🤝 Contributing

Want to improve the analysis?
1. Fork the project
2. Create feature branch
3. Add improvements
4. Submit pull request

---

## 📞 Support

Stuck? Check these:
1. **QUICK_START.md** - Most common questions answered
2. **AI_SETUP_GUIDE.md** - Detailed documentation
3. **Code comments** - search_engine.py is well-commented

---

## ⚖️ Disclaimer

This tool provides analysis based on available online data. Always:
- ✓ Verify information independently
- ✓ Research company thoroughly
- ✓ Never pay upfront fees
- ✓ Contact company directly for confirmation
- ✓ Consult trusted sources

---

## 📈 Future Enhancements

- [ ] Mobile app version
- [ ] Real-time company updates
- [ ] Direct company review submission
- [ ] Video verification interviews
- [ ] Blockchain-verified certificates

---

## 📄 License

MIT License - Free to use and modify

---

## 🎯 Quick Links

| Need | Link |
|------|------|
| **Quick Setup** | See QUICK_START.md |
| **Detailed Setup** | See AI_SETUP_GUIDE.md |
| **See Improvements** | See BEFORE_AFTER_COMPARISON.md |
| **Technical Info** | See IMPLEMENTATION_SUMMARY.md |
| **Run App** | `python app.py` |
| **Get API Key** | https://ai.google.dev/ |

---

## 🎉 Ready to Start?

```bash
# 1. Install
pip install -r requirements.txt

# 2. Get API key (free from Gemini)
# https://ai.google.dev/

# 3. Setup
echo "GEMINI_API_KEY=your_key" > .env
pip install google-generativeai

# 4. Run
python app.py

# 5. Open browser
# http://localhost:5000/

# 6. Search a company and see AI-powered analysis! 🚀
```

---

**Help students avoid internship scams with AI-powered company analysis!** 🛡️

For questions or improvements, check the documentation files above.

*Version: 2.0 (AI-Powered)*
*Last Updated: May 20, 2026*
