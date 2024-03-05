from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Define your API URL and API key
API_URL = "https://api.sommify.ai/sommelier/v1/url/list"
API_RECIPE = "https://api.sommify.ai/sommelier/v1/recipe/list"
API_KEY = "YOUR_SOMMIFYAI_API_KEY"
EDAMAM_API = "https://api.edamam.com/api/recipes/v2"
EDAMAM_APP_ID = "YOUR_EDAMAM_APP_ID"
EDAMAM_APP_KEY = "YOUR_EDAMAM_APP_KEY"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/recommend", methods=["POST"])
def recommend():
    recipe_url = request.form.get("recipe_url")
    recipe_title = request.form.get("recipe_title_edamam")

    # Get filter parameters from the form
    tags = request.form.getlist("tags")
    streamline = request.form.get("streamline") == "on"
    green = request.form.get("green") == "on"
    limit = int(request.form.get("limit")) if request.form.get("limit") else 3
    min_price = request.form.get("min_price")
    max_price = request.form.get("max_price")
    preferences = request.form.getlist("preferences")
    dislikes = request.form.getlist("dislikes")
    origin_country = request.form.get("origin_country")
    origin_region = request.form.get("origin_region")
    origin_subregion = request.form.get("origin_subregion")
    grapes = request.form.getlist("grapes")
    vintage = [int(year.strip()) for year in request.form.get("vintage").split(",")] if request.form.get(
        "vintage") else None
    min_alcohol_level = int(request.form.get("min_alcohol_level")) if request.form.get("min_alcohol_level") else None
    max_alcohol_level = int(request.form.get("max_alcohol_level")) if request.form.get("max_alcohol_level") else None

    # Construct the filter payload
    filter_payload = {
        "tags": tags,
        "streamline": streamline,
        "green": green,
        "limit": limit,
        "price": {
            "min": min_price,
            "max": max_price,
            "currency": "EUR"
        },
         "preferences": preferences,
         "dislikes": dislikes,
         "origin": [origin_country,origin_region,origin_subregion],
         "grapes": grapes,
         "vintage": vintage,
        "minAlcoholLevel": min_alcohol_level,
        "maxAlcoholLevel": max_alcohol_level
    }

    if recipe_url:
        payload = {
            "url": recipe_url,
            "filter": filter_payload
        }
        response = requests.post(API_URL, headers={"X-Api-Key": API_KEY, "Content-Type": "application/json"},
                                 json=payload)
    elif recipe_title:
        # Call Edamam recipe search API
        edamam_payload = {
            "type": "public",
            "app_id": EDAMAM_APP_ID,
            "app_key": EDAMAM_APP_KEY,
            "q": recipe_title
        }
        edamam_response = requests.get(EDAMAM_API, params=edamam_payload)
        if edamam_response.status_code == 200:
            recipes = edamam_response.json()["hits"]
            if recipes:
                # Use the first recipe found
                recipe_url = recipes[0]["recipe"]["url"]
                payload = {
                    "url": recipe_url,
                    "filter": filter_payload
                }
                response = requests.post(API_URL, headers={"X-Api-Key": API_KEY, "Content-Type": "application/json"},
                                         json=payload)
            else:
                return "No recipes found for the given title."
        else:
            return "Error fetching recipes from Edamam API."
    else:
        recipe_ingredients = [ingredient.strip() for ingredient in request.form.get("recipe_ingredients").split(",")]
        recipe_steps = [step.strip() for step in request.form.get("recipe_steps").split(".")]

        # Include filter payload even when providing recipe details
        payload = {
            "title": recipe_title,
            "ingredients": recipe_ingredients,
            "steps": recipe_steps,
            "filter": filter_payload
        }

        response = requests.post(API_RECIPE, headers={"X-Api-Key": API_KEY, "Content-Type": "application/json"},
                                 json=payload)

    if response.status_code == 200:
        recommendations = response.json()["wines"]
        return render_template("recommendations.html", recommendations=recommendations)
    else:
        error_message = f"Error: {response.status_code} - {response.text}"
        print(error_message)
        return "Error fetching recommendations"


if __name__ == "__main__":
    app.run(debug=True)
