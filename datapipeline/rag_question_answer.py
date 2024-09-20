"""
Example entry point for the RAG question-answer pipeline.

This assumes that a document store has already been set up - see process.py
"""

import sys
sys.path.append("..")

from datapipeline.utils.opensearch_pipeline_functions import setup_rag_pipeline
from datapipeline.utils.search_functions import query_answer
from datapipeline.opensearch_config import opensearch_config


# Setup the RAG pipeline - this can be done on app startup
pipe = setup_rag_pipeline(opensearch_config)

# Test query
search_query = "When will my GDD allowance expire?"

# Get the response
answer = query_answer(search_query, pipe)

print(answer['answer'])
print("\nSources:\n")
for source in answer['sources']:
    print(f"Document title: {source['title']}")
    print(f"Text excerpt: {source['text_excerpt']}")
    print("-----\n")

