import requests
from flask import Flask, request, render_template
import time
app = Flask(__name__)

# Set your Gemini API key (replace with your actual API key)
GEMINI_API_KEY = "AIzaSyAdHKUV2avBTh061MVD3CS7vVIgnLG2yew"

# Function to call the Gemini API and get generated content
def generate_text_with_gemini(prompt, retries=3, delay=2):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    for attempt in range(retries):
        response = requests.post(url, json=payload, headers=headers, params={"key": GEMINI_API_KEY})
        
        # Print the full response for debugging
        print("API Response: ", response.json())  # This will print the full response
        
        # If request is successful, return the generated text
        if response.status_code == 200:
            try:
                # Updated key paths to match the response structure
                generated_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                return generated_text
            except KeyError as e:
                return f"Error: Missing expected key {str(e)} in response."
        
        # If the model is overloaded, retry with exponential backoff
        elif response.status_code == 429:  # HTTP 429 means "Too Many Requests"
            time.sleep(delay)  # Wait before retrying
            delay *= 2  # Exponential backoff
        else:
            # For other errors, return the error message
            error_message = response.json().get('error', {}).get('message', 'Unknown error')
            return f"Error generating text: {error_message}"

    # If all retries failed, return a message
    return "The model is still overloaded. Please try again later."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_text():
    prompt = request.form["prompt"]
    generated_text = generate_text_with_gemini(prompt)
    return render_template("index.html", prompt=prompt, result=generated_text)

if __name__ == "__main__":
    app.run(debug=True)
