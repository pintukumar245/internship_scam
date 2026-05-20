import os
import csv
import re
import requests
from bs4 import BeautifulSoup
import urllib.parse
import json

# Path to the local CSV database
CSV_PATH = os.path.join(os.path.dirname(__file__), "templates", "internship_scam_analysis_data.csv")

# AI Configuration - Try multiple LLM providers
AI_PROVIDER = "gemini"  # Options: "gemini", "groq", "openai"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def clean_company_name(name):
    if not name:
        return ""
    # Remove "Actively hiring" and clean up whitespace
    name = re.sub(r'Actively hiring', '', name, flags=re.IGNORECASE)
    # Remove multiple spaces/newlines
    name = re.sub(r'\s+', ' ', name)
    return name.strip()

def get_domain_from_url(url):
    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except:
        return ""

def search_local_db(company_name):
    cleaned_query = clean_company_name(company_name).lower()
    if not cleaned_query:
        return None
        
    results = []
    if os.path.exists(CSV_PATH):
        try:
            with open(CSV_PATH, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    db_company = clean_company_name(row.get('Company', ''))
                    if cleaned_query in db_company.lower():
                        results.append({
                            'title': row.get('Title', 'N/A'),
                            'company': db_company,
                            'location': row.get('Location', 'N/A'),
                            'stipend': row.get('Stipend', 'N/A'),
                            'source': row.get('Source', 'Internshala'),
                            'flag': row.get('Scam_Indicator_Flag', 'Needs Review')
                        })
        except Exception as e:
            print(f"Error reading local CSV database: {e}")
            
    return results

def fetch_bing_snippets(query):
    """
    Fetch web search snippets from Bing.
    This works reliably when run from a local user's network.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
    snippets = []
    
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for standard search results in b_algo class
            lis = soup.find_all('li', class_='b_algo')
            for li in lis:
                title_elem = li.find('h2')
                link_elem = title_elem.find('a') if title_elem else li.find('a')
                snippet_elem = li.find('p') or li.find('div', class_='b_caption')
                
                if title_elem and link_elem:
                    title = title_elem.text.strip()
                    link = link_elem.get('href', '')
                    snippet = snippet_elem.text.strip() if snippet_elem else ""
                    
                    if link.startswith('http'):
                        snippets.append({
                            'title': title,
                            'link': link,
                            'snippet': snippet
                        })
            
            # Fallback if no b_algo found (check for simple h2 headers with links)
            if not snippets:
                for h2 in soup.find_all('h2'):
                    link_elem = h2.find('a')
                    if link_elem:
                        title = h2.text.strip()
                        link = link_elem.get('href', '')
                        if link.startswith('http') and not 'bing.com' in link:
                            snippets.append({
                                'title': title,
                                'link': link,
                                'snippet': 'Web search result'
                            })
    except Exception as e:
        print(f"Error fetching Bing snippets: {e}")
        
    return snippets

def fetch_duckduckgo_api(company_name):
    """
    Query the DuckDuckGo Instant Answer API for official logo and website info.
    """
    url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(company_name)}&format=json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'abstract': data.get('AbstractText', ''),
                'website': data.get('OfficialWebsite', '') or data.get('AbstractURL', ''),
                'logo': data.get('Image', '')
            }
    except Exception as e:
        print(f"Error fetching from DDG API: {e}")
    return {}

def calculate_scam_score(company_name, snippets, db_records):
    """
    Heuristics to calculate a realistic scam percentage score.
    Returns: (score, breakdown, details)
    """
    score = 0
    breakdown = {
        'fee_demand': 0,
        'certificate_validity': 0,
        'online_presence': 0,
        'review_sentiment': 0
    }
    details = []
    
    # 1. Local Database checks
    if db_records:
        has_needs_review = any(r['flag'] == 'Needs Review' for r in db_records)
        unpaid = any('unpaid' in str(r['stipend']).lower() for r in db_records)
        
        # Check stipends
        low_stipend = any(re.search(r'1,000|1,100|1,200|1,500', str(r['stipend'])) for r in db_records)
        
        if unpaid:
            details.append("Company offers unpaid internships. Beware of hidden work hours without pay.")
            breakdown['certificate_validity'] += 20
        if low_stipend:
            details.append("Very low stipend records found (< 2000 INR/month). Check if learning value matches the low payout.")
            breakdown['certificate_validity'] += 15

    # 2. Text Analysis of Web Search Snippets
    all_text = " ".join([s['title'] + " " + s['snippet'] for s in snippets]).lower()
    
    # Keyword Lists
    fee_keywords = ['fee', 'pay money', 'security deposit', 'registration fee', 'training fee', 'charges', 'charge', 'demand money', 'paisa']
    cert_keywords = ['fake certificate', 'fraud certificate', 'no value', 'selling certificate', 'sell certificate', 'fake internship']
    scam_keywords = ['scam', 'fraud', 'complaint', 'fake', 'avoid', 'trap', 'cheated', 'worst', 'lose money', 'frod']
    positive_keywords = ['legit', 'good company', 'genuine', 'happy', 'great learning', 'best internship', 'trusted', 'verify']

    # Match Counts
    fee_matches = sum(1 for kw in fee_keywords if kw in all_text)
    cert_matches = sum(1 for kw in cert_keywords if kw in all_text)
    scam_matches = sum(1 for kw in scam_keywords if kw in all_text)
    positive_matches = sum(1 for kw in positive_keywords if kw in all_text)

    # Score calculation
    # Fee demands (Max 40 points)
    if fee_matches > 0:
        score_add = min(40, fee_matches * 15)
        breakdown['fee_demand'] = score_add
        details.append(f"Found references indicating money/fee demands ({fee_matches} mentions). Legit internships NEVER ask students for money.")
    
    # Certificate fraud (Max 30 points)
    if cert_matches > 0:
        score_add = min(30, cert_matches * 15)
        breakdown['certificate_validity'] = min(100, breakdown['certificate_validity'] + score_add)
        details.append(f"Flagged for fake/invalid internship certificate practices ({cert_matches} mentions).")

    # Review sentiment & Scam mentions (Max 30 points)
    if scam_matches > 0:
        score_add = min(30, scam_matches * 10)
        breakdown['review_sentiment'] = score_add
        details.append(f"Negative reviews and scam complaints detected online ({scam_matches} mentions).")
        
    # Online presence check (Max 20 points)
    if len(snippets) < 3:
        breakdown['online_presence'] = 50
        details.append("Very low online presence. Real companies usually have multiple verified news articles, LinkedIn posts, or websites.")
    else:
        # Check if domains match major review sites with negative context
        complaints_sites = ['consumercomplaints', 'mouthshut', 'quora', 'reddit']
        site_matches = sum(1 for s in snippets if any(cs in s['link'] for cs in complaints_sites))
        if site_matches > 0:
            breakdown['online_presence'] = min(100, site_matches * 20)
            details.append(f"Discussions found on student forums / complaint portals like Quora/Reddit/MouthShut ({site_matches} links).")

    # Calculate overall scam score
    total_raw = breakdown['fee_demand'] * 0.40 + breakdown['certificate_validity'] * 0.25 + breakdown['review_sentiment'] * 0.20 + breakdown['online_presence'] * 0.15
    score = int(min(100, total_raw))

    # Apply positive offsets
    if positive_matches > 2 and score > 20:
        score = max(10, score - (positive_matches * 4))
        details.append(f"Note: Some positive student feedback was also found online.")

    # Cap if there is definite proof of fee demands
    if breakdown['fee_demand'] >= 30 and score < 60:
        score = 65

    # Safe defaults if no warning indicators matched
    if not details:
        score = 5 # 5% baseline risk
        details.append("No active scam indicators found online. The company appears safe, but always verify before paying any money.")

    return score, breakdown, details

def estimate_employee_size(company_name, snippets, ddg_info):
    """
    Search snippets for employee size indicators, with fallback estimates.
    """
    # First check hardcoded database
    massive_firms = {
        'google': '190,000+ employees',
        'microsoft': '230,000+ employees',
        'amazon': '1,500,000+ employees',
        'meta': '67,000+ employees',
        'apple': '161,000+ employees',
        'tcs': '613,000+ employees',
        'infosys': '314,000+ employees',
        'wipro': '250,000+ employees',
        'cognizant': '376,000+ employees',
        'accenture': '738,000+ employees',
        'capgemini': '325,000+ employees',
        'ibm': '290,000+ employees',
        'oracle': '160,000+ employees',
        'salesforce': '80,000+ employees',
        'adobe': '24,000+ employees',
        'cisco': '80,000+ employees',
        'intel': '110,000+ employees',
        'nvidia': '28,000+ employees'
    }
    
    company_lower = company_name.lower().strip()
    # Check against hardcoded database
    for firm_name, size in massive_firms.items():
        if firm_name in company_lower:
            return size
    
    # Try finding patterns in snippets like "10-50 employees", "500+", "size: 50-100"
    all_text = " ".join([s['title'] + " " + s['snippet'] for s in snippets]).lower()
    
    patterns = [
        r'(\d+[\s-]+\d+)\s+employees',
        r'(\d+[,.]?\d*)\+\s+employees',
        r'employee size:\s*(\d+[\s-]+\d+)',
        r'size of\s*(\d+[\s-]+\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, all_text)
        if match:
            return match.group(1) + " employees"
        
    # Check if there is decent online presence
    if len(snippets) > 6:
        return "201-500 employees (Estimated)"
    elif len(snippets) >= 3:
        return "51-200 employees (Estimated)"
    else:
        return "1-50 employees (Small team or Startup)"

def find_company_logo(company_name, snippets, ddg_info):
    """
    Generate or fetch a company logo.
    Uses Clearbit API if a domain is resolved, else a beautiful letter-logo SVG pattern.
    """
    logo_url = ddg_info.get('logo') if ddg_info else None
    if logo_url:
        return logo_url
        
    # Attempt to extract a domain from search snippets
    domain = ""
    # Filter snippets to find company official websites
    for s in snippets:
        link = s['link'].lower()
        if 'linkedin.com' not in link and 'facebook.com' not in link and 'glassdoor' not in link and 'indeed' not in link and 'mouthshut' not in link and 'complaints' not in link:
            # Check if domain has company name keywords
            domain_cand = get_domain_from_url(s['link'])
            if domain_cand:
                domain = domain_cand
                break
                
    if domain:
        # Use Clearbit Logo API which is free and high quality
        return f"https://logo.clearbit.com/{domain}"
        
    # Fallback to a letter-logo template generator in HTML/CSS, which is handled dynamically in the frontend.
    return None

def fetch_wikipedia_summary(company_name):
    """Fetch accurate company info from Wikipedia if available."""
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(company_name)}"
        headers = {'User-Agent': 'ScamShieldApp/1.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json().get('extract', '')
    except:
        pass
    return ""

def call_gemini_api(company_name, snippets_text, risk_score):
    """Call Google Gemini API for AI-powered company analysis."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""Analyze the following company and provide a concise, Hindi-English mixed response (Hinglish):

Company: {company_name}
Risk Score: {risk_score}%
Web Data Summary: {snippets_text[:1000]}

Generate a 2-3 sentence professional analysis about:
1. What the company does
2. If it's legitimate or has red flags
3. A brief recommendation for internship seekers

Keep it in Hinglish (Hindi words written in English) and be direct."""
        
        response = model.generate_content(prompt)
        return f"AI Insight: {response.text}"
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None

def call_groq_api(company_name, snippets_text, risk_score):
    """Call Groq API (free LLM alternative) for company analysis."""
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""Analyze this company for internship seekers:
Company: {company_name}
Risk Score: {risk_score}%
Web Data: {snippets_text[:800]}

Provide 2-3 sentences in Hinglish about: 
- What they do
- Legitimacy status
- Recommendation

Keep it brief and direct."""
        
        payload = {
            "model": "mixtral-8x7b-32768",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            return f"AI Insight: {content}"
    except Exception as e:
        print(f"Groq API error: {e}")
        return None

def call_openai_api(company_name, snippets_text, risk_score):
    """Call OpenAI GPT API for company analysis."""
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""Analyze this company for Indian internship seekers:
Company: {company_name}
Risk Score: {risk_score}%
Web Data: {snippets_text[:800]}

Provide 2-3 sentences in Hinglish about:
- Company description
- Legitimacy assessment
- Recommendation

Be concise and direct."""
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            return f"AI Insight: {content}"
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

def generate_ai_insight_with_llm(company_name, score, employee_size, snippets, ddg_abstract, wiki_abstract):
    """Enhanced AI insight generation using LLM API."""
    
    # If we have Wikipedia or DuckDuckGo abstract, use it as base
    if wiki_abstract:
        base_info = f"AI Overview: {wiki_abstract}"
    elif ddg_abstract:
        base_info = f"AI Overview: {ddg_abstract}"
    else:
        base_info = f"Company: {company_name}"
    
    # Prepare snippets text for LLM analysis
    snippets_text = " ".join([f"{s['title']}: {s['snippet']}" for s in snippets[:5]])
    
    if not snippets_text.strip():
        snippets_text = f"No online presence found for {company_name}"
    
    # Try to get AI-powered analysis
    ai_response = None
    
    if GEMINI_API_KEY:
        ai_response = call_gemini_api(company_name, snippets_text, score)
    elif GROQ_API_KEY:
        ai_response = call_groq_api(company_name, snippets_text, score)
    elif OPENAI_API_KEY:
        ai_response = call_openai_api(company_name, snippets_text, score)
    
    # If LLM API fails or no API key, use enhanced template-based analysis
    if not ai_response:
        ai_response = generate_ai_insight(company_name, score, employee_size, snippets, ddg_abstract, wiki_abstract)
    
    return ai_response

def generate_ai_insight(company_name, score, employee_size, snippets, ddg_abstract, wiki_abstract):
    """Generates a dynamic, company-specific summary based on collected signals."""
    
    # Start with accurate company info if available
    if wiki_abstract:
        wiki_desc = wiki_abstract.split('. ')[0]  # First sentence
        return f"ℹ️ {company_name}: {wiki_abstract}\n\n✅ Employee Size: {employee_size}\n\n🎯 Internship Safety: {score}% Risk | " + (
            "🚨 HIGH RISK - Avoid" if score > 60 else "⚠️ MEDIUM RISK - Verify" if score > 35 else "✓ SAFE - Legitimate"
        )
    
    if ddg_abstract:
        ddg_desc = ddg_abstract.split('. ')[0]  # First sentence
        return f"ℹ️ {company_name}: {ddg_abstract}\n\n✅ Employee Size: {employee_size}\n\n🎯 Internship Safety: {score}% Risk | " + (
            "🚨 HIGH RISK - Avoid" if score > 60 else "⚠️ MEDIUM RISK - Verify" if score > 35 else "✓ SAFE - Legitimate"
        )
        
    if not snippets:
        if score > 70:
            return f"⚠️ AI Analysis: '{company_name}' ke liye internet pe bahut ghatiya reviews aur complaints mil rahe hain (Risk: {score}%). Ye scam ho sakti hai - paise mat dein!\n📌 Action: Avoid this company, search for alternatives."
        elif score > 40:
            return f"📊 AI Analysis: '{company_name}' ke baare mein mixed information hai. Employee size: {employee_size}. Apply karne se pehle kuch complaints dekhe gaye hain. Careful rahein.\n📌 Action: Verify independently before applying."
        else:
            return f"✓ AI Analysis: '{company_name}' ka record filhal safe lag raha hai. Estimated team: {employee_size}. Phir bhi pehle verify karein aur koi upfront fees nahin den.\n📌 Action: Safe to apply - always verify credentials."
    
    # Analyze snippets for detailed company-specific insights
    all_text = " ".join([s['snippet'] for s in snippets]).lower()
    all_titles = " ".join([s['title'] for s in snippets]).lower()
    
    # Extract key info from snippets
    company_info_snippets = []
    for s in snippets[:3]:
        if s['snippet'].strip():
            company_info_snippets.append(s['snippet'][:150])
    
    company_context = " ".join(company_info_snippets) if company_info_snippets else f"No detailed info found for {company_name}"
    
    # Check for company type/industry
    industry_markers = {
        'fintech': ['banking', 'payment', 'financial', 'trading', 'crypto', 'forex'],
        'ed-tech': ['education', 'learning', 'course', 'training', 'skill', 'certificate'],
        'saas': ['software', 'cloud', 'platform', 'analytics', 'management', 'saas'],
        'ecommerce': ['ecommerce', 'online store', 'shop', 'retail', 'marketplace'],
        'consulting': ['consulting', 'advisory', 'management consulting', 'strategy'],
        'marketing': ['marketing', 'digital marketing', 'seo', 'agency', 'social media'],
        'it services': ['it services', 'software development', 'outsourcing', 'development'],
        'healthcare': ['healthcare', 'medical', 'pharmacy', 'hospital', 'clinic']
    }
    
    detected_industry = "Business"
    for industry, keywords in industry_markers.items():
        if any(kw in all_text for kw in keywords):
            detected_industry = industry.title()
            break
    
    # Build risk-based analysis with company context
    insight = f"🏢 {company_name} - {detected_industry} Sector\n"
    insight += f"👥 Team Size: {employee_size}\n"
    insight += f"📊 Web Presence: {len(snippets)} results found\n\n"
    insight += f"📰 Overview: {company_context[:200]}...\n\n"
    
    # Risk assessment in Hinglish
    if score >= 80:
        insight += f"🚨 CRITICAL RISK ({score}%): Multiple red flags detected - fee demands, fake certificates, student complaints. AVOID THIS COMPANY. Do not pay any money!"
        
    elif score >= 60:
        insight += f"⚠️ HIGH RISK ({score}%): Several negative reviews and complaints found. Potential scam indicators including registration fees or certificate fraud. Be very cautious."
        
    elif score >= 40:
        insight += f"⚡ MEDIUM RISK ({score}%): Mixed online sentiment. Some student complaints detected. Verify all claims independently before applying. Never pay upfront fees."
        
    elif score >= 20:
        insight += f"✓ LOW RISK ({score}%): Generally positive online presence with minimal complaints. Appears relatively safe based on available data. Standard verification recommended."
        
    else:
        insight += f"✓ VERY LOW RISK ({score}%): Strong online presence with few red flags. This appears to be a legitimate company based on data analysis."
    
    # Add specific warning flags
    if 'fee' in all_text or 'registration' in all_text or 'deposit' in all_text:
        insight += "\n ⚠️ WARNING: Fee/money demands reported online"
    
    if 'fake' in all_text or 'fraud' in all_text or 'scam' in all_text:
        insight += "\n 🚩 ALERT: Scam/fraud allegations detected in online discussions"
        
    if 'good' in all_text or 'great' in all_text or 'best' in all_text or 'excellent' in all_text:
        insight += "\n 👍 NOTE: Positive student feedback also found online"
    
    # Add recommendation
    insight += "\n\n📌 RECOMMENDATION: "
    if score > 60:
        insight += f"Avoid this company. Search for verified alternatives with better reputation."
    elif score > 35:
        insight += f"Proceed with caution. Contact current employees, verify certificate validity, and never pay registration fees upfront."
    else:
        insight += f"Safe to apply. Still verify their official website, check employee LinkedIn profiles, and confirm internship terms."
    
    return insight

def analyze_company(company_name):
    """
    Main entry point for company scan with AI-powered analysis.
    """
    if not company_name:
        return None
        
    cleaned_name = clean_company_name(company_name)
    
    # 1. Fetch Local Database Records
    db_records = search_local_db(cleaned_name)
    
    # 2. Query APIs for accurate descriptions
    ddg_info = fetch_duckduckgo_api(cleaned_name)
    wiki_info = fetch_wikipedia_summary(cleaned_name)
    
    # 3. Perform Live Search Queries
    overview_snippets = fetch_bing_snippets(f"{cleaned_name} company overview news website")
    scam_snippets = fetch_bing_snippets(f"{cleaned_name} internship scam reviews fraud money fee")
    
    # Combine snippets
    all_snippets = []
    seen_links = set()
    for s in overview_snippets + scam_snippets:
        if s['link'] not in seen_links:
            seen_links.add(s['link'])
            all_snippets.append(s)
            
    # 4. Calculate Scam Score & Indicators
    scam_score, risk_breakdown, scam_details = calculate_scam_score(cleaned_name, all_snippets, db_records)
    
    # 5. Get Employee Size
    employee_size = estimate_employee_size(cleaned_name, all_snippets, ddg_info)
    
    # 6. Resolve Logo Image
    logo_url = find_company_logo(cleaned_name, all_snippets, ddg_info)
    
    # 7. Formulate AI-Powered Company Description (with LLM fallback)
    description = generate_ai_insight_with_llm(
        company_name=cleaned_name,
        score=scam_score,
        employee_size=employee_size,
        snippets=all_snippets,
        ddg_abstract=ddg_info.get('abstract', ''),
        wiki_abstract=wiki_info
    )
        
    # Website Link
    website = ddg_info.get('website', '')
    if not website and all_snippets:
        for s in all_snippets:
            if 'linkedin.com' not in s['link'] and 'glassdoor' not in s['link']:
                website = s['link']
                break
                
    return {
        'name': cleaned_name,
        'description': description,
        'logo_url': logo_url,
        'website': website,
        'employee_size': employee_size,
        'scam_score': scam_score,
        'risk_breakdown': risk_breakdown,
        'scam_details': scam_details,
        'snippets': all_snippets[:6],
        'local_records': db_records
    }
