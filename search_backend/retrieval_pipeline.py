"""
Haystack pipeline functions and retrieval, using Opensearch as the document store.
"""

import os
from haystack import Pipeline
from haystack.components.joiners import DocumentJoiner
from haystack.components.rankers import TransformersSimilarityRanker
from haystack_integrations.components.embedders.fastembed import (
    FastembedTextEmbedder,
)
from haystack_integrations.components.retrievers.opensearch import (
    OpenSearchBM25Retriever,
    OpenSearchEmbeddingRetriever,
)
from haystack_integrations.document_stores.opensearch import (
    OpenSearchDocumentStore,
)
from search_backend.threshold_score import ThresholdScore


class RetrievalPipeline:
    """
    Class to set up the retrieval pipeline. Three options for the type of retrieval:
     - Hybrid (BM25 + dense embedding)
     - Semantic (dense embedding)
     - BM25
    """

    def __init__(
        self,
        document_store: OpenSearchDocumentStore,
        dense_embedding_model: str = None,
        rerank_model: str = None,
        retrieval: Pipeline = None,
    ):
        """
        :param document_store: An Haystack/OpenSearch document store object, set up elsewhere.
        :param dense_embedding_model: Name of the embedding model to use (assumes model is available from HuggingFace)
            for a semantic/hybrid search. Leave blank if using a BM25 search.
        :param rerank_model: Name of the reranker/cross-encoder model to use (assumes model is available from HuggingFace)
            for a semantic/hybrid search
        :param retrieval: pipeline to do the retrieval, which will be configured in this constructor
        """

        if retrieval is None:
            retrieval = Pipeline()

        self.retrieval = retrieval
        self.document_store = document_store

        self.bm25_retriever = OpenSearchBM25Retriever(
            document_store=self.document_store,
            scale_score=True,
            fuzziness="AUTO",
        )
        self.embedding_retriever = OpenSearchEmbeddingRetriever(
            document_store=self.document_store
        )

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
        This function sets up the hybrid retrieval pipeline based on an existing document
        store.

        Notes:
         - Although a reranker is used, it is only applied to the dense embedding retrieval
           (prior to joining with results from the BM25 retrieval). This is because the
           pipeline is set up to allow all matches to be returned from the BM25 retrieval,
           and if there are many matches it would cause the reranking stage to be very slow.
         - Results from the BM25 and embedding retrieval are joined using reciprocal rank
           fusion

        :return: Returns the pipeline object which can then be used to search the data for
            matches to a particular query.
        """

        self.retrieval.add_component(
            "dense_text_embedder", self.dense_text_embedder
        )
        self.retrieval.add_component("bm25_retriever", self.bm25_retriever)
        self.retrieval.add_component(
            "embedding_retriever", self.embedding_retriever
        )
        self.retrieval.add_component(
            "ranker", TransformersSimilarityRanker(model=self.rerank_model)
        )
        self.retrieval.add_component("semantic_threshold", ThresholdScore())
        self.retrieval.add_component(
            "document_joiner",
            DocumentJoiner(join_mode="reciprocal_rank_fusion"),
        )

        self.retrieval.connect(
            "dense_text_embedder.embedding",
            "embedding_retriever.query_embedding",
        )
        self.retrieval.connect("bm25_retriever", "document_joiner")
        self.retrieval.connect("embedding_retriever", "ranker")
        self.retrieval.connect("ranker", "semantic_threshold.documents")
        self.retrieval.connect("semantic_threshold", "document_joiner")

        return self.retrieval

    def setup_semantic_pipeline(self) -> Pipeline:
        """
        This function sets up a dense embedding retrieval pipeline based on an existing document store.

        :return: Returns the pipeline object which can then be used to search the data for matches to a particular query.
        """

        self.retrieval.add_component(
            "dense_text_embedder", self.dense_text_embedder
        )
        self.retrieval.add_component(
            "embedding_retriever", self.embedding_retriever
        )
        self.retrieval.add_component(
            "ranker", TransformersSimilarityRanker(model=self.rerank_model)
        )
        self.retrieval.add_component("threshold", ThresholdScore())

        self.retrieval.connect(
            "dense_text_embedder.embedding",
            "embedding_retriever.query_embedding",
        )
        self.retrieval.connect("embedding_retriever", "ranker")
        self.retrieval.connect("ranker", "threshold.documents")

        return self.retrieval

    def setup_bm25_pipeline(self) -> Pipeline:
        """
        This function sets up a BM25 retrieval pipeline based on an existing document store.

        :return: Returns the pipeline object which can then be used to search the data for matches to a particular query.
        """

        self.retrieval.add_component("bm25_retriever", self.bm25_retriever)

        return self.retrieval
