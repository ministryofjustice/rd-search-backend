from pathlib import Path
from urllib.parse import urlparse

from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore
from opensearchpy import OpenSearch, Urllib3HttpConnection, Urllib3AWSV4SignerAuth

from . import get_config
from .aws import get_aws_session
from .bedrockqueryservice import BedrockQueryService
from .dummyqueryservice import DummyQueryService
from .hybridqueryservice import HybridQueryService
from .opensearchpipeline import setup_hybrid_pipeline, setup_rag_pipeline
from .s3client import S3Client


# S3 needs a specific region if we're using Analytical Platform buckets
def s3client_factory():
    cfg = get_config()
    s3_session = get_aws_session(cfg, cfg["S3_REGION"])
    client = s3_session.client("s3", endpoint_url=cfg["AWS_URL_S3"])
    return S3Client(cfg["S3_BUCKET"], cfg["S3_KEY_PREFIX"], client)


# OpenSearch health check client
def opensearch_client_factory():
    cfg = get_config()

    aws_session = get_aws_session(cfg, cfg["AWS_REGION"])
    credentials = aws_session.get_credentials()
    auth = Urllib3AWSV4SignerAuth(credentials, cfg["AWS_REGION"], "es")
    url = cfg["OPENSEARCH_URL"]
    use_ssl = urlparse(url).scheme == "https"

    return OpenSearch(
        hosts=[url],
        http_auth=auth,
        use_ssl=use_ssl,
        verify_certs=False,
        connection_class=Urllib3HttpConnection,
    )


def document_store_factory(cfg, create_index=False):
    aws_session = get_aws_session(cfg, cfg["AWS_REGION"])
    credentials = aws_session.get_credentials()
    auth = Urllib3AWSV4SignerAuth(credentials, cfg["AWS_REGION"], "es")
    url = cfg["OPENSEARCH_URL"]
    use_ssl = urlparse(url).scheme == "https"

    # OpenSearch document store
    opensearch_docstore_options = {
        "hosts": [url],
        "http_auth": auth,
        "use_ssl": use_ssl,
        "verify_certs": False,
        "connection_class": Urllib3HttpConnection,
        "index": "document",
        "embedding_dim": 384,
    }

    return OpenSearchDocumentStore(create_index=create_index, **opensearch_docstore_options)


# set up the hybrid pipeline with the read-only opensearch document store
def query_service_factory():
    cfg = get_config()
    document_store = document_store_factory(cfg, create_index=False)

    if cfg["QUERY_SERVICE"] == "hybrid":
        return HybridQueryService(
            setup_hybrid_pipeline(document_store, cfg["dense_embedding_model"], cfg["rerank_model"])
        )
    elif cfg["QUERY_SERVICE"] == "bedrock":
        return BedrockQueryService(
            setup_rag_pipeline(
                setup_hybrid_pipeline(
                    document_store,
                    cfg["dense_embedding_model"],
                    cfg["rerank_model"]
                ),
                cfg["llm"],
                cfg["BEDROCK_REGION"],
                get_aws_session(cfg, cfg["BEDROCK_REGION"]).get_credentials()
            )
        )
    else:
        return DummyQueryService(
            Path(__file__).parent / "../fixtures/dummyanswers.json"
        )


SERVICES = {
    "queryservicefactory": query_service_factory,
    "s3clientfactory": s3client_factory,
    "opensearchclientfactory": opensearch_client_factory,
    "documentstorefactory": document_store_factory,
    "querydocumentstore": document_store_factory(get_config(), create_index=False),
}
