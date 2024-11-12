import unittest
from haystack import Pipeline
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore
from mockito import mock, when, verify, any
from mockito.matchers import captor

from search_backend.retrieval_pipeline import RetrievalPipeline
from search_backend.search import Search

class TestSearch(unittest.TestCase):

    def setUp(self):
        self.mock_document_store = mock(OpenSearchDocumentStore)
        self.dense_embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        self.rerank_model = "cross-encoder/ms-marco-MiniLM-L-2-v2"

    def test_bm25_search_method(self):
        """
        Mock basic functionality
        """

        mock_pipeline = mock(Pipeline)
        when(mock_pipeline).add_component(any(str), any())
        when(mock_pipeline).connect(any(str), any(str))

        bm25_pipeline = RetrievalPipeline(self.mock_document_store, retrieval=mock_pipeline)
        bm25_pipeline = bm25_pipeline.setup_bm25_pipeline()
        bm25_search_init = Search(bm25_pipeline)

        mock_prediction = [{"content": "test result", "score": 0.9}]
        when(bm25_search_init).bm25_search(...).thenReturn(mock_prediction)

        results = bm25_search_init.bm25_search("test query")

        self.assertEqual(len(results), 1, f"Expected 1 result but got {len(results)}")
        self.assertEqual(results[0]["content"], "test result", f"Expected content 'test result', got {results[0]['content']}")
        verify(bm25_search_init).bm25_search(...)