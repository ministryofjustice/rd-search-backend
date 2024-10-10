"""
Haystack pipeline functions for indexing and retrieval, using Opensearch as the document store.
"""

import os

from haystack import Document
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from haystack.components.preprocessors.document_splitter import DocumentSplitter
from haystack import Pipeline
from haystack.components.joiners import DocumentJoiner
from haystack.components.rankers import TransformersSimilarityRanker
from haystack_integrations.components.embedders.fastembed import (
    FastembedDocumentEmbedder,
    FastembedTextEmbedder,
)
from haystack_integrations.components.retrievers.opensearch import OpenSearchBM25Retriever, OpenSearchEmbeddingRetriever
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore



def run_indexing_pipeline(dataset, document_store: OpenSearchDocumentStore, cfg, semantic: bool=False):
    """
    This function splits the data into chunks and writes to a document store. If the 'semantic' arg
    is set to True then the chunks of text are embedded and written to a vector store.

    :dataset: This is list of dictionaries containing the parsed data.
    :document_store: DocumentStore object that has been set up elsewhere
    :cfg: configuration of the pipeline, as per get_config(). Includes the name of the embedding model.
    :semantic: set this to True to enable semantic/hybrid search. Otherwise uses a BM25 search.

    Other inputs, such as models to be used come from the config file.
    """

    # Convert the list of dictionaries into a list of Haystack Document objects
    docs = [
        Document(**content, id_hash_keys=["content", "meta"]) for content in dataset
    ]

    document_splitter = DocumentSplitter(
        split_by="word", split_length=128, split_overlap=32
    )

    indexing = Pipeline()
    indexing.add_component("document_splitter", document_splitter)

    if semantic:
        indexing.add_component(
            "dense_doc_embedder",
            FastembedDocumentEmbedder(model=cfg["dense_embedding_model"]),
        )

    indexing.add_component(
        "document_writer",
        DocumentWriter(document_store=document_store, policy=DuplicatePolicy.OVERWRITE),
    )

    if semantic:
        indexing.connect("document_splitter", "dense_doc_embedder")
        indexing.connect("dense_doc_embedder", "document_writer")
    else:
        indexing.connect("document_splitter", "document_writer")

    # Create the document store
    print("Running indexing pipeline...")
    indexing.run({"document_splitter": {"documents": docs}})



class RetrievalPipeline:
    """
    Class to set up the retrieval pipeline. Three options for the type of retrieval:
     - Hybrid (BM25 + dense embedding)
     - Semantic (dense embedding)
     - BM25
    """

    def __init__(self, document_store: OpenSearchDocumentStore, dense_embedding_model: str=None, rerank_model: str=None):
        """
        Args:
        :document_store: An Haystack/OpenSearch document store object, set up elsewhere.
        :dense_embedding_model: Name of the embedding model to use (assumes model is available from HuggingFace)
            for a semantic/hybrid search. Leave blank if using a BM25 search.
        :rerank_model: Name of the reranker/cross-encoder model to use (assumes model is available from HuggingFace)
            for a semantic/hybrid search
        """

        self.retrieval = Pipeline()
        self.document_store = document_store

        self.bm25_retriever = OpenSearchBM25Retriever(document_store=self.document_store, scale_score=True)
        self.embedding_retriever = OpenSearchEmbeddingRetriever(document_store=self.document_store)

        if dense_embedding_model is not None:
            self.dense_text_embedder = FastembedTextEmbedder(
                model=dense_embedding_model,
                cache_dir=os.getcwd() + "/embedding_cache",
            )
        else:
            self.dense_text_embedder = None

        if rerank_model is not None:
            self.rerank_model = rerank_model
        else:
            self.rerank_model = None

    def setup_hybrid_pipeline(self) -> Pipeline:
        """
        This function sets up the hybrid retrieval pipeline based on an existing document store.

        :return: Returns the pipeline object which can then be used to search the data for matches to a particular query.
        """

        hybrid_retrieval = self.retrieval

        hybrid_retrieval.add_component("dense_text_embedder", self.dense_text_embedder)
        hybrid_retrieval.add_component("bm25_retriever", self.bm25_retriever)
        hybrid_retrieval.add_component("embedding_retriever", self.embedding_retriever)
        hybrid_retrieval.add_component("document_joiner", DocumentJoiner(join_mode="reciprocal_rank_fusion"))
        hybrid_retrieval.add_component("ranker", TransformersSimilarityRanker(model=self.rerank_model))

        hybrid_retrieval.connect(
            "dense_text_embedder.embedding", "embedding_retriever.query_embedding"
        )
        hybrid_retrieval.connect("bm25_retriever", "document_joiner")
        hybrid_retrieval.connect("embedding_retriever", "document_joiner")
        hybrid_retrieval.connect("document_joiner", "ranker")

        return hybrid_retrieval


    def setup_semantic_pipeline(self) -> Pipeline:
        """
        This function sets up a dense embedding retrieval pipeline based on an existing document store.

        :return: Returns the pipeline object which can then be used to search the data for matches to a particular query.
        """

        retrieval = self.retrieval

        retrieval.add_component("dense_text_embedder", self.dense_text_embedder)
        retrieval.add_component("embedding_retriever", self.embedding_retriever)
        retrieval.add_component("ranker", TransformersSimilarityRanker(model=self.rerank_model))

        retrieval.connect(
            "dense_text_embedder.embedding", "embedding_retriever.query_embedding"
        )
        retrieval.connect("embedding_retriever", "ranker")

        return retrieval


    def setup_bm25_pipeline(self) -> Pipeline:
        """
        This function sets up a BM25 retrieval pipeline based on an existing document store.

        :return: Returns the pipeline object which can then be used to search the data for matches to a particular query.
        """

        bm25_retrieval = self.retrieval
        bm25_retrieval.add_component("bm25_retriever", self.bm25_retriever)

        return bm25_retrieval