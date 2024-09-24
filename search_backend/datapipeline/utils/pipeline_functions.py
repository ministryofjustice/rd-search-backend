"""
Haystack pipeline functions for indexing and retrieval.
"""

import os

from haystack.utils import Secret
from haystack import Document
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.builders.answer_builder import AnswerBuilder
from haystack.components.joiners import DocumentJoiner
from haystack.components.preprocessors.document_splitter import DocumentSplitter
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.writers import DocumentWriter
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.document_stores.types import DuplicatePolicy
from haystack_integrations.components.embedders.fastembed import (
    FastembedDocumentEmbedder,
    FastembedTextEmbedder,
)
from haystack_integrations.components.generators.amazon_bedrock import AmazonBedrockGenerator
from haystack_integrations.components.retrievers.qdrant import (
    QdrantEmbeddingRetriever,
)
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

from search_backend.api.src.lib import get_config

cfg = get_config()


def run_semantic_indexing_pipeline(dataset):
    """
    This function embeds the data according to the chosen model, and writes to a document store.

    :param 1: dataset - this is list of dictionaries containing the parsed data.

    Other inputs, such as models to be used come from the config file.
    """

    # Convert the list of dictionaries into a list of Haystack Document objects
    docs = [
        Document(**content, id_hash_keys=["content", "meta"]) for content in dataset
    ]

    # Initialise DocumentStore
    document_store = QdrantDocumentStore(
        path="DocumentStore",
        index="Document",
        embedding_dim=384,
        recreate_index=True,
        hnsw_config={"m": 16, "ef_construct": 64},  # Optional
        return_embedding=True,
        use_sparse_embeddings=False,
    )

    document_splitter = DocumentSplitter(
        split_by="word", split_length=128, split_overlap=32
    )

    print("Running embedding pipeline...")
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
    indexing.run({"document_splitter": {"documents": docs}})


def setup_hybrid_pipeline(dataset):
    """
    This function sets up the hybrid retrieval pipeline based on an existing document store.

    :param 1: dataset - this is list of dictionaries containing the parsed xlm data. The output of data_loading().

    Other inputs, such as models to be used come from the config file.

    :return: Returns the pipeline object which can then be used to search the data for matches to a particular query.
    """

    # Set up BM25 in-memory index
    print("Indexing docs (BM25)")
    # Convert the list of dictionaries into a list of Haystack Document objects
    docs = [
        Document(**content, id_hash_keys=["content", "meta"]) for content in dataset
    ]
    document_splitter = DocumentSplitter(
        split_by="word", split_length=128, split_overlap=32
    )
    sparse_document_store = InMemoryDocumentStore()

    indexing = Pipeline()
    indexing.add_component("document_splitter", document_splitter)
    indexing.add_component("document_writer", DocumentWriter(sparse_document_store))
    
    indexing.connect("document_splitter", "document_writer")
    indexing.run({"document_splitter": {"documents": docs}})

    # Initialise DocumentStore for semantic search
    document_store = QdrantDocumentStore(
        path="DocumentStore",
        index="Document",
        embedding_dim=384,
        recreate_index=False,
        hnsw_config={"m": 16, "ef_construct": 64},  # Optional
        return_embedding=True,
        use_sparse_embeddings=False,
    )

    # Embed the search query
    dense_text_embedder = FastembedTextEmbedder(
        model=cfg["dense_embedding_model"],
        cache_dir=os.getcwd()+"/embedding_cache",
    )

    print("Creating hybrid search pipeline")
    hybrid_retrieval = Pipeline()

    hybrid_retrieval.add_component("dense_text_embedder", dense_text_embedder)

    hybrid_retrieval.add_component("bm25_retriever", InMemoryBM25Retriever(sparse_document_store))
    hybrid_retrieval.add_component("embedding_retriever", QdrantEmbeddingRetriever(document_store))

    hybrid_retrieval.add_component("document_joiner", DocumentJoiner(join_mode="concatenate"))

    hybrid_retrieval.add_component("ranker", TransformersSimilarityRanker(model=cfg["rerank_model"]))

    hybrid_retrieval.connect(
        "dense_text_embedder.embedding", "embedding_retriever.query_embedding"
    )
    hybrid_retrieval.connect("bm25_retriever", "document_joiner")
    hybrid_retrieval.connect("embedding_retriever", "document_joiner")
    hybrid_retrieval.connect("document_joiner", "ranker")

    return hybrid_retrieval



