import csv
import random
from flask import Flask, request, render_template

app = Flask(__name__)
app.secret_key = "secure_key"

def load_csv(path):
    data = []
    with open(path, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

trending_products = load_csv("models/trending_products.csv")
train_data = load_csv("models/clean_data.csv")

def truncate(text, length):
    return text[:length] + "..." if len(text) > length else text


# Recommendation logic (same as your old)
def content_based_recommendations(train_data, product_name, top_n=10):
    product_name = product_name.lower()

    base_product = None
    for p in train_data:
        if p.get("Name", "").lower() == product_name:
            base_product = p
            break

    if not base_product:
        return []

    keywords = base_product.get("Tags", "").lower().split()
    scores = []

    for i, item in enumerate(train_data):
        tags = item.get("Tags", "").lower().split()
        score = len(set(tags) & set(keywords))
        if score > 0 and item != base_product:
            scores.append((i, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return [train_data[i] for i, _ in scores[:top_n]]


@app.route("/")
@app.route("/index")
def home():
    # Assign random price only (ImageURL already exists!)
    for item in trending_products:
        item["price"] = random.randint(49, 499)

    return render_template("index.html",
                           trending_products=trending_products[:8],
                           truncate=truncate)


@app.route("/main")
def main():
    return render_template("main.html")


@app.route("/recommendations", methods=["POST"])
def recommendations():
    prod = request.form.get("prod", "").strip().lower()
    qty = int(request.form.get("nbr", 10))

    if not prod:
        return render_template("main.html", message="❌ Please enter a product name.")

    recs = content_based_recommendations(train_data, prod, qty)

    if not recs:
        return render_template("main.html", message="⚠ No recommendations found for this product.")

    # Add prices
    for r in recs:
        r["price"] = random.randint(49, 499)

    return render_template("recommendation.html",
                           recommended_products=recs,
                           truncate=truncate)


if __name__ == "__main__":
    app.run()
