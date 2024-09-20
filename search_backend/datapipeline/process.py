"""
Example entry point for the data processing
"""

import sys
sys.path.append("..")

from search_backend.api.src.lib import get_config
from search_backend.api.src.lib.services import SERVICES
from search_backend.datapipeline.utils.read_data_functions import read_docs
from search_backend.datapipeline.utils.pipeline_functions import run_semantic_indexing_pipeline

s3client = SERVICES["s3client"]

# Get a list of documents to be read in
objs, _ = s3client.list()
file_list = [obj["Key"] for obj in objs]

# Parse the data
dataset = read_docs(s3client, file_list)

# Create the document store containing the embeddings
run_semantic_indexing_pipeline(dataset, get_config())
