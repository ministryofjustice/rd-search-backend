"""
Example entry point for the hybrid retrieval pipeline (without the generative AI layer).

This assumes that a document store has already been set up - see process.py
"""
from api.src.lib import get_config
from api.src.lib.services import SERVICES
from utils.opensearch_pipeline_functions import setup_hybrid_pipeline
from utils.search_functions import formatted_search_results


# Setup the hybrid search pipeline - this can be done on app startup
hybrid_pipeline = setup_hybrid_pipeline(SERVICES["querydocumentstore"], get_config())

# Test query
search_query = "When will my GDD allowance expire?"

# Retrieve matching document sections - this part needs to be run when a user enters a query
# results = hybrid_search(search_query, hybrid_pipeline, filters=None, top_k=5)
results = formatted_search_results(search_query, hybrid_pipeline, top_k=5)

print(results['answer'])
for doc in results['sources']:
    print(f"Document title: {doc['title']}")
    print(f"Text excerpt: {doc['text_excerpt']}")
    print("-----\n")
