import csv
import random
from flask import Flask, request, render_template

app = Flask(__name__)

# Secret Key
app.secret_key = "secure_key"

# Load CSV Files
def load_csv(file_path):
    data = []
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

trending_products = load_csv("models/trending_products.csv")
train_data = load_csv("models/clean_data.csv")


# Truncate title text
def truncate(text, length):
    return text[:length] + "..." if len(text) > length else text


# Simple content-based recommendation using word match count
def content_based_recommendations(train_data, item_name, top_n=10):
    item_name = item_name.lower()

    # Find selected product
    product = None
    for p in train_data:
        if p.get("Name", "").lower() == item_name:
            product = p
            break

    if not product:
        return []

    product_keywords = product.get("Tags", "").lower().split()

    # Compare with other products
    scores = []
    for idx, item in enumerate(train_data):
        tags = item.get("Tags", "").lower().split()
        score = len(set(tags) & set(product_keywords))  # word overlap
        if score > 0 and item != product:
            scores.append((idx, score))

    # Sort by relevance score
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    recommended_items = []
    for idx, _ in scores[:top_n]:
        recommended_items.append(train_data[idx])

    return recommended_items


# Serve Homepage
@app.route("/")
@app.route("/index")
def index():
    random_imgs = [f"static/img/img_{i}.png" for i in range(1, 9)]
    for item in trending_products:
        item["img"] = random.choice(random_imgs)
        item["price"] = random.randint(40, 150)

    return render_template("index.html", trending_products=trending_products[:8], truncate=truncate)


@app.route("/main")
def main():
    return render_template("main.html")


@app.route('/recommendations', methods=['POST'])
def recommendations():
    prod = request.form.get('prod', '').strip().lower()
    nbr = int(request.form.get('nbr', 10))

    if not prod:
        return render_template('main.html', message="Please enter a valid product name.")

    recommended = content_based_recommendations(train_data, prod, nbr)

    if not recommended:
        return render_template('main.html', message="No recommendations available for this product.")

    random_imgs = [f"static/img/img_{i}.png" for i in range(1, 9)]
    for item in recommended:
        item["img"] = random.choice(random_imgs)
        item["price"] = random.randint(40, 150)

    return render_template("recommendation.html", recommended_products=recommended, truncate=truncate)


if __name__ == "__main__":
    app.run()
