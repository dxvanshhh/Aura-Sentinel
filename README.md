README.md🛡️ 
AuraSentinel: The Proactive Phishing Detection Engine
AuraSentinel is a next-generation security platform that uses a multi-layered AI and live analysis engine to proactively detect and neutralize phishing threats in real-time.

This project was developed for the final round of our hackathon, focusing on creating a robust, polished, and innovative solution to the growing problem of sophisticated phishing attacks.

💡 The Problem: Why Existing Tools Fail
Traditional browser security relies on blacklists, which are slow to update. By the time a malicious site is blacklisted, it has often already claimed numerous victims. Modern phishing attacks, like the sophisticated Haldiram franchisee scam, use aged domains and clean-looking URLs to evade these simple checks, creating a significant security gap for everyday users.

Impact: Phishing is the #1 cause of data breaches, leading to billions of dollars in financial loss and the compromise of sensitive personal information globally.

✨ The Solution: A Proactive, Multi-Layered Defense
AuraSentinel provides a proactive defense by analyzing a website's reputation, content, and intent, not just its URL. Our solution is a Chrome extension powered by an intelligent Python backend that performs a deep, real-time analysis on every site you visit.

(Action Item: Record a short screen video of your extension working, convert it to a GIF using a site like ezgif.com, and replace the link above. This is crucial for the "Demo Effectiveness" score.)

🚀 Key Features & Technical Innovation
Our project scores high on Technical Innovation & Quality by using a hybrid analysis engine that combines multiple cutting-edge technologies.

Dynamic Brand Impersonation Detection: Instead of a limited list, our engine dynamically fetches a comprehensive database of global brands to detect impersonation with high accuracy. This is our main solution for catching sophisticated fakes.

Global Threat Intelligence Integration: It leverages the VirusTotal API to check URLs against a database of over 70 top security vendors, providing an instant layer of community-vetted protection.

Contextual AI Analysis: It uses Google's Gemini AI to scrape and analyze a webpage's text for signs of social engineering or scam language, understanding a site's intent.

Real-time Heuristic Engine: Performs live checks for domain age (whois), SSL certificate reputation (PyOpenSSL), and suspicious code (BeautifulSoup, jsbeautifier).

Seamless User Experience: The extension provides automatic, background protection with a dynamic icon that changes color based on the site's real-time safety level.

🛠️ Technical Architecture & Tech Stack
Our architecture is designed for performance and scalability, separating the lightweight frontend from the powerful backend analysis engine.

Backend: Python, Flask, Scikit-learn, Pandas, VirusTotal API, Google Gemini AI, Requests, BeautifulSoup, Whois, PyOpenSSL

Frontend: JavaScript, HTML, CSS (as a Chrome Extension)

Version Control: Git & GitHub

🏃 How to Run the Prototype
This project has been designed for a seamless setup.

1. Backend Setup
Navigate to the AuraSentinel-Backend folder.

Install all dependencies: pip install -r requirements.txt

Set the required API keys in your terminal. This is a crucial step.

On Windows (PowerShell):

$env:VT_API_KEY = 'YOUR_VIRUSTOTAL_KEY'
$env:GOOGLE_API_KEY = 'YOUR_GEMINI_KEY'

Run the server: python app.py

2. Frontend Setup
Open Google Chrome and navigate to chrome://extensions.

Enable "Developer mode" in the top-right corner.

Click "Load unpacked" and select the AuraSentinel-Extension folder.

The AuraSentinel icon will appear in your toolbar.

📈 Market Viability & Future Roadmap
AuraSentinel has a clear path to becoming a viable product.

Phase 1 (Current): A powerful free extension for individual users to build a user base and gather threat intelligence.

Phase 2 (B2C): Launch AuraSentinel Pro, a premium subscription with family plans and multi-device protection (mobile and desktop).

Phase 3 (B2B): Launch AuraSentinel for Business, an enterprise-grade solution that integrates directly with corporate email (Microsoft 365, Google Workspace) and communication tools (Slack, Teams) to block threats before an employee can click. This represents the primary revenue stream.

👥 The Team
Devansh Raizada

Lakshya Goyal

Niyati Saxena

Aabir Das