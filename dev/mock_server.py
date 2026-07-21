"""
dev/mock_server.py

Fake version of the product API for testing offline, since my wifi
kept cutting out while working on this. Serves the same JSON shape as
the real DummyJSON API.

Run with:  python dev/mock_server.py
Then point the client at:  http://localhost:5000/products
"""
from flask import Flask, jsonify

app = Flask(__name__)

FIXTURE_PRODUCTS = [
    {
        "id": 1,
        "title": "Waterproof Trail Jacket",
        "description": "A lightweight, waterproof jacket designed for hiking in wet conditions. Breathable fabric, packable design.",
        "category": "outerwear",
        "price": 79.99,
        "brand": "TrailPeak",
    },
    {
        "id": 2,
        "title": "Insulated Winter Parka",
        "description": "Heavy insulated parka built for sub-zero temperatures, with a fur-lined hood and windproof shell.",
        "category": "outerwear",
        "price": 149.99,
        "brand": "NorthGear",
    },
    {
        "id": 3,
        "title": "Ceramic Coffee Mug Set",
        "description": "Set of four hand-glazed ceramic mugs, microwave and dishwasher safe. A simple gift for any occasion.",
        "category": "home",
        "price": 24.50,
        "brand": "Homely",
    },
    {
        "id": 4,
        "title": "Wireless Noise-Cancelling Headphones",
        "description": "Over-ear headphones with active noise cancellation, 30-hour battery life, and fast charging.",
        "category": "electronics",
        "price": 129.00,
        "brand": "SoundCore",
    },
    {
        "id": 5,
        "title": "Kids Rain Boots",
        "description": "Colorful, easy-to-clean rubber rain boots for children, with reinforced soles for outdoor play.",
        "category": "footwear",
        "price": 18.99,
        "brand": "SplashKids",
    },
    {
        "id": 6,
        "title": "Birthday Gift Card Holder",
        "description": "A decorative box designed to hold a gift card and a short handwritten note, under $20.",
        "category": "gifts",
        "price": 9.99,
        "brand": "PaperCraft",
    },
    {
        "id": 7,
        "title": "Running Shoes - Trail Edition",
        "description": "Grippy outsole running shoes built for muddy and uneven trail terrain, lightweight mesh upper.",
        "category": "footwear",
        "price": 89.99,
        "brand": "TrailPeak",
    },
    {
        "id": 8,
        "title": "Portable Bluetooth Speaker",
        "description": "Compact splash-resistant speaker with 12-hour battery, suitable for outdoor use.",
        "category": "electronics",
        "price": 39.99,
        "brand": "SoundCore",
    },
]


@app.route("/products")
def products():
    return jsonify({"products": FIXTURE_PRODUCTS, "total": len(FIXTURE_PRODUCTS)})


if __name__ == "__main__":
    app.run(port=5000)