def setup_semantic_pipeline(dataset):
    """
    This function loads Haystack, preprocesses our text, loads it into the datastore, encodes it according to the models chosen,
    sets up the pipeline and processes the datastore according to the instructions in the pipeline

    :param 1: dataset - this is list of dictionaries containing the parsed data.

    Other inputs, such as models to be used, come from the config file.

    :return: Returns the pipeline object which can then be used to search the data for matches to a particular query.
    """

    # Initialise DocumentStore
    document_store = QdrantDocumentStore(
        path="DocumentStore",
        index="Document",
        embedding_dim=384,
        recreate_index=False,
        hnsw_config={"m": 16, "ef_construct": 64},  # Optional
        return_embedding=True,
        use_sparse_embeddings=False,
    )

    print("Creating embedding retrieval pipeline...")
    
    # Embed the search query
    dense_text_embedder = FastembedTextEmbedder(
        model=cfg["dense_embedding_model"],
        cache_dir=os.getcwd()+"/embedding_cache",
    )

    retrieval = Pipeline()
    retrieval.add_component("dense_text_embedder", dense_text_embedder)
    retrieval.add_component("embedding_retriever", QdrantEmbeddingRetriever(document_store))
    retrieval.add_component("ranker", TransformersSimilarityRanker(model=cfg["rerank_model"]))

    retrieval.connect(
        "dense_text_embedder.embedding", "embedding_retriever.query_embedding"
    )
    retrieval.connect("embedding_retriever", "ranker")

    return retrieval


def setup_bm25_pipeline(dataset):
    """
    This function preprocesses our text, loads it into an in-memory datastore, sets up a BM25 retrieval pipeline.

    :param 1: dataset - This is list of dictionaries containing the parsed data.

    :return: Returns the pipeline object which can then be used to search the data for matches to a particular query.
    """

    sparse_document_store = InMemoryDocumentStore()
    bm25_retriever = InMemoryBM25Retriever(sparse_document_store)

    # Convert the list of dictionaries into a list of Haystack Document objects
    docs = [
        Document(**content, id_hash_keys=["content", "meta"]) for content in dataset
    ]
    
    document_splitter = DocumentSplitter(
        split_by="word", split_length=128, split_overlap=32
    )

    print("Indexing docs")
    indexing = Pipeline()
    indexing.add_component("document_splitter", document_splitter)
    indexing.add_component("document_writer", DocumentWriter(sparse_document_store))
    
    indexing.connect("document_splitter", "document_writer")
    indexing.run({"document_splitter": {"documents": docs}})
    # indexing.run(docs)

    print("Creating BM25 retrieval pipeline")
    bm25_retrieval = Pipeline()
    bm25_retrieval.add_component("bm25_retriever", bm25_retriever)

    return bm25_retrieval


def setup_rag_pipeline(dataset):
    """
    This function sets up the RAG pipeline by providing a prompt to a genAI model, and calling the function
    setup the hybrid retrieval pipeline.

    :param 1: dataset - This is list of dictionaries containing the parsed data.

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
        model=cfg["llm"],
#         aws_access_key_id=Secret.from_token(bedrock_credentials.access_key),
#         aws_secret_access_key=Secret.from_token(bedrock_credentials.secret_key),
#         aws_session_token=Secret.from_token(bedrock_credentials.token),
#         aws_region_name=Secret.from_token(cfg["BEDROCK_REGION"]),
        max_length = 1000,
        temperature = 0,
    )

    pipe = setup_hybrid_pipeline(dataset)
    # pipe = setup_bm25_pipeline(dataset)

    print("Creating RAG pipeline...")
    pipe.add_component("prompt_builder", PromptBuilder(template=template))
    pipe.add_component("generator", generator)
    pipe.add_component("answer_builder", AnswerBuilder())

    pipe.connect("ranker", "prompt_builder.documents")
    # pipe.connect("bm25_retriever", "prompt_builder.documents")

    pipe.connect("prompt_builder", "generator")
    pipe.connect("generator.replies", "answer_builder.replies")
    pipe.connect("ranker", "answer_builder.documents")

    return pipe
