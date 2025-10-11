import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from urllib.parse import urlparse, urljoin
import requests
import whois
from datetime import datetime
import google.generativeai as genai
from vt import Client as VirusTotalClient
import tldextract
import io # Used to read the online CSV data
from bs4 import BeautifulSoup

# --- DYNAMIC ONLINE BRAND DATABASE LOADING ---
# URL for a public list of top global domains.
# This makes our brand detection far more powerful than a small local file.
BRAND_DATABASE_URL = 'https://raw.githubusercontent.com/cisagov/dotgov-data/main/current-full.csv'
TRUSTED_BRANDS = {}

def load_online_brand_database():
    """
    Fetches and parses a list of top brands from a public URL.
    Falls back to a local file if the online source is unavailable.
    """
    global TRUSTED_BRANDS
    try:
        print("Fetching latest brand database from online source...")
        response = requests.get(BRAND_DATABASE_URL, timeout=10)
        response.raise_for_status() # Raises an exception for bad status codes
        
        # Use pandas to read the CSV data directly from the response text
        brands_df = pd.read_csv(io.StringIO(response.text))
        
        # The column name in this specific CSV is 'Domain Name'
        for domain in brands_df['Domain Name']:
            try:
                brand_keyword = tldextract.extract(domain).domain
                if brand_keyword and brand_keyword not in TRUSTED_BRANDS:
                    TRUSTED_BRANDS[brand_keyword.lower()] = domain.lower()
            except Exception:
                continue
        
        print(f"Successfully loaded {len(TRUSTED_BRANDS)} brands from the online database.")

    except Exception as e:
        print(f"WARNING: Could not fetch online brand database. Reason: {e}")
        print("Falling back to local 'brands.csv' file.")
        try:
            brands_df = pd.read_csv('brands.csv')
            TRUSTED_BRANDS = {row['brand_keyword']: row['official_domain'] for index, row in brands_df.iterrows()}
            print(f"Successfully loaded {len(TRUSTED_BRANDS)} brands from local backup.")
        except Exception as local_e:
            print(f"FATAL: Could not load local brands.csv either. Brand impersonation checks will fail. Details: {local_e}")
            TRUSTED_BRANDS = {}

