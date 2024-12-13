import unittest
from haystack import Pipeline, Document
from haystack_integrations.document_stores.opensearch import (
    OpenSearchDocumentStore,
)
from mockito import mock, when, verify, any
from search_backend.retrieval_pipeline import RetrievalPipeline
from search_backend.search import Search
from search_backend.threshold_score import ThresholdScore


class TestThresholdScore(unittest.TestCase):

    def setUp(self):
        self.mock_document_store = mock(OpenSearchDocumentStore)
        self.dense_embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        self.rerank_model = "cross-encoder/ms-marco-MiniLM-L-2-v2"
        
        # Mock some search results
        mock_prediction = [
            {"content": "high score", "score": 0.8},
            {"content": "low score", "score": 0.4},
        ]
        self.mock_prediction = [
            Document(content=doc["content"], score=doc["score"])
            for doc in mock_prediction
        ]


    def test_threshold_score_filter(self):
        """
        Test that only search results with a score over a defined threshold are returned by the search.
        """

        # Use a threshold where we expect 1 result
        threshold = 0.4
        results = ThresholdScore().run(documents=self.mock_prediction, score_threshold=threshold)
        results = results["documents"]

        self.assertEqual(
            len(results),
            1,
            f"Expected 1 result with score above 0.5 but got {len(results)}",
        )
        self.assertEqual(
            results[0].content,
            "high score",
            f"Expected content 'high score', got {results[0].content}",
        )

    def test_threshold_out_of_range(self):
        """
        Test that an error is raised if threshold scores outside the range 0-1 are defined
        """

        threshold = -1
        with self.assertRaises(ValueError):
            ThresholdScore().run(documents=self.mock_prediction, score_threshold=threshold)

        threshold = 1.1
        with self.assertRaises(ValueError):
            ThresholdScore().run(documents=self.mock_prediction, score_threshold=threshold)

    def test_no_input(self):
        """
        Test that an empty object is returned when no documents are provided
        """

        docs = []
        results = ThresholdScore().run(documents=docs, score_threshold=0)

        self.assertEqual(
            results,
            {"documents": []},
            f"Expected empty list in dictionary, but got {results}",
        )
        docs = []
        results = ThresholdScore().run(documents=docs, score_threshold=0)

        self.assertEqual(
            results,
            {"documents": []},
            f"Expected empty list in dictionary, but got {results}",
        )

        docs = None
        results = ThresholdScore().run(documents=docs, score_threshold=0)

        self.assertEqual(
            results,
            {"documents": []},
            f"Expected empty list in dictionary, but got {results}",
        )
