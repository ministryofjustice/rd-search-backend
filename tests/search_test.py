import unittest
from haystack import Pipeline, Document
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore
from mockito import mock, when, verify, any
from search_backend.retrieval_pipeline import RetrievalPipeline
from search_backend.search import Search


class TestSearch(unittest.TestCase):

    def setUp(self):
        self.mock_document_store = mock(OpenSearchDocumentStore)
        self.dense_embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        self.rerank_model = "cross-encoder/ms-marco-MiniLM-L-2-v2"

    def create_mock_pipeline(self):
        # Create a fresh mock pipeline
        mock_pipeline = mock(Pipeline)
        when(mock_pipeline).add_component(any(str), any())
        when(mock_pipeline).connect(any(str), any(str))

        return(mock_pipeline)

    def test_bm25_search_method(self):
        """
        Check basic BM25 search functionality
        """

        # Create a fresh mock pipeline
        mock_pipeline = self.create_mock_pipeline()

        # Set up the Search instance
        bm25_pipeline = RetrievalPipeline(
            self.mock_document_store, retrieval=mock_pipeline
        ).setup_bm25_pipeline()
        bm25_search_init = Search(bm25_pipeline)

        # Mock the behaviour of the Search instance
        mock_prediction = [{"content": "test result", "score": 0.9}]
        mock_prediction = [Document(content=doc["content"], score=doc["score"]) for doc in mock_prediction]
        when(bm25_search_init).bm25_search(...).thenReturn(mock_prediction)

        results = bm25_search_init.bm25_search("test query")

        # Run tests
        self.assertEqual(len(results), 1, f"Expected 1 result but got {len(results)}")
        self.assertEqual(results[0].content, "test result", f"Expected content 'test result', got {results[0].content}")
        verify(bm25_search_init).bm25_search(...)


    def test_semantic_search_method(self):
        """
        Check basic semantic search functionality
        """

        # Create a fresh mock pipeline
        mock_pipeline = self.create_mock_pipeline()

        # Set up the Search instance
        semantic_pipeline = RetrievalPipeline(
            self.mock_document_store, self.dense_embedding_model, self.rerank_model, retrieval=mock_pipeline
        ).setup_semantic_pipeline()
        semantic_search_init = Search(semantic_pipeline)

        # Mock the behaviour of the Search instance
        mock_prediction = [{"content": "test result", "score": 0.9}]
        mock_prediction = [Document(content=doc["content"], score=doc["score"]) for doc in mock_prediction]
        when(semantic_search_init).semantic_search(...).thenReturn(mock_prediction)

        results = semantic_search_init.semantic_search("test query")

        # Run tests
        self.assertEqual(len(results), 1, f"Expected 1 result but got {len(results)}")
        self.assertEqual(results[0].content, "test result", f"Expected content 'test result', got {results[0].content}")
        verify(semantic_search_init).semantic_search(...)


    def test_hybrid_search_method(self):
        """
        Check basic hybrid search functionality
        """

        # Create a fresh mock pipeline
        mock_pipeline = self.create_mock_pipeline()

        # Set up the Search instance
        hybrid_pipeline = RetrievalPipeline(
            self.mock_document_store, self.dense_embedding_model, self.rerank_model, retrieval=mock_pipeline
        ).setup_hybrid_pipeline()
        hybrid_pipeline_init = Search(hybrid_pipeline)

        # Mock the behaviour of the Search instance
        mock_prediction = [{"content": "test result", "score": 0.9}]
        mock_prediction = [Document(content=doc["content"], score=doc["score"]) for doc in mock_prediction]
        when(hybrid_pipeline_init).hybrid_search(...).thenReturn(mock_prediction)

        results = hybrid_pipeline_init.hybrid_search("test query")

        # Run tests
        self.assertEqual(len(results), 1, f"Expected 1 result but got {len(results)}")
        self.assertEqual(results[0].content, "test result", f"Expected content 'test result', got {results[0].content}")
        verify(hybrid_pipeline_init).hybrid_search(...)


    def test_hybrid_search_threshold_filter(self):
        """
        Test that only search results with a score over a defined threshold are returned by the hybrid search.
        """

        # Create a fresh mock pipeline
        mock_pipeline = self.create_mock_pipeline()

        # Mock the search results
        mock_prediction = [{"content": "high score", "score": 0.8}, {"content": "low score", "score": 0.4}]
        mock_prediction = {"ranker": {"documents": [Document(content=doc["content"], score=doc["score"]) for doc in mock_prediction]}}
        
        # Set up the Search instance
        hybrid_pipeline = RetrievalPipeline(
            self.mock_document_store, self.dense_embedding_model, self.rerank_model, retrieval=mock_pipeline
        ).setup_hybrid_pipeline()

        # Mock the part where the retrieval pipeline is run
        when(hybrid_pipeline).run(...).thenReturn(mock_prediction)
        hybrid_pipeline_init = Search(hybrid_pipeline)

        # Use a threshold where we expect 2 results
        threshold = 0.1
        results = hybrid_pipeline_init.hybrid_search("test query", threshold=threshold)

        self.assertEqual(len(results), 2, f"Expected 2 results but got {len(results)}")

        # Use a threshold where we expect 1 result
        threshold = 0.4
        results = hybrid_pipeline_init.hybrid_search("test query", threshold=threshold)

        self.assertEqual(len(results), 1, f"Expected 1 result with score above 0.5 but got {len(results)}")
        self.assertEqual(results[0].content, "high score", f"Expected content 'high score', got {results[0].content}")

        # Use a threshold where we expect 0 results
        threshold = 0.9
        results = hybrid_pipeline_init.hybrid_search("test query", threshold=threshold)

        self.assertEqual(len(results), 0, f"Expected no results but got {len(results)}")


    def test_semantic_search_threshold_filter(self):
        """
        Test that only search results with a score over a defined threshold are returned by the semantic search.
        """

        # Create a fresh mock pipeline
        mock_pipeline = self.create_mock_pipeline()

        # Mock the search results
        mock_prediction = [{"content": "high score", "score": 0.8}, {"content": "low score", "score": 0.4}]
        mock_prediction = {"ranker": {"documents": [Document(content=doc["content"], score=doc["score"]) for doc in mock_prediction]}}
        
        # Set up the Search instance
        semantic_pipeline = RetrievalPipeline(
            self.mock_document_store, self.dense_embedding_model, self.rerank_model, retrieval=mock_pipeline
        ).setup_semantic_pipeline()

        # Mock the part where the retrieval pipeline is run
        when(semantic_pipeline).run(...).thenReturn(mock_prediction)
        semantic_pipeline_init = Search(semantic_pipeline)

        # Use a threshold where we expect 1 result
        threshold = 0.4
        results = semantic_pipeline_init.semantic_search("test query", threshold=threshold)

        self.assertEqual(len(results), 1, f"Expected 1 result with score above 0.5 but got {len(results)}")
        self.assertEqual(results[0].content, "high score", f"Expected content 'high score', got {results[0].content}")


    def test_search_invalid_query(self):
        """
        Check nothing gets returned when an empty/invalid query is entered.
        """

        # Set up the Search instance
        pipeline_init = Search(Pipeline())

        # Test with empty string
        results = pipeline_init.hybrid_search("")
        self.assertEqual(len(results), 0, f"Expected 0 results but got {len(results)}")

        # Test with blank spaces
        results = pipeline_init.hybrid_search("   ")
        self.assertEqual(len(results), 0, f"Expected 0 results but got {len(results)}")

        # Test with single character
        results = pipeline_init.hybrid_search("A")
        self.assertEqual(len(results), 0, f"Expected 0 results but got {len(results)}")

        # Test with semantic search method
        results = pipeline_init.semantic_search("  ")
        self.assertEqual(len(results), 0, f"Expected 0 results but got {len(results)}")

        # Test with BM25 search method
        results = pipeline_init.bm25_search("  ")
        self.assertEqual(len(results), 0, f"Expected 0 results but got {len(results)}")


    def test_hybrid_search_unexpected_object_returned(self):
        """
        Check the hybrid search behaviour when an unexpected object is returned by the Haystack pipeline
        """

        # Create a fresh mock pipeline
        mock_pipeline = self.create_mock_pipeline()

        # Set up the retrieval pipeline
        retrieval_pipeline = RetrievalPipeline(
            self.mock_document_store, self.dense_embedding_model, self.rerank_model, retrieval=mock_pipeline
        ).setup_hybrid_pipeline()

        # Mock the part where the retrieval pipeline is run and return something unexpected (None)
        when(retrieval_pipeline).run(...).thenReturn(None)
        results = Search(retrieval_pipeline).hybrid_search("test query")

        self.assertEqual(len(results), 0, f"Expected 0 results but got {len(results)}")

        # Try with something returned that isn't None
        when(retrieval_pipeline).run(...).thenReturn({'A': 1})
        results = Search(retrieval_pipeline).hybrid_search("test query")

        # Try with something that's only partially structured correctly
        when(retrieval_pipeline).run(...).thenReturn({'ranker': {'A': 1}})
        results = Search(retrieval_pipeline).hybrid_search("test query")

        self.assertEqual(len(results), 0, f"Expected 0 results but got {len(results)}")


    def test_semantic_search_unexpected_object_returned(self):
        """
        Check the semantic search behaviour when an unexpected object is returned by the Haystack pipeline
        """

        # Create a fresh mock pipeline
        mock_pipeline = self.create_mock_pipeline()

        # Set up the Search instance
        retrieval_pipeline = RetrievalPipeline(
            self.mock_document_store, self.dense_embedding_model, self.rerank_model, retrieval=mock_pipeline
        ).setup_semantic_pipeline()

        # Mock the part where the retrieval pipeline is run and return something unexpected (None)
        when(retrieval_pipeline).run(...).thenReturn(None)
        results = Search(retrieval_pipeline).semantic_search("test query")

        self.assertEqual(len(results), 0, f"Expected 0 results but got {len(results)}")

        # Try with something returned that isn't None
        when(retrieval_pipeline).run(...).thenReturn({'A': 1})
        results = Search(retrieval_pipeline).semantic_search("test query")

        self.assertEqual(len(results), 0, f"Expected 0 results but got {len(results)}")

        # Try with something that's only partially structured correctly
        when(retrieval_pipeline).run(...).thenReturn({'ranker': {'A': 1}})
        results = Search(retrieval_pipeline).semantic_search("test query")

        self.assertEqual(len(results), 0, f"Expected 0 results but got {len(results)}")


    def test_bm25_search_unexpected_object_returned(self):
        """
        Check the BM25 search behaviour when an unexpected object is returned by the Haystack pipeline
        """

        # Create a fresh mock pipeline
        mock_pipeline = self.create_mock_pipeline()

        # Set up the Search instance
        retrieval_pipeline = RetrievalPipeline(
            self.mock_document_store, self.dense_embedding_model, self.rerank_model, retrieval=mock_pipeline
        ).setup_bm25_pipeline()

        # Mock the part where the retrieval pipeline is run and return something unexpected (None)
        when(retrieval_pipeline).run(...).thenReturn(None)
        results = Search(retrieval_pipeline).bm25_search("test query")

        self.assertEqual(len(results), 0, f"Expected 0 results but got {len(results)}")

        # Try with something returned that isn't None
        when(retrieval_pipeline).run(...).thenReturn({'A': 1})
        results = Search(retrieval_pipeline).bm25_search("test query")

        self.assertEqual(len(results), 0, f"Expected 0 results but got {len(results)}")

        # Try with something that's only partially structured correctly
        when(retrieval_pipeline).run(...).thenReturn({'bm25_retriever': {'A': 1}})
        results = Search(retrieval_pipeline).bm25_search("test query")

        self.assertEqual(len(results), 0, f"Expected 0 results but got {len(results)}")

        # Try with a correctly structured object
        mock_prediction = [{"content": "high score", "score": 0.8}, {"content": "low score", "score": 0.4}]
        mock_prediction = {"bm25_retriever": {"documents": [Document(content=doc["content"], score=doc["score"]) for doc in mock_prediction]}}
        when(retrieval_pipeline).run(...).thenReturn(mock_prediction)
        results = Search(retrieval_pipeline).bm25_search("test query")

        self.assertEqual(len(results), 2, f"Expected 2 results but got {len(results)}")
