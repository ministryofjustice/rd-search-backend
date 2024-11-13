import unittest

from haystack import Pipeline, Document
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack_integrations.components.embedders.fastembed import FastembedDocumentEmbedder
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore
from mockito import mock, when, verify, any
from mockito.matchers import captor

from search_backend.indexing_pipeline import IndexingPipeline


class TestIndexingPipeline(unittest.TestCase):
    def setUp(self):
        self.mock_document_store = mock(OpenSearchDocumentStore)

        self.mock_pipeline = mock(Pipeline)
        when(self.mock_pipeline).add_component(any(), any())
        when(self.mock_pipeline).connect(any(), any())

    def test_init_with_semantic_search(self):
        IndexingPipeline(self.mock_document_store, "dense_model", semantic=True, indexing=self.mock_pipeline)

        verify(self.mock_pipeline).add_component("document_splitter", any(DocumentSplitter))
        verify(self.mock_pipeline).add_component("document_writer", any(DocumentWriter))
        verify(self.mock_pipeline).add_component("dense_doc_embedder", any(FastembedDocumentEmbedder))
        verify(self.mock_pipeline).connect("document_splitter", "dense_doc_embedder")
        verify(self.mock_pipeline).connect("dense_doc_embedder", "document_writer")

    def test_init_without_semantic_search(self):
        IndexingPipeline(self.mock_document_store, "dense_model", indexing=self.mock_pipeline)

        verify(self.mock_pipeline).add_component("document_splitter", any(DocumentSplitter))
        verify(self.mock_pipeline).add_component("document_writer", any(DocumentWriter))
        verify(self.mock_pipeline).connect("document_splitter", "document_writer")

    def test_index_docs_method(self):
        pipeline = IndexingPipeline(self.mock_document_store, "dense_model", indexing=self.mock_pipeline)
        mock_docs = [mock(Document), mock(Document)]
        expected_result = {"some": "result"}

        when(self.mock_pipeline).run({"document_splitter": {"documents": mock_docs}}).thenReturn(expected_result)

        result = pipeline.index_docs(mock_docs)

        self.assertEqual(result, expected_result, f"Expected {expected_result}, but got {result}")

    def test_delete_docs_method(self):
        pipeline = IndexingPipeline(self.mock_document_store, "dense_model")
        doc_ids = ["1", "2"]
        id_metafield = "custom_id"

        mock_doc1 = mock()
        mock_doc1.id = "1"

        mock_doc2 = mock()
        mock_doc2.id = "2"

        mock_results = [mock_doc1, mock_doc2]

        when(self.mock_document_store).filter_documents(filters={
            "field": f"meta.{id_metafield}",
            "operator": "in",
            "value": doc_ids,
        }).thenReturn(mock_results)

        capture = captor()
        when(self.mock_document_store).delete_documents(capture)

        pipeline.delete_docs(doc_ids, id_metafield)

        # because the values returned by the document store are a set, the sort
        # order is not guaranteed, so we sort before doing the assertion
        self.assertEqual(sorted(doc_ids), sorted(capture.value))
