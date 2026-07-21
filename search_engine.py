"""
search_engine.py

does the actual searching. turns each product's text into a TF-IDF
vector and compares it to the query using cosine similarity - basically
it just checks which words show up in both and scores products higher
the more (weighted) words they share with the query.

there's also an "embeddings" option that uses sentence-transformers
instead, which is supposed to be better at catching things like "warm
coat" matching "insulated jacket" even with no shared words.
"""

import re

import pandas as pd
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# made this once here instead of inside the function so we're not
# creating a new PorterStemmer every single time a word gets stemmed
stemmer = PorterStemmer()
word_pattern = re.compile(r"[a-zA-Z]{2,}")


def stem_tokenize(text):
    # spent a while confused why searching "shirt" wasn't finding any of
    # the "mens-shirts" products. turns out TfidfVectorizer just treats
    # "shirt" and "shirts" as two totally different words. stemming
    # chops words down to a root form (shirts -> shirt, running -> run)
    # so they end up counting as the same word
    words = word_pattern.findall(text.lower())
    return [stemmer.stem(w) for w in words if w not in ENGLISH_STOP_WORDS]


class ProductSearchEngine:
    def __init__(self, catalog, backend="tfidf"):
        self.catalog = catalog.reset_index(drop=True)
        self.backend = backend

        if backend == "tfidf":
            # passing our own analyzer means TfidfVectorizer's built in
            # stop_words/lowercase settings don't do anything anymore -
            # stem_tokenize has to take care of all of that itself
            self.vectorizer = TfidfVectorizer(analyzer=stem_tokenize, max_features=5000)
            self.matrix = self.vectorizer.fit_transform(self.catalog["search_text"])
        elif backend == "embeddings":
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            self.matrix = self.model.encode(self.catalog["search_text"].tolist())
        else:
            raise ValueError(f"unknown backend: {backend}")

    def embed_query(self, query):
        if self.backend == "tfidf":
            return self.vectorizer.transform([query.lower()])
        return self.model.encode([query.lower()])

    def search(self, query, top_k=5, min_score=0.1):
        # if we don't filter out low scores, a query that shares zero
        # words with anything in the catalog still returns 5 "results"
        # since everything ties at a score of 0 and head() just grabs
        # whatever rows happen to come first. dropping anything under
        # min_score fixes that
        query_vec = self.embed_query(query)
        scores = cosine_similarity(query_vec, self.matrix).flatten()

        results = self.catalog.copy()
        results["score"] = scores
        results = results[results["score"] >= min_score]
        results = results.sort_values("score", ascending=False).head(top_k)
        return results[["title", "brand", "category", "price", "score"]].reset_index(drop=True)
