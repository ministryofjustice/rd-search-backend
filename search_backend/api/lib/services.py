from pathlib import Path
from urllib.parse import urlparse

from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore
from opensearchpy import OpenSearch, Urllib3HttpConnection, Urllib3AWSV4SignerAuth

from search_backend.api.lib.config import get_config
from search_backend.api.lib.aws import get_aws_session
from search_backend.api.lib.dummyqueryservice import DummyQueryService
from search_backend.api.lib.hybridqueryservice import HybridQueryService
from search_backend.api.lib.retrieval_pipeline import RetrievalPipeline
from search_backend.api.lib.s3client import S3Client


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
    embedding_dim = cfg["embedding_dim"],

    # OpenSearch document store
    opensearch_docstore_options = {
        "hosts": [url],
        "http_auth": auth,
        "use_ssl": use_ssl,
        "verify_certs": False,
        "connection_class": Urllib3HttpConnection,
        "index": "document",
        "embedding_dim": embedding_dim,
    }

    return OpenSearchDocumentStore(create_index=create_index, **opensearch_docstore_options)


# set up the hybrid pipeline with the read-only opensearch document store
def query_service_factory():
    cfg = get_config()
    document_store = document_store_factory(cfg, create_index=False)

    if cfg["QUERY_SERVICE"] == "hybrid":
        pipeline = RetrievalPipeline(document_store, cfg["dense_embedding_model"], cfg["rerank_model"])
        return HybridQueryService(pipeline.setup_hybrid_pipeline())
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
