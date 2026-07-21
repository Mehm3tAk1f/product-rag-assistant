"""
api_client.py

talks to the products API and grabs the product list.
using the DummyJSON api by default since it's free and doesn't need a key
https://dummyjson.com/docs/products
"""

import sys
import time

import requests

DEFAULT_BASE_URL = "https://dummyjson.com/products"
REQUEST_TIMEOUT_SECONDS = 10
MAX_RETRIES = 3


class ApiError(RuntimeError):
    pass


def fetch_products(base_url=DEFAULT_BASE_URL, limit=100):
    params = {"limit": limit}
    last_error = None

    # just retry a couple times if it fails, sometimes it's just a random timeout
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(base_url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        except requests.exceptions.RequestException as exc:
            last_error = exc
            time.sleep(attempt)
            continue

        if response.status_code == 200:
            try:
                payload = response.json()
            except ValueError as exc:
                raise ApiError(f"got a 200 but the body wasn't valid json: {exc}")

            # normally the api gives back {"products": [...]}, but just in
            # case it's ever a plain list instead, handle that too (ran
            # into this while testing with a different endpoint)
            if isinstance(payload, list):
                products = payload
            else:
                products = payload.get("products")

            if products is None:
                raise ApiError(f"couldn't find a products list in the response: {payload}")

            return products

        if 500 <= response.status_code < 600:
            last_error = ApiError(f"server error {response.status_code}")
            time.sleep(attempt)
            continue

        raise ApiError(f"request failed with status {response.status_code}: {response.text[:200]}")

    raise ApiError(f"gave up after {MAX_RETRIES} tries: {last_error}")


if __name__ == "__main__":
    # quick manual test, run: python api_client.py [base_url]
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE_URL
    items = fetch_products(url, limit=5)
    print(f"got {len(items)} products")
    for item in items[:3]:
        print(" -", item.get("title"))
