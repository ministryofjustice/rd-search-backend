"""
Functions to run searches based on Haystack pipelines and print the results.
"""

from haystack import Pipeline

class Search:
    """
    Run different types of search, based on an existing pipeline:
    either BM25, semantic, or hybrid (semantic + BM25).

    NOTE: the search function selected needs to correspond the pipeline set up
    with RetrievalPipeline(). i.e:
     - setup_hybrid_pipeline -> hybrid_search
     - setup_semantic_pipeline -> semantic_search
     - setup_bm25_pipeline -> bm25_search
    """

    def __init__(self, search_query: str, pipeline: Pipeline, filters: dict=None, top_k: int=10):
        """
        Args:
            :search_query: The search query in the form of a text string.
            :pipeline: The pipeline to use. This should be defined using the RetrievalPipeline() class.
            :filters: Metadata filters. These should be formatted like:
                ```
                filters = {
                    "operator": "AND",
                    "conditions": [
                        {"field": "meta.type", "operator": "==", "value": "article"},
                        {"field": "meta.genre", "operator": "in", "value": ["economy", "politics"]},
                    ],
                }
                ```
            :top_k: How many results to return.
        """

        self.search_query = search_query
        self.pipeline = pipeline
        self.filters = filters
        self.top_k = top_k

    def hybrid_search(self):
        """
        Run a hybrid search pipeline and return results.

        :return: A list of ranked search results.
        """

        prediction = self.pipeline.run(
            {
                "dense_text_embedder": {"text": self.search_query},
                "bm25_retriever": {"query": self.search_query, "filters": self.filters, "top_k": self.top_k},
                "embedding_retriever": {"filters": self.filters, "top_k": self.top_k},
                "ranker": {"query": self.search_query, "top_k": self.top_k},
            }
        )

        return prediction

    def semantic_search(self):
        """
        Run a semantic search pipeline and return results.

        :return: A list of ranked search results.
        """

        print("Running search...")
        prediction = self.pipeline.run(
            {
                "dense_text_embedder": {"text": self.search_query},
                "embedding_retriever": {"filters": self.filters, "top_k": self.top_k},
                "ranker": {"query": self.search_query, "top_k": self.top_k},
            }
        )

        return prediction

    def bm25_search(self):
        """
        Run a BM25 search pipeline and return results.

        :return: A list of ranked search results.
        """

        prediction = self.pipeline.run(
            {
                "bm25_retriever": {"query": self.search_query, "filters": self.filters, "top_k": self.top_k},
            }
        )

        return prediction
