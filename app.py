import csv
import random
from flask import Flask, request, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "secure_key"

# Load CSV files
def load_csv(file_path):
    data = []
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

trending_products = load_csv("models/trending_products.csv")
train_data = load_csv("models/clean_data.csv")

# Truncate function
def truncate(text, length):
    return text[:length] + "..." if len(text) > length else text

# Content based recommendation
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


# Home - Trending Page
@app.route("/")
def index():
    for item in trending_products:
        item["price"] = random.randint(100, 999)

    return render_template("index.html",
                           trending_products=trending_products,
                           truncate=truncate,
                           cart_count=len(session.get("cart", [])))


@app.route("/main")
def main():
    return render_template("main.html",
                           cart_count=len(session.get("cart", [])))


@app.route("/recommendations", methods=["POST"])
def recommendations():
    prod = request.form.get("prod", "").strip()
    nbr = int(request.form.get("nbr", 10))

    recommended_products = content_based_recommendations(train_data, prod, nbr)

    if not recommended_products:
        return render_template("main.html",
                               message="No product found ❌",
                               cart_count=len(session.get("cart", [])))

    for item in recommended_products:
        item["price"] = random.randint(100, 999)

    return render_template("recommendation.html",
                           recommended_products=recommended_products,
                           truncate=truncate,
                           cart_count=len(session.get("cart", [])))


# Add to Cart
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    product_name = request.form["product_name"]
    brand = request.form["brand"]
    price = request.form["price"]
    rating = request.form["rating"]
    image = request.form["image"]

    product = {
        "Name": product_name,
        "Brand": brand,
        "price": price,
        "Rating": rating,
        "ImageURL": image
    }

    cart = session.get("cart", [])
    cart.append(product)
    session["cart"] = cart

    return redirect(request.referrer)


# Cart Page View
@app.route("/cart")
def cart():
    cart_items = session.get("cart", [])
    return render_template("cart.html",
                           cart_items=cart_items,
                           cart_count=len(cart_items))


# Clear Cart
@app.route("/clear_cart")
def clear_cart():
    session["cart"] = []
    return redirect("/cart")


if __name__ == "__main__":
    app.run(debug=True)
