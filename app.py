import pymysql
pymysql.install_as_MySQLdb()  # Ensure SQLAlchemy uses PyMySQL for MySQL connections
from flask import Flask, request, render_template
import pandas as pd
import random
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load files
trending_products = pd.read_csv("models/trending_products.csv")
train_data = pd.read_csv("models/clean_data.csv")

# Database configuration
app.secret_key = "alskdjfwoeieiurlskdjfsldkdjf"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/ecom"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Define models for signup and signin
class Signup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)  # Increased column size

class Signin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)


# Recommendations function
def truncate(text, length):
    return text[:length] + "..." if len(text) > length else text


def content_based_recommendations(train_data, item_name, top_n=10):
    print(f"Looking for recommendations for: {item_name}")

    # Check if item exists in the dataset
    if item_name not in train_data['Name'].values:
        print(f"Item '{item_name}' not found in the dataset.")
        return pd.DataFrame()  # Return empty DataFrame if not found

    # Check if the 'Tags' column exists
    if 'Tags' not in train_data.columns:
        print("Error: 'Tags' column is missing in the dataset.")
        return pd.DataFrame()

    # Apply TF-IDF Vectorizer and compute cosine similarities
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix_content = tfidf_vectorizer.fit_transform(train_data['Tags'])
    cosine_similarities_content = cosine_similarity(tfidf_matrix_content, tfidf_matrix_content)

    # Get index of the item
    item_index = train_data[train_data['Name'] == item_name].index[0]
    similar_items = list(enumerate(cosine_similarities_content[item_index]))
    similar_items = sorted(similar_items, key=lambda x: x[1], reverse=True)

    # Get top n similar items
    top_similar_items = similar_items[1:top_n + 1]

    # Get the indices of recommended items
    recommended_item_indices = [x[0] for x in top_similar_items]

    # Check if we have any recommended items
    if not recommended_item_indices:
        print("No recommendations found.")
        return pd.DataFrame()

    recommended_items_details = train_data.iloc[recommended_item_indices][
        ['Name', 'ReviewCount', 'Brand', 'ImageURL', 'Rating']]

    return recommended_items_details


# Helper function to generate random images and prices
def get_random_product_images_and_prices():
    random_image_urls = [
        "static/img/img_1.png",
        "static/img/img_2.png",
        "static/img/img_3.png",
        "static/img/img_4.png",
        "static/img/img_5.png",
        "static/img/img_6.png",
        "static/img/img_7.png",
        "static/img/img_8.png",
    ]
    prices = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
    return [random.choice(random_image_urls) for _ in range(len(trending_products))], random.choice(prices)

def validate_image_urls(df):
    # Ensure all image URLs are strings and not null
    df['ImageURL'] = df['ImageURL'].fillna('').astype(str)
    return df

# Validate image URLs in train_data
train_data = validate_image_urls(train_data)


# Routes
@app.route("/")
def index():
    random_product_image_urls, random_price = get_random_product_images_and_prices()
    return render_template('index.html', trending_products=trending_products.head(8),
                           truncate=truncate, random_product_image_urls=random_product_image_urls,
                           random_price=random_price)


@app.route("/main")
def main():
    return render_template('main.html')


@app.route("/index")
def indexredirect():
    random_product_image_urls, random_price = get_random_product_images_and_prices()
    return render_template('index.html', trending_products=trending_products.head(8),
                           truncate=truncate, random_product_image_urls=random_product_image_urls,
                           random_price=random_price)


@app.route("/signup", methods=['POST', 'GET'])
def signup(random_image_urls=None):
    # Provide a default list of image URLs if random_image_urls is None
    if random_image_urls is None:
        random_image_urls = [
            "static/img/img_1.png",
            "static/img/img_2.png",
            "static/img/img_3.png",
            "static/img/img_4.png",
            "static/img/img_5.png",
            "static/img/img_6.png",
            "static/img/img_7.png",
            "static/img/img_8.png",
        ]

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        new_signup = Signup(username=username, email=email, password=password)
        db.session.add(new_signup)
        db.session.commit()

        random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
        price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
        return render_template('index.html', trending_products=trending_products.head(8), truncate=truncate,
                               random_product_image_urls=random_product_image_urls, random_price=random.choice(price),
                               signup_message='User signed up successfully!'
                               )
@app.route('/signin', methods=['POST', 'GET'])
def signin():
    # Provide a default list of image URLs if random_image_urls is not initialized
    random_image_urls = [
        "static/img/img_1.png",
        "static/img/img_2.png",
        "static/img/img_3.png",
        "static/img/img_4.png",
        "static/img/img_5.png",
        "static/img/img_6.png",
        "static/img/img_7.png",
        "static/img/img_8.png",
    ]

    if request.method == 'POST':
        username = request.form['signinUsername']
        password = request.form['signinPassword']

        # Add user sign-in logic to the database
        new_signin = Signin(username=username, password=password)
        db.session.add(new_signin)
        db.session.commit()

        # Create a list of random image URLs for each product
        random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
        price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
        return render_template('index.html', trending_products=trending_products.head(8), truncate=truncate,
                               random_product_image_urls=random_product_image_urls, random_price=random.choice(price),
                               signup_message='User signed in successfully!'
                               )


@app.route('/recommendations', methods=['POST'])
def recommendations():
    try:
        prod = request.form.get('prod', '').strip().lower()
        nbr = int(request.form.get('nbr', 10))

        if not prod:
            return render_template('main.html', message="Please enter a valid product name.")

        train_data['Name'] = train_data['Name'].str.strip().str.lower()
        content_based_rec = content_based_recommendations(train_data, prod, top_n=nbr)

        if content_based_rec.empty:
            return render_template('main.html', message="No recommendations available for this product.")

        random_product_image_urls, random_prices = get_random_product_images_and_prices()
        return render_template(
            'recommendation.html',
            recommended_products=content_based_rec,
            truncate=truncate,
            random_product_image_urls=random_product_image_urls,
            random_prices=random_prices
        )
    except Exception as e:
        print(f"Error in recommendations route: {e}")
        return render_template('main.html', message="An error occurred while fetching recommendations.")

if __name__ == '__main__':
    app.run(debug=True)