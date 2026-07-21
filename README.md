# product-rag-assistant

Small project I made to practice working with a real API and basic NLP
search. (No LLM calls here, just TF-IDF/embeddings + cosine similarity,
figured "RAG" was close enough since it's retrieval over a catalog for
search type queries.)

## What it does

Pulls a product catalog from an API, cleans it up into a dataframe, builds
a search index over it, and lets you type stuff in plain English instead
of exact keywords.

```
> a lightweight jacket for hiking in the rain
  [0.47] Waterproof Trail Jacket  ($79.99, outerwear, TrailPeak)
  [0.00] Insulated Winter Parka   ($149.99, outerwear, NorthGear)
```

## Files

- `api_client.py`: calls the API (DummyJSON by default), retries a bit if
  it fails, raises an error if the response looks broken.
- `data_pipeline.py`: cleans the raw JSON into a pandas DataFrame, fills
  in missing fields instead of just dropping rows, saves to
  `data/products.csv` so it doesn't have to hit the API every run.
- `search_engine.py`: TF-IDF + cosine similarity search over the catalog.
  Also has an embeddings backend if you `pip install sentence-transformers`.
- `main.py`: the actual CLI, ties everything together.

## Running it

```bash
pip install -r requirements.txt
python main.py
```

Then type stuff at the prompt, `quit` to leave:

```bash
python main.py --use-cache                # skip the API call, use the saved csv
python main.py --query "red lipstick"      # one query and exit
python main.py --backend embeddings        # needs pip install sentence-transformers
```

## Testing offline

My wifi kept dropping while I was building this so I wrote
`dev/mock_server.py`, a tiny Flask app that returns fake products in the
same shape as the real API:

```bash
pip install flask
python dev/mock_server.py &
python main.py --base-url http://localhost:5000/products
```

## Known limitations

- No price filtering. "under $20" just gets matched as text, not parsed
  as an actual number, so it doesn't really work as a filter.
- Default backend (`tfidf`) only matches shared words, no real synonyms
  ("phone" won't match "smartphone"). It does stem words now (nltk's
  PorterStemmer), so at least singular/plural stuff matches. Like "shirt"
  finds products in the "mens-shirts" category, which it didn't before.
  Ran into the no-match case early on too: a query with 0 overlapping
  words with any product still returned 5 results because ties all
  scored 0.0 and top-k just grabbed whatever came first. Fixed that by
  dropping anything under a `min_score` threshold in `search_engine.py`
  instead of always returning something.
- `--backend embeddings` handles actual synonyms better ("warm coat" ~
  "insulated jacket") but is slower and needs the extra dependency.
