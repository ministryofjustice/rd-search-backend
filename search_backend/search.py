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

    def __init__(self, pipeline: Pipeline):
        """
        Args:
            :pipeline: The pipeline to use. This should be defined using the RetrievalPipeline() class.
        """

        self.pipeline = pipeline


    def _basic_query_verification(self, search_query: str):
        """
        There's no point running the pipeline if there's no proper query. Make sure the query length
        is greater than 1 character.
        """
        return len(search_query.strip()) <= 1


    def hybrid_search(self, search_query: str, filters: dict=None, top_k: int=10, threshold: float=0.):
        """
        Run a hybrid search pipeline and return results.

        :param search_query: The search query in the form of a text string.
        :param filters: Metadata filters. These should be formatted like:
            ```
            filters = {
                "operator": "AND",
                "conditions": [
                    {"field": "meta.type", "operator": "==", "value": "article"},
                    {"field": "meta.genre", "operator": "in", "value": ["economy", "politics"]},
                ],
            }
            ```
        :param top_k: How many results to return.
        :param threshold: Set a threshold match score (between 0 and 1)

        :return: A list of ranked search results.
        """

        if self._basic_query_verification(search_query):
            return []

        prediction = self.pipeline.run(
            {
                "dense_text_embedder": {"text": search_query},
                "bm25_retriever": {"query": search_query, "filters": filters, "top_k": top_k},
                "embedding_retriever": {"filters": filters, "top_k": top_k},
                "ranker": {"query": search_query, "top_k": top_k},
            }
        )

        if "ranker" not in prediction:
            return []
        elif "documents" not in prediction["ranker"]:
            return []
        else:
            docs = prediction["ranker"]["documents"]

        # Filter by threshold score
        if threshold > 0:
            docs = [doc for doc in docs if doc.score > threshold]

        return docs

    def semantic_search(self, search_query: str, filters: dict=None, top_k: int=10, threshold: float=0.):
        """
        Run a semantic search pipeline and return results.

        :param search_query: The search query in the form of a text string.
        :param filters: Metadata filters. These should be formatted like:
            ```
            filters = {
                "operator": "AND",
                "conditions": [
                    {"field": "meta.type", "operator": "==", "value": "article"},
                    {"field": "meta.genre", "operator": "in", "value": ["economy", "politics"]},
                ],
            }
            ```
        :param top_k: How many results to return.
        :param threshold: Set a threshold match score (between 0 and 1)

        :return: A list of ranked search results.
        """

        if self._basic_query_verification(search_query):
            return []

        print("Running search...")
        prediction = self.pipeline.run(
            {
                "dense_text_embedder": {"text": search_query},
                "embedding_retriever": {"filters": filters, "top_k": top_k},
                "ranker": {"query": search_query, "top_k": top_k},
            }
        )

        if "ranker" not in prediction:
            return []
        elif "documents" not in prediction["ranker"]:
            return []
        else:
            results = prediction["ranker"]["documents"]

        # Filter by threshold score
        if threshold > 0:
            results = [result for result in results if result.score > threshold]

        return results

    def bm25_search(self, search_query: str, filters: dict=None, top_k: int=100):
        """
        Run a BM25 search pipeline and return results.

        :param search_query: The search query in the form of a text string.
        :param filters: Metadata filters. These should be formatted like:
            ```
            filters = {
                "operator": "AND",
                "conditions": [
                    {"field": "meta.type", "operator": "==", "value": "article"},
                    {"field": "meta.genre", "operator": "in", "value": ["economy", "politics"]},
                ],
            }
            ```
        :param top_k: How many results to return.

        :return: A list of ranked search results.
        """

        if self._basic_query_verification(search_query):
            return []

        prediction = self.pipeline.run(
            {
                "bm25_retriever": {"query": search_query, "filters": filters, "top_k": top_k},
            }
        )

        if "bm25_retriever" not in prediction:
            return []
        elif "documents" not in prediction["bm25_retriever"]:
            return []
        else:
            results = prediction["bm25_retriever"]["documents"]

        return results
