import os

from search_backend.api.lib.s3client import S3Client

defaults = {
    # either specify AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY,
    # or AWS_WEB_IDENTITY_TOKEN_FILE and AWS_ROLE_ARN
    "AWS_ACCESS_KEY_ID": "localstack",
    "AWS_SECRET_ACCESS_KEY": "localstack",
    # OR
    "AWS_WEB_IDENTITY_TOKEN_FILE": None,
    "AWS_ROLE_ARN": None,

    # this only needs to be set if the S3 bucket we're using is not in eu-west-2 (Cloud Platform);
    # Analytical Platform S3 is in eu-west-1
    "S3_REGION": "eu-west-1",

    "AWS_URL": "http://localstack:4566",
    "AWS_URL_S3": "http://localstack:4566",
    "AWS_REGION": "eu-west-2",
    "S3_BUCKET": "mojap-rd",
    "S3_KEY_PREFIX": "demo_folder",
    "OPENSEARCH_URL": "http://localstack:4566",
    "QUERY_SERVICE": "hybrid",

    # Optional arg for the OpenSearch docstore, to prevent trying to index everything in one go
    "index_batch_size": 10,

    # Select embedding model for the semantic search. This should be a sentence-similarity
    # model available on Huggingface: https://huggingface.co/models?pipeline_tag=sentence-similarity
    "dense_embedding_model": "snowflake/snowflake-arctic-embed-xs",
    # The value of the embedding dimension must match that specified for the model defined above
    "embedding_dim": 384,

    # Language model used to rank search results better than the embedding retrieval can
    "rerank_model": "cross-encoder/ms-marco-MiniLM-L-2-v2",
}


def get_config() -> dict[str, str]:
    env = {}
    for key, default_value in defaults.items():
        env[key] = os.getenv(key, default_value)
    return env
