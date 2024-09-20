"""
Run test retrievals using BM25 and semantic search separately, to make sure both
retrievers are actually returning results.

Example of usage:
> python test_search_components.py "When will my GDD allowance expire?"
"""

import argparse

from search_backend.api.src.lib import get_config
from search_backend.api.src.lib.services import SERVICES
from search_backend.api.src.lib.opensearchpipeline import setup_semantic_pipeline, setup_bm25_pipeline, setup_hybrid_pipeline
from search_backend.api.src.lib.searchfunctions import bm25_search, semantic_search, hybrid_search, pretty_print_results

cfg = get_config()

# test_query = "When will my GDD allowance expire?"

parser = argparse.ArgumentParser(prog="Test search components")
parser.add_argument("query", help="Enter search query to try")
args = parser.parse_args()

test_query = args.query
print(test_query)

# Connect to an existing Opensearch document store
query_document_store = SERVICES["querydocumentstore"]

# Check BM25 pipeline
print("**************************")
print("BM25 search results")
print("**************************")
bm25_pipeline = setup_bm25_pipeline(query_document_store)
results = bm25_search(test_query, bm25_pipeline, top_k=3)
pretty_print_results(results["bm25_retriever"]['documents'])

print("\n")
print("**************************")
print("Semantic search results")
print("**************************")
semantic_pipeline = setup_semantic_pipeline(query_document_store, cfg["dense_embedding_model"], cfg["rerank_model"])
results = semantic_search(test_query, semantic_pipeline, top_k=3)
pretty_print_results(results["ranker"]['documents'])
print("\n")

print("\n")
print("**************************")
print("Hybrid search results")
print("**************************")
hybrid_pipeline = setup_hybrid_pipeline(query_document_store, cfg["dense_embedding_model"], cfg["rerank_model"])
results = hybrid_search(test_query, hybrid_pipeline, top_k=3)
pretty_print_results(results["ranker"]['documents'])
print("\n")