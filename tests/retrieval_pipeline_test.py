import unittest

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
from mockito import mock, when, verify, any

from search_backend.retrieval_pipeline import RetrievalPipeline
from search_backend.threshold_score import ThresholdScore


class TestRetrievalPipeline(unittest.TestCase):

    def setUp(self):
        self.mock_document_store = mock(OpenSearchDocumentStore)
        self.dense_embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        self.rerank_model = "cross-encoder/ms-marco-MiniLM-L-2-v2"

    def create_mock_pipeline(self):
        # Create a fresh mock pipeline
        mock_pipeline = mock(Pipeline)
        when(mock_pipeline).add_component(any(str), any())
        when(mock_pipeline).connect(any(str), any(str))

        return mock_pipeline

    def test_setup_hybrid_pipeline(self):
        """
        Verify components of hybrid retrieval pipeline get set up
        """

        mock_pipeline = self.create_mock_pipeline()

        RetrievalPipeline(
            self.mock_document_store,
            self.dense_embedding_model,
            self.rerank_model,
            retrieval=mock_pipeline,
        ).setup_hybrid_pipeline()

        verify(mock_pipeline).add_component(
            "dense_text_embedder", any(FastembedTextEmbedder)
        )
        verify(mock_pipeline).add_component(
            "bm25_retriever", any(OpenSearchBM25Retriever)
        )
        verify(mock_pipeline).add_component(
            "embedding_retriever", any(OpenSearchEmbeddingRetriever)
        )
        verify(mock_pipeline).add_component(
            "ranker", any(TransformersSimilarityRanker)
        )
        verify(mock_pipeline).add_component(
            "semantic_threshold", any(ThresholdScore)
        )
        verify(mock_pipeline).add_component(
            "document_joiner", any(DocumentJoiner)
        )

        verify(mock_pipeline).connect(
            "dense_text_embedder.embedding",
            "embedding_retriever.query_embedding",
        )
        verify(mock_pipeline).connect("bm25_retriever", "document_joiner")
        verify(mock_pipeline).connect("embedding_retriever", "ranker")
        verify(mock_pipeline).connect("ranker", "semantic_threshold.documents")
        verify(mock_pipeline).connect("semantic_threshold", "document_joiner")

    def test_setup_semantic_pipeline(self):
        """
        Verify components of embedding retrieval pipeline get set up
        """

        mock_pipeline = self.create_mock_pipeline()

        RetrievalPipeline(
            self.mock_document_store,
            self.dense_embedding_model,
            self.rerank_model,
            retrieval=mock_pipeline,
        ).setup_semantic_pipeline()

        verify(mock_pipeline).add_component(
            "dense_text_embedder", any(FastembedTextEmbedder)
        )
        verify(mock_pipeline).add_component(
            "embedding_retriever", any(OpenSearchEmbeddingRetriever)
        )
        verify(mock_pipeline).add_component(
            "ranker", any(TransformersSimilarityRanker)
        )
        verify(mock_pipeline).add_component("threshold", any(ThresholdScore))
        verify(mock_pipeline).connect(
            "dense_text_embedder.embedding",
            "embedding_retriever.query_embedding",
        )
        verify(mock_pipeline).connect("embedding_retriever", "ranker")
        verify(mock_pipeline).connect("ranker", "threshold.documents")

    def test_setup_bm25_pipeline(self):
        """
        Verify components of BM25 retrieval pipeline get set up
        """

        mock_pipeline = self.create_mock_pipeline()

        RetrievalPipeline(
            self.mock_document_store, retrieval=mock_pipeline
        ).setup_bm25_pipeline()

        verify(mock_pipeline).add_component(
            "bm25_retriever", any(OpenSearchBM25Retriever)
        )

    def test_setup_no_input_pipeline(self):
        """
        Test that the Pipeline object gets set up if not provided as an arg.
        """

        pipeline = RetrievalPipeline(self.mock_document_store)

        self.assertEqual(
            type(pipeline.retrieval),
            Pipeline,
            f"Expected Pipeline object but got {type(pipeline.retrieval)}",
        )
