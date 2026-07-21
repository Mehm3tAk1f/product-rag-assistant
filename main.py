"""
main.py

this is the actual program you run. it grabs the product list, cleans
it up, and then you can type questions and it tries to find matching
products.

usage:
    python main.py
    python main.py --use-cache
    python main.py --base-url http://localhost:5000/products
    python main.py --backend embeddings
"""

import argparse
import sys

from api_client import ApiError, DEFAULT_BASE_URL, fetch_products
from data_pipeline import clean_products, load_cache, save_cache
from search_engine import ProductSearchEngine


def build_catalog(base_url, use_cache):
    if use_cache:
        cached = load_cache()
        if cached is not None:
            print(f"loaded {len(cached)} products from cache")
            return cached
        print("no cache found, fetching instead")

    print(f"fetching products from {base_url} ...")
    try:
        raw = fetch_products(base_url, limit=100)
    except ApiError as e:
        print(f"could not fetch products: {e}", file=sys.stderr)
        sys.exit(1)

    df = clean_products(raw)
    save_cache(df)
    print(f"got {len(df)} products, cached to data/products.csv")
    return df


def format_results(results):
    if results.empty:
        return "No matching products found. Try different words, or use --backend embeddings."

    output = ""
    for _, row in results.iterrows():
        output += f"  [{row['score']:.2f}] {row['title']}  (${row['price']:.2f}, {row['category']}, {row['brand']})\n"
    return output.rstrip("\n")


def main():
    parser = argparse.ArgumentParser(description="Product search assistant")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--use-cache", action="store_true")
    parser.add_argument("--backend", default="tfidf", choices=["tfidf", "embeddings"])
    parser.add_argument("--query", default=None)
    args = parser.parse_args()

    catalog = build_catalog(args.base_url, args.use_cache)
    engine = ProductSearchEngine(catalog, backend=args.backend)

    if args.query:
        print(format_results(engine.search(args.query)))
        return

    print("\nType a question, or 'quit' to exit.\n")
    while True:
        try:
            query = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not query or query.lower() in {"quit", "exit"}:
            break
        results = engine.search(query, top_k=5)
        print(format_results(results))
        print()


if __name__ == "__main__":
    main()
