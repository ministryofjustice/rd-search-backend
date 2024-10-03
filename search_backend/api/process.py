"""
Example entry point for the data processing
"""

from search_backend.api.lib import get_config
from search_backend.api.lib.services import SERVICES
from search_backend.api.lib.read_data_functions import read_docs
from search_backend.api.lib.opensearchpipeline import run_indexing_pipeline

cfg = get_config()

s3client = SERVICES["s3clientfactory"]()
document_store = SERVICES["documentstorefactory"](cfg, create_index=True)

# Get a list of documents to be read in
objs, _ = s3client.list()
file_list = [obj["Key"] for obj in objs]

# Parse the data
dataset = read_docs(s3client, file_list)

# Create the document store containing the embeddings
run_indexing_pipeline(dataset, document_store, cfg, semantic=True)
