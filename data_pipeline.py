"""
data_pipeline.py

takes the raw json from the api and turns it into a pandas dataframe,
then saves it as a csv so I don't have to keep re-fetching every time
I run the script.
"""

import os

import pandas as pd

CACHE_PATH = os.path.join(os.path.dirname(__file__), "data", "products.csv")

COLUMNS = ["id", "title", "description", "category", "price", "brand"]


def clean_products(raw_products):
    rows = []
    for i, item in enumerate(raw_products):
        # some products don't come with an id for some reason. if I just
        # left this as None, every product missing an id would count as
        # a "duplicate" of every other one later and get deleted, so
        # give them a fake placeholder id instead
        item_id = item.get("id")
        if item_id is None:
            item_id = "noid-" + str(i)

        rows.append({
            "id": item_id,
            "title": (item.get("title") or "").strip(),
            "description": (item.get("description") or "").strip(),
            "category": (item.get("category") or "uncategorized").strip().lower(),
            "price": item.get("price", float("nan")),
            "brand": (item.get("brand") or "unknown").strip(),
        })

    df = pd.DataFrame(rows, columns=COLUMNS)
    df = df.dropna(subset=["title"])
    df = df[df["title"] != ""]
    df = df.drop_duplicates(subset=["id"]).reset_index(drop=True)

    # combine title + category + description into one field so the search
    # can match on any of them, not just the title
    df["search_text"] = (df["title"] + ". " + df["category"] + ". " + df["description"]).str.lower()

    return df


def save_cache(df, path=CACHE_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


def load_cache(path=CACHE_PATH):
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)
