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
    "BEDROCK_REGION": "eu-west-3",

    "AWS_URL": "http://localstack:4566",
    "AWS_URL_S3": "http://localstack:4566",
    "AWS_REGION": "eu-west-2",
    "S3_BUCKET": "mojap-rd",
    "S3_KEY_PREFIX": "gdd_capability/gdd_capability_pay",
    "OPENSEARCH_URL": "http://localstack:4566",
    "QUERY_SERVICE": "hybrid",

    "dense_embedding_model": "snowflake/snowflake-arctic-embed-s",
    "rerank_model": "cross-encoder/ms-marco-MiniLM-L-6-v2",
    "llm": "anthropic.claude-3-sonnet-20240229-v1:0",
}


def get_config() -> dict[str, str]:
    env = {}
    for key, default_value in defaults.items():
        env[key] = os.getenv(key, default_value)
    return env
