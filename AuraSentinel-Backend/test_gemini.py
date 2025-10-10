import os
import google.generativeai as genai

print("--- Starting Gemini Connection Test ---")

try:
    # Step 1: Set your API Key in the terminal before running
    # On Windows PowerShell: $env:GOOGLE_API_KEY = 'YOUR_API_KEY'
    api_key = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    print("API Key found and configured.")

    # Step 2: Initialize the model
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    print("Model initialized successfully.")

    # Step 3: Send a simple prompt
    print("Sending prompt to Gemini...")
    response = model.generate_content("Hello, world.")

    # Step 4: Print the response
    print("\n--- SUCCESS! ---")
    print("Gemini responded:")
    print(response.text)

except Exception as e:
    print("\n--- TEST FAILED ---")
    print("An error occurred:")
    print(e)