"""
Haystack pipeline functions for indexing, using Opensearch as the document store.
"""

from haystack import Document
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from haystack.components.preprocessors.document_splitter import DocumentSplitter
from haystack import Pipeline
from haystack_integrations.components.embedders.fastembed import (
    FastembedDocumentEmbedder,
    FastembedTextEmbedder,
)
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore


def run_indexing_pipeline(dataset, document_store: OpenSearchDocumentStore, cfg, semantic: bool=False):
    """
    This function splits the data into chunks and writes to a document store. If the 'semantic' arg
    is set to True then the chunks of text are embedded and written to a vector store.

    Args
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


def delete_docs(document_ids: List[str], id_metafield: str, document_store: OpenSearchDocumentStore):
    """
    Wrapper to show how to remove documents from the OpenSearch index.

    Args
    :document_ids: List of document ids to delete. These are IDs created by Haystack/OpenSearch.
    :id_metafield: The name of the field in the docstore metadata containing identifiers to use
        to select docs for deletion.
    :document_store: OpenSearchDocumentStore object that has been set up elsewhere.
    """

    # Match up a list of values in a particular field to IDs recognised by the docstore
    filters = {
        "field": f"meta.{id_metafield}",
        "operator": "in",
        "value": document_ids,
    }
    results = document_store.filter_documents(filters=filters)
    document_ids = {result.meta['_id'] for result in results['documents']}

    document_store.delete_documents(document_ids)
