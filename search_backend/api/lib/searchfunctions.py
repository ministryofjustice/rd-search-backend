"""
Functions to run searches based on Haystack pipelines and print the results. 
"""

import re


def clean_query(query):
    """
    Performs cleaning on an input string to remove characters that aren't
    letters, numbers, spaces, or the following punctuation marks: -.?',
    """

    # Replace ampersands
    query = re.sub(r'\&', 'and', query)
    # Remove some punctuation marks
    query = re.sub(r"[^A-Za-z0-9\s\-\.\?\'\,\"]+", "", query)
    # Remove newlines
    query = re.sub(r'\n', ' ', query)
    # Replace multiple spaces with a single space
    query = re.sub(r'[\s\s]+', ' ', query)
    query = re.sub(r'[\.\.]+', '.', query)
    query = re.sub(r'[\,\,]+', ',', query)
    query = re.sub(r'[\?\?]+', '?', query)
    query = re.sub(r"[\'\']+", "'", query)
    query = re.sub(r'[\"\"]+', '"', query)
    # Trim any whitespace introduced by removing punctuation
    query = query.strip()

    return query


def detect_bad_query(query):
    """
    Function to flag queries that we don't want to pass to an AI. Currently flags queries that:
     - are too long
     - have unusual spacing - for example 'I g n o r e  a l l  p r e v i o u s  i n s t r u c t i o n'
    """

    # Check if the query exceeds a threshold length
    if len(query) > 500:
        print("The query is too long, please enter a shorter query.")
        return True

    unusual_spacing = re.match(
        r"[A-Za-z][\s\-\.\?\'\,][A-Za-z][\s\-\.\?\'\,][A-Za-z][\s\-\.\?\'\,][A-Za-z][\s\-\.\?\'\,]", query)
    if unusual_spacing:
        print("Invalid query. Please reduce spacing.")
        return True

    return False


def hybrid_search(search_query, pipeline, filters=None, top_k=10):
    """
    This allows us to enter a search query and search the data by running the pipeline and
    returning the specified number of results from each node.

    :param 1: The search query in the form of a text string.
    :param 2: The pipeline object. This is the output from setup_hybrid_pipeline().

    :return: Returns a list of ranked search outputs.
    """

    prediction = pipeline.run(
        {
            # "sparse_text_embedder": {"text": search_query},
            "dense_text_embedder": {"text": search_query},
            # "text_embedder": {"text": search_query},
            "bm25_retriever": {"query": search_query, "filters": filters, "top_k": top_k},
            "embedding_retriever": {"filters": filters, "top_k": top_k},
            # "retriever": {"filters": filters, "top_k": top_k},
            "ranker": {"query": search_query, "top_k": top_k},
        }
    )

    return prediction


def semantic_search(search_query, pipeline, filters=None, top_k=10):
    """
    This allows us to enter a search query and search the data by running the pipeline and
    returning the specified number of results from each node.

    :param 1: The search query in the form of a text string.
    :param 2: The pipeline object. This is the output from setup_semantic_pipeline().

    :return: Returns a list of ranked search outputs.
    """

    print("Running search...")
    prediction = pipeline.run(
        {
            "dense_text_embedder": {"text": search_query},
            "embedding_retriever": {"filters": filters, "top_k": top_k},
            "ranker": {"query": search_query, "top_k": top_k},
        }
    )

    return prediction


def bm25_search(search_query, pipeline, filters=None, top_k=10):
    """
    This allows us to enter a search query and search the data by running the pipeline and
    returning the specified number of results from each node.

    :param 1: The search query in the form of a text string.
    :param 2: The pipeline object. This is the output from setup_bm25_pipeline().

    :return: Returns a list of ranked search outputs.
    """

    prediction = pipeline.run(
        {
            "bm25_retriever": {"query": search_query, "filters": filters, "top_k": top_k},
        }
    )

    return prediction


def pretty_print_results(prediction):
    """
    This reformats the ranked search results to a more human-readable format.

    :param 1: The predicted results of the search query. This is the output of search().

    :return: Prints a human readable list of the ranked search results to the screen.
    """

    for doc in prediction:
        print('-----------------------------------')
        print(f'{doc.meta["title"]} - Score: {doc.score}')
        print(doc.content)
        print("\n")


def formatted_search_results(search_query: str, pipe, filters=None, top_k: int = 5):
    """
    Format hybrid search results
    """

    # Run text cleaning (to remove excess spaces and less common punctuation marks)
    cleaned_query = clean_query(search_query)

    # Generate an answer - this part needs to be run when a user enters a query
    if detect_bad_query(cleaned_query):
        answer = {
            "answer": "Invalid query. Please try again.",
            "sources": []
        }
    else:
        # This only runs if the query has passed a validation check
        results = hybrid_search(search_query, pipe, filters=filters, top_k=top_k)

        docs = []
        for doc in results["ranker"]['documents']:
            doc_info = {
                "title": doc.meta["title"],
                "score": doc.score,
                "text_excerpt": f'"{doc.content}"',
            }
            docs.append(doc_info)

        answer = {
            "answer": "Top matched documents",
            "sources": docs,
        }

    return answer
