"""
Haystack pipeline functions for indexing and retrieval, using Opensearch as the document store.
"""

import os

from haystack.utils import Secret
from haystack import Document
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from haystack.components.preprocessors.document_splitter import DocumentSplitter
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.joiners import DocumentJoiner
from haystack.components.rankers import TransformersSimilarityRanker
from haystack_integrations.components.embedders.fastembed import (
    FastembedDocumentEmbedder,
    FastembedTextEmbedder,
)
from haystack_integrations.components.generators.amazon_bedrock import AmazonBedrockGenerator
from haystack_integrations.components.retrievers.opensearch import OpenSearchBM25Retriever, OpenSearchEmbeddingRetriever
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore


def run_semantic_indexing_pipeline(dataset, document_store: OpenSearchDocumentStore, cfg):
    """
    This function embeds the data according to the chosen model, and writes to a document store.

    :param dataset - this is list of dictionaries containing the parsed data.
    :param cfg - the configuration of the pipeline, as per get_config()

    Other inputs, such as models to be used come from the config file.
    """

    print("Initialising dense embedding pipeline...")

    # Convert the list of dictionaries into a list of Haystack Document objects
    docs = [
        Document(**content, id_hash_keys=["content", "meta"]) for content in dataset
    ]

    document_splitter = DocumentSplitter(
        split_by="word", split_length=128, split_overlap=32
    )

    indexing = Pipeline()
    indexing.add_component("document_splitter", document_splitter)
    indexing.add_component(
        "dense_doc_embedder",
        FastembedDocumentEmbedder(model=cfg["dense_embedding_model"]),
    )
    indexing.add_component(
        "document_writer",
        DocumentWriter(document_store=document_store, policy=DuplicatePolicy.OVERWRITE),
    )
    indexing.connect("document_splitter", "dense_doc_embedder")
    indexing.connect("dense_doc_embedder", "document_writer")

    # Create the document store
    print("Running embedding pipeline...")
    indexing.run({"document_splitter": {"documents": docs}})


def run_bm25_indexing_pipeline(dataset, document_store: OpenSearchDocumentStore, cfg):
    """
    This function embeds the data according to the chosen model, and writes to a document store.

    :param dataset - this is list of dictionaries containing the parsed data.
    :param cfg - the configuration of the pipeline, as per get_config()

    Other inputs, such as models to be used come from the config file.
    """

    print("Initialising document store")

    # Convert the list of dictionaries into a list of Haystack Document objects
    docs = [
        Document(**content, id_hash_keys=["content", "meta"]) for content in dataset
    ]

    document_splitter = DocumentSplitter(
        split_by="word", split_length=128, split_overlap=32
    )

    indexing = Pipeline()
    indexing.add_component("document_splitter", document_splitter)
    indexing.add_component(
        "document_writer",
        DocumentWriter(document_store=document_store, policy=DuplicatePolicy.OVERWRITE),
    )
    indexing.connect("document_splitter", "document_writer")

    # Create the document store
    print("Running indexing pipeline...")
    indexing.run({"document_splitter": {"documents": docs}})


def setup_hybrid_pipeline(document_store: OpenSearchDocumentStore, dense_embedding_model: str, rerank_model: str) -> Pipeline:
    """
    This function sets up the hybrid retrieval pipeline based on an existing document store.

    :return: Returns the pipeline object which can then be used to search the data for matches to a particular query.
    """
    # Embed the search query
    dense_text_embedder = FastembedTextEmbedder(
        model=dense_embedding_model,
        cache_dir=os.getcwd() + "/embedding_cache",
    )

    hybrid_retrieval = Pipeline()

    hybrid_retrieval.add_component("dense_text_embedder", dense_text_embedder)

    bm25_retriever = OpenSearchBM25Retriever(document_store=document_store, scale_score=True)
    embedding_retriever = OpenSearchEmbeddingRetriever(document_store=document_store)

    hybrid_retrieval.add_component("bm25_retriever", bm25_retriever)
    hybrid_retrieval.add_component("embedding_retriever", embedding_retriever)
    hybrid_retrieval.add_component("document_joiner", DocumentJoiner(join_mode="concatenate"))
    hybrid_retrieval.add_component("ranker", TransformersSimilarityRanker(model=rerank_model))

    hybrid_retrieval.connect(
        "dense_text_embedder.embedding", "embedding_retriever.query_embedding"
    )
    hybrid_retrieval.connect("bm25_retriever", "document_joiner")
    hybrid_retrieval.connect("embedding_retriever", "document_joiner")
    hybrid_retrieval.connect("document_joiner", "ranker")

    return hybrid_retrieval