# --- API KEY CONFIGURATION & API SETUP ---
VT_API_KEY = os.environ.get("VT_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

vt_client = VirusTotalClient(VT_API_KEY) if VT_API_KEY else None
llm = None
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        llm = genai.GenerativeModel('gemini-2.5-flash')
        print("Gemini API configured successfully.")
    except Exception as e:
        print(f"WARNING: Could not configure Gemini API. Details: {e}")
if not vt_client:
    print("WARNING: VirusTotal API key not set.")

# --- HELPER FUNCTION FOR ML MODEL TRAINING ---
def extract_features_for_training(url):
    features = []
    try:
        hostname = urlparse(url).netloc
        features.extend([len(url), len(hostname), url.count('.'), url.count('-')])
        features.extend([1 if '@' in url else 0, hostname.count('.')])
        features.append(1 if re.match(r"\d{1,3}(\.\d{1,3}){3}", hostname) else 0)
        suspicious_keywords = ['login', 'secure', 'bank', 'account', 'verify', 'password']
        features.append(1 if any(keyword in url.lower() for keyword in suspicious_keywords) else 0)
    except Exception: return [0] * 8
    return features

# --- ML MODEL TRAINING ---
print("Training phishing detection model...")
try:
    df = pd.read_csv('dataset.csv')
    X = [extract_features_for_training(url) for url in df['url']]
    y = [1 if str(label).strip().lower() == 'phishing' else 0 for label in df['type']]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    print(f"Model Accuracy: {accuracy_score(y_test, model.predict(X_test)):.2f}")
    print("Model training complete.")
except Exception as e:
    print(f"FATAL ERROR during model training: {e}")
    exit()

# --- LIVE ANALYSIS HELPER FUNCTIONS ---
def get_domain_age(domain_name):
    try:
        w = whois.whois(domain_name)
        creation_date = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
        if creation_date: return (datetime.now() - creation_date).days
    except Exception: pass
    return -1

def check_brand_impersonation(url):
    try:
        extracted_url = tldextract.extract(url)
        domain = extracted_url.domain.lower()
        subdomain = extracted_url.subdomain.lower()
        registered_domain = extracted_url.top_domain_under_public_suffix.lower()

        for brand, official_domain in TRUSTED_BRANDS.items():
            if brand in domain or brand in subdomain:
                if registered_domain != official_domain:
                    return True, f"Impersonating the brand '{brand.title()}'"
    except Exception: pass
    return False, ""

# --- Load the database on startup ---
load_online_brand_database()

# --- FLASK API SERVER ---
app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze_url():
    data = request.get_json()
    url_to_check = data.get('url')
    if not url_to_check: return jsonify({'error': 'URL not provided'}), 400

    reasons = []
    is_phishing = False

    # Layer 1: Brand Impersonation (now uses the powerful online list)
    impersonating, brand_reason = check_brand_impersonation(url_to_check)
    if impersonating:
        is_phishing = True
        reasons.append(brand_reason)

    # Layer 2: Global Threat Intelligence (VirusTotal)
    if not is_phishing and vt_client:
        try:
            url_id = requests.utils.quote(url_to_check, safe='')
            analysis = vt_client.get_object(f"/urls/{url_id}")
            malicious_votes = analysis.last_analysis_stats['malicious']
            if malicious_votes > 2:
                is_phishing = True
                reasons.append(f"Flagged by {malicious_votes} security vendors on VirusTotal.")
        except Exception:
            pass 

    # Layer 3: Live Analysis & Contextual AI
    if not is_phishing:
        try:
            hostname = urlparse(url_to_check).netloc
            domain_age = get_domain_age(hostname)
            if 0 <= domain_age < 90:
                is_phishing = True
                reasons.append(f"Site is very new ({domain_age} days old).")

            if llm and not is_phishing:
                response = requests.get(url_to_check, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(response.content, 'html.parser')
                page_text = soup.get_text(separator=' ', strip=True)
                prompt = f"Analyze the following website text for signs of a scam (e.g., franchise scam, job offer scam, fake login, urgency). Respond with a single word: 'High Risk' if scam language is present, otherwise 'Low Risk'. Text: '{page_text[:3000]}'"
                ai_response = llm.generate_content(prompt)
                if "High Risk" in ai_response.text:
                    is_phishing = True
                    reasons.append("AI detected suspicious language on the page (potential scam).")

            if not is_phishing:
                url_features = extract_features_for_training(url_to_check)
                ai_confidence = model.predict_proba([url_features])[0][1]
                if ai_confidence > 0.8:
                    is_phishing = True
                    reasons.append("AI model detected suspicious URL patterns.")

        except Exception as e:
            reasons.append(f"Could not perform live analysis: {e}")

    # --- Final Verdict ---
    if is_phishing:
        final_status = "Phishing"
        message = ". ".join(reasons) if reasons else "High risk detected."
    else:
        final_status = "Legitimate"
        message = "This site appears to be safe."
        reasons.append("No major risk factors detected by the analysis engine.")

    result = {"status": final_status, "message": message, "reasons": reasons}
    return jsonify(result)

# The /analyze-text endpoint is kept for the extension's second tab.
@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    if not llm:
        return jsonify({"error": "Gemini API not configured on the server."}), 500
        
    data = request.get_json()
    text_to_check = data.get('text')
    if not text_to_check: return jsonify({'error': 'No text provided'}), 400

    prompt = f"""
    Analyze the following text for signs of a phishing or social engineering scam. 
    Focus on tactics like manufactured urgency, suspicious links, grammatical errors, and unusual requests.
    Provide a verdict ("Safe" or "High Risk") and a brief, one-sentence explanation.
    Your response must be a valid JSON object with two keys: "verdict" and "explanation".

    Text to analyze: --- {text_to_check} ---
    """
    
    try:
        response = llm.generate_content(prompt)
        clean_response = response.text.strip().replace("```json", "").replace("```", "")
        return clean_response, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({"error": f"Failed to analyze text with AI: {e}"}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)

