from typing import Iterable, Any

from haystack import Pipeline, Document
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from haystack_integrations.components.embedders.fastembed import FastembedDocumentEmbedder
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore


class IndexingPipeline:
    """
    Index documents into opensearch document store.
    """

    def __init__(
            self,
            document_store: OpenSearchDocumentStore,
            dense_embedding_model: str,
            semantic: bool = False,
            indexing: Pipeline = Pipeline(),
            split_length: int = 64,
            split_overlap: int = 8,
            split_threshold: int = 0
    ):
        """
        :param document_store: DocumentStore object that has been set up elsewhere
        :param dense_embedding_model: name of the dense embedding model
        :param semantic: set this to True to enable semantic/hybrid search. Otherwise uses a BM25 search. If True,
        the chunks of text are embedded and written to a vector store.
        :param indexing: pipeline to do the indexing, which will be configured in this constructor
        """
        self.document_store = document_store

        document_splitter = DocumentSplitter(
            split_by="word",
            split_length=split_length,
            split_overlap=split_overlap,
            split_threshold=split_threshold,
        )

        indexing.add_component("document_splitter", document_splitter)

        indexing.add_component(
            "document_writer",
            DocumentWriter(document_store=self.document_store, policy=DuplicatePolicy.OVERWRITE),
        )

        if semantic:
            indexing.add_component(
                "dense_doc_embedder",
                FastembedDocumentEmbedder(model=dense_embedding_model),
            )

            indexing.connect("document_splitter", "dense_doc_embedder")
            indexing.connect("dense_doc_embedder", "document_writer")
        else:
            indexing.connect("document_splitter", "document_writer")

        self.indexing = indexing

    def index_docs(self, docs: Iterable[Document]):
        """
        Split the data into chunks and write it to the document store.

        :param docs: Haystack Document objects to be indexed.
        """
        return self.indexing.run({"document_splitter": {"documents": docs}})

    def delete_docs(self, document_ids: list[Any], id_metafield: str):
        """
        Remove documents from the OpenSearch index.

        :param document_ids: List of document ids to delete. These are values of the id_metafield field of
        documents in the document store which are to be deleted.
        :param id_metafield: The name of the field in the docstore metadata containing identifiers to use
            to select docs for deletion.
        """

        # Match up a list of values in a particular field to IDs recognised by the docstore
        filters = {
            "field": f"meta.{id_metafield}",
            "operator": "in",
            "value": document_ids,
        }

        results = self.document_store.filter_documents(filters=filters)
        doc_ids = {result.id for result in results}

        self.document_store.delete_documents(list(doc_ids))