def setup_semantic_pipeline(document_store: OpenSearchDocumentStore, dense_embedding_model: str, rerank_model: str) -> Pipeline:
    """
    This function sets up a dense embedding retrieval pipeline based on an existing document store.

    :return: Returns the pipeline object which can then be used to search the data for matches to a particular query.
    """
    # Embed the search query
    dense_text_embedder = FastembedTextEmbedder(
        model=dense_embedding_model,
        cache_dir=os.getcwd() + "/embedding_cache",
    )

    retrieval = Pipeline()

    retrieval.add_component("dense_text_embedder", dense_text_embedder)

    embedding_retriever = OpenSearchEmbeddingRetriever(document_store=document_store)

    retrieval.add_component("embedding_retriever", embedding_retriever)
    retrieval.add_component("ranker", TransformersSimilarityRanker(model=rerank_model))

    retrieval.connect(
        "dense_text_embedder.embedding", "embedding_retriever.query_embedding"
    )
    retrieval.connect("embedding_retriever", "ranker")

    return retrieval


def setup_bm25_pipeline(document_store: OpenSearchDocumentStore) -> Pipeline:
    """
    This function sets up a BM25 retrieval pipeline based on an existing document store.

    :return: Returns the pipeline object which can then be used to search the data for matches to a particular query.
    """

    bm25_retrieval = Pipeline()
    bm25_retriever = OpenSearchBM25Retriever(document_store=document_store, scale_score=True)
    bm25_retrieval.add_component("bm25_retriever", bm25_retriever)

    return bm25_retrieval


def setup_rag_pipeline(base_pipeline: Pipeline, llm: str, region: str, credentials) -> Pipeline:
    """
    This function sets up the RAG pipeline by providing a prompt to a genAI model, and calling the function
    setup the hybrid retrieval pipeline.

    :return: Returns the pipeline object to be used for a Question-Answer system.
    """

    template = """
    You are a helpful assistant tasked with answering HR policy queries.

    Here is information to use to answer a question:
    {% for document in documents %}
        {{ document.content }}
    {% endfor %}

    Answer the following question using the information above.
    Your answer must be in British English and use language that is clear and concise.
    Answer the question directly. DO NOT begin your answer with 'According to the information provided'.

    If the information does not provide the answer to the question, reply with: 'Apologies, that query cannot be answered using the supplied documents.'

    Question: {{question}}
    Answer:
    """

    generator = AmazonBedrockGenerator(
        # model="anthropic.claude-3-haiku-20240307-v1:0",
        model=llm,
        aws_access_key_id=Secret.from_token(credentials.access_key),
        aws_secret_access_key=Secret.from_token(credentials.secret_key),
        aws_session_token=Secret.from_token(credentials.token),
        aws_region_name=Secret.from_token(region),
        max_length=1000,
        temperature=0
    )

    base_pipeline.add_component("prompt_builder", PromptBuilder(template=template))
    base_pipeline.add_component("generator", generator)
    base_pipeline.add_component("answer_builder", AnswerBuilder())

    base_pipeline.connect("ranker", "prompt_builder.documents")

    base_pipeline.connect("prompt_builder", "generator")
    base_pipeline.connect("generator.replies", "answer_builder.replies")
    base_pipeline.connect("ranker", "answer_builder.documents")

    return base_pipeline
