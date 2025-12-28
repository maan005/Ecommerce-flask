import csv
import random
from flask import Flask, request, render_template

app = Flask(__name__)
app.secret_key = "secure_key"

# Load CSV
def load_csv(file_path):
    data = []
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

trending_products = load_csv("models/trending_products.csv")
train_data = load_csv("models/clean_data.csv")

# Truncate function for product names
def truncate(text, length):
    return text[:length] + "..." if len(text) > length else text

# Simple recommendation engine
def content_based_recommendations(train_data, item_name, top_n=10):
    item_name = item_name.lower()
    selected_item = None

    for item in train_data:
        if item.get("Name", "").lower() == item_name:
            selected_item = item
            break

    if not selected_item:
        return []

    keywords = selected_item.get("Tags", "").lower().split()
    scores = []

    for itm in train_data:
        tags = itm.get("Tags", "").lower().split()
        score = len(set(tags) & set(keywords))
        if score > 0 and itm != selected_item:
            scores.append((itm, score))

    scores.sort(key=lambda x: x[1], reverse=True)

    return [itm[0] for itm in scores[:top_n]]


@app.route("/")
@app.route("/index")
def index():
    for item in trending_products[:8]:
        item["price"] = random.randint(100, 999)

    return render_template("index.html",
                           trending_products=trending_products[:8],
                           truncate=truncate)


@app.route("/main")
def main():
    return render_template("main.html")


@app.route("/recommendations", methods=["POST"])
def recommendations():
    prod = request.form.get("prod", "").strip().lower()
    nbr = int(request.form.get("nbr", 10))

    if not prod:
        return render_template("main.html", message="Please enter a product name.")

    recommended_products = content_based_recommendations(train_data, prod, nbr)

    if not recommended_products:
        return render_template("main.html", message="No product found ❌")

    for item in recommended_products:
        item["price"] = random.randint(100, 999)

    return render_template("recommendation.html",
                           recommended_products=recommended_products,
                           truncate=truncate)


if __name__ == "__main__":
    app.run(debug=True)
