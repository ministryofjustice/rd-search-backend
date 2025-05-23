"""
Run test retrievals using BM25 and semantic search separately, to make sure both
retrievers are actually returning results.

Example of usage:
> python test_search_components.py "When will my GDD allowance expire?"
"""

import argparse

from scripts.config import get_config
from scripts.services import SERVICES
from search_backend.retrieval_pipeline import RetrievalPipeline
from search_backend.search import Search
from scripts.search_formatting_functions import pretty_print_results

cfg = get_config()

# test_query = "When will my GDD allowance expire?"

parser = argparse.ArgumentParser(prog="Test search components")
parser.add_argument("query", help="Enter search query to try")
args = parser.parse_args()

test_query = args.query
print(test_query)

# Connect to an existing Opensearch document store
query_document_store = SERVICES["querydocumentstore"]

pipeline = RetrievalPipeline(
    query_document_store, cfg["dense_embedding_model"], cfg["rerank_model"]
)

# Check BM25 pipeline
print("**************************")
print("BM25 search results")
print("**************************")
bm25_pipeline = pipeline.setup_bm25_pipeline()
bm25_search_init = Search(bm25_pipeline)
results = bm25_search_init.bm25_search(test_query, top_k=3)
pretty_print_results(results["bm25_retriever"]["documents"])

print("\n")
print("**************************")
print("Semantic search results")
print("**************************")
semantic_pipeline = pipeline.setup_semantic_pipeline()
semantic_search_init = Search(semantic_pipeline)
results = semantic_search_init.semantic_search(test_query, top_k=3)
pretty_print_results(results["ranker"]["documents"])
print("\n")

print("\n")
print("**************************")
print("Hybrid search results")
print("**************************")
hybrid_pipeline = pipeline.setup_hybrid_pipeline()
hybrid_search_init = Search(hybrid_pipeline)
results = hybrid_search_init.hybrid_search(test_query, top_k=3)
pretty_print_results(results["ranker"]["documents"])
print("\n")
