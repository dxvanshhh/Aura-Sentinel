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
from bs4 import BeautifulSoup
import whois
from datetime import datetime
import imagehash
from PIL import Image
import tldextract
import jsbeautifier
import ssl
import socket
from OpenSSL import SSL
import google.generativeai as genai

# --- DATABASE OF TRUSTED BRANDS ---
# In a real app, this would be a larger, external database.
TRUSTED_BRAND_LOGOS = {
    "google": imagehash.hex_to_hash('ffc3818181c3ffff'),
    "facebook": imagehash.hex_to_hash('ffc3c1e0e0c1c3ff'),
    "microsoft": imagehash.hex_to_hash('f7f7a5a5a5a5f7f7')
}

# --- HELPER FUNCTION FOR MODEL TRAINING ---
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

# --- ULTIMATE EDITION: Advanced Live Analysis Functions ---

def get_domain_age(domain_name):
    try:
        w = whois.whois(domain_name)
        creation_date = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
        if creation_date: return (datetime.now() - creation_date).days
    except Exception: pass
    return -1

def check_ssl_certificate(hostname):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                issuer = dict(x[0] for x in cert['issuer'])
                # Legitimate sites usually have well-known issuers
                if "Let's Encrypt" in issuer.get('organizationName', ''):
                    return 1 # Flag: Basic, free SSL often used by phishing sites
                return 0 # Flag: Reputable SSL issuer
    except Exception: pass
    return 1 # Flag: SSL check failed or no SSL

def analyze_page_details(soup, base_url):
    details = {
        "password_field": 0,
        "external_favicon": 0,
        "obfuscated_js": 0,
        "logo_impersonation": 0
    }
    try:
        # Password field
        if soup.find('input', {'type': 'password'}): details["password_field"] = 1
        
        # External favicon
        icon_link = soup.find("link", rel=re.compile("icon", re.I))
        if icon_link and icon_link.has_attr('href'):
            favicon_url = urljoin(base_url, icon_link['href'])
            if tldextract.extract(favicon_url).registered_domain != tldextract.extract(base_url).registered_domain:
                details["external_favicon"] = 1
        
        # Obfuscated JS
        for script in soup.find_all("script", src=True):
            try:
                script_url = urljoin(base_url, script['src'])
                js_code = requests.get(script_url, timeout=3).text
                beautified_code = jsbeautifier.beautify(js_code)
                if len(js_code) > 1000 and len(beautified_code) < len(js_code) * 0.5:
                    details["obfuscated_js"] += 1
            except Exception: continue

        # Logo Impersonation
        page_domain = tldextract.extract(base_url).domain
        if page_domain not in TRUSTED_BRAND_LOGOS:
            for img in soup.find_all('img', {'src': re.compile(r'logo', re.I)}):
                try:
                    img_url = urljoin(base_url, img['src'])
                    response = requests.get(img_url, stream=True, timeout=3)
                    img_hash = imagehash.average_hash(Image.open(response.raw))
                    for brand_hash in TRUSTED_BRAND_LOGOS.values():
                        if img_hash - brand_hash < 5: # Similarity threshold
                            details["logo_impersonation"] = 1
                            break
                except Exception: continue
    except Exception: pass
    return details

# --- ML Model Training ---
print("Training model...")
df = pd.read_csv('dataset.csv')
X = [extract_features_for_training(url) for url in df['url']]
y = [1 if str(label).strip().lower() == 'phishing' else 0 for label in df['type']]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
print(f"Model Accuracy: {accuracy_score(y_test, model.predict(X_test)):.2f}")
print("Model training complete.")

# --- Configure Gemini API ---
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    llm = genai.GenerativeModel('gemini-1.5-flash-latest')
    print("Gemini API configured successfully.")
except Exception:
    llm = None
    print("WARNING: Could not configure Gemini API. Text analysis will not work.")

# --- Flask API Server ---
app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze_url():
    data = request.get_json()
    url_to_check = data.get('url')
    if not url_to_check: return jsonify({'error': 'URL not provided'}), 400

    score_breakdown = {}
    reasons = []

    # Layer 1: AI Model Prediction
    url_features = extract_features_for_training(url_to_check)
    ai_confidence = model.predict_proba([url_features])[0][1]
    score_breakdown['AI Model Confidence'] = int(ai_confidence * 50)
    if ai_confidence > 0.7:
        reasons.append("AI model detected suspicious URL patterns")

    # Layer 2: Live Detective Checks
    try:
        hostname = urlparse(url_to_check).netloc
        response = requests.get(url_to_check, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        
        domain_age = get_domain_age(hostname)
        if 0 <= domain_age < 90:
            score_breakdown[f'Domain Age ({domain_age} days)'] = 25
            reasons.append(f"Site is very new ({domain_age} days old)")
        
        if check_ssl_certificate(hostname) == 1:
            score_breakdown['Basic/Invalid SSL'] = 15
            reasons.append("Uses a basic or invalid SSL certificate")
        
        page_details = analyze_page_details(soup, url_to_check)
        if page_details["password_field"] == 1: reasons.append("Page contains a password field")
        if page_details["external_favicon"] == 1:
            score_breakdown['External Favicon'] = 10
            reasons.append("Favicon is hosted on a different domain")
        if page_details["obfuscated_js"] > 0:
            score_breakdown['Obfuscated JavaScript'] = 20
            reasons.append("Detected potentially obfuscated JavaScript")
        if page_details["logo_impersonation"] == 1:
            score_breakdown["Logo Impersonation"] = 30
            reasons.append("Impersonating a trusted brand's logo")
            
    except Exception as e:
        reasons.append(f"Could not perform live analysis: {e}")

    phishing_score = sum(score_breakdown.values())
    phishing_score = min(phishing_score, 100)
    is_phishing = phishing_score > 60

    if is_phishing:
        final_status = "Phishing"
        message = ". ".join(reasons) if reasons else "AI model flagged this site."
    else:
        final_status = "Legitimate"
        message = "This site appears to be safe."

    result = {
        "status": final_status,
        "phishing_score": f"{phishing_score:.0f}",
        "message": message,
        "reasons": reasons
    }
    return jsonify(result)

@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    if not llm:
        return jsonify({"error": "Gemini API not configured on the server."}), 500
        
    data = request.get_json()
    text_to_check = data.get('text')
    if not text_to_check:
        return jsonify({'error': 'No text provided'}), 400

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
        print(f"Error calling Gemini API: {e}")
        return jsonify({"error": "Failed to analyze text with AI."}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)