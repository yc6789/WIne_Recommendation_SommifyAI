from flask import Flask, jsonify, request, render_template
import requests

app = Flask(__name__)

# API Configuration
API_URL = "https://api.sommify.ai/sommelier/v1/url/list"
API_RECIPE = "https://api.sommify.ai/sommelier/v1/recipe/list"
API_KEY = "YOUR_SOMMIFYAI_API_KEY"
EDAMAM_API = "https://api.edamam.com/api/recipes/v2"
EDAMAM_APP_ID = "YOUR_EDAMAM_APP_ID"
EDAMAM_APP_KEY = "YOUR_EDAMAM_APP_KEY"

# Home endpoint
@app.route("/")
def home():
    return render_template("index.html")

# Fetch recommendations based on URL
@app.route("/recommendations", methods=["POST"])
def create_recommendations():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        data = request.json
    else:
        return "Content-Type not supported!", 415
    
    url = data.get("url")
    title = data.get("title")
    
    if not url and not title:
        return "Missing URL or Title", 400

    filter_payload = data.get("filter", {})

    if url:
        payload = {"url": url, "filter": filter_payload}
        response = requests.post(API_URL, headers={"X-Api-Key": API_KEY, "Content-Type": "application/json"}, json=payload)
    elif title:
        response = handle_edamam_recipe(title, filter_payload)
        if isinstance(response, str):  # Handle error messages directly returned from the helper function
            return response, 400
    else:
        return "Invalid request data", 400

    if response.status_code == 200:
        recommendations = response.json().get("wines", [])
        return jsonify(recommendations)
    else:
        return f"Error fetching recommendations: {response.status_code} - {response.text}", response.status_code

def handle_edamam_recipe(title, filter_payload):
    edamam_payload = {
        "type": "public",
        "app_id": EDAMAM_APP_ID,
        "app_key": EDAMAM_APP_KEY,
        "q": title
    }
    response = requests.get(EDAMAM_API, params=edamam_payload)
    if response.status_code == 200:
        recipes = response.json().get("hits", [])
        if recipes:
            recipe_url = recipes[0]["recipe"]["url"]
            return requests.post(API_URL, headers={"X-Api-Key": API_KEY, "Content-Type": "application/json"},
                                 json={"url": recipe_url, "filter": filter_payload})
        else:
            return "No recipes found for the given title."
    else:
        return f"Error fetching recipes from Edamam: {response.status_code} - {response.text}"

if __name__ == "__main__":
    app.run(debug=True)
