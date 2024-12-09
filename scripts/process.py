"""
Example entry point for the data processing and setting up a Document Store for the search
"""

from haystack import Document

from scripts.config import get_config
from search_backend.indexing_pipeline import IndexingPipeline
from scripts.read_data_functions import read_docs
from scripts.services import SERVICES

cfg = get_config()

s3client = SERVICES["s3clientfactory"]()
document_store = SERVICES["documentstorefactory"](cfg, create_index=True)

# Get a list of documents to be read in
objs, _ = s3client.list()
file_list = [obj["Key"] for obj in objs]

# Parse the data
dataset = read_docs(s3client, file_list)

# Create the document store containing the embeddings
indexer = IndexingPipeline(
    document_store, cfg["dense_embedding_model"], semantic=True
)
docs = [Document(**content) for content in dataset]
indexer.index_docs(docs)
