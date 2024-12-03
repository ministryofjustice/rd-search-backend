<!--- Badges start --->
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)
[![codecov](https://codecov.io/github/ministryofjustice/rd-search-backend/graph/badge.svg?token=4UC7ESQEP2)](https://codecov.io/github/ministryofjustice/rd-search-backend)
<!--- Badges End --->

# rd-search-backend

Backend developed by the Digital R&D team for hybrid search apps. Related repos:

 - https://github.com/ministryofjustice/rd-service-catalogue
 - https://github.com/ministryofjustice/rd-ai-nexus

## Installation

Install with `pip install git+ssh://git@github.com/ministryofjustice/rd-search-backend.git`


## Quick start

Steps to get started indexing and searching documents in local OpenSearch (see also notebooks/demo_search.ipynb):

1. Open Docker Desktop

2. Start the stack

```
docker compose up
```

3. Run imports and define config variables

```
import json
from haystack import Document
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore
from search_backend.indexing_pipeline import IndexingPipeline
from search_backend.retrieval_pipeline import RetrievalPipeline
from search_backend.search import Search


cfg = {
    # Optional arg for the OpenSearch docstore, to prevent trying to index everything in one go
    "index_batch_size": 10,
    # Select embedding model for the semantic search. This should be a sentence-similarity
    # model available on Huggingface: https://huggingface.co/models?pipeline_tag=sentence-similarity
    "dense_embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    # The value of the embedding dimension must match that specified for the model defined above
    "embedding_dim": 384,
    # Language model used to rank search results better than the embedding retrieval can
    "rerank_model": "cross-encoder/ms-marco-MiniLM-L-2-v2",
}
```

4. Get some data

```
with open('tests/data/demo_data.json') as f:
    doc_list = json.load(f)

# Put into Haystack Document instances
docs = [Document(**content) for content in doc_list]
```

5. Connect to an OpenSearch container set up by `docker compose`

```
query_document_store = OpenSearchDocumentStore(
    hosts="http://0.0.0.0:4566/opensearch/eu-west-2/rd-demo",
    use_ssl=False,
    verify_certs=False,
    http_auth=("localstack", "localstack"),
    embedding_dim=cfg["embedding_dim"],
    batch_size=cfg["index_batch_size"],
)
```

6. Run the indexing pipeline to write documents to the vector store

```
indexer = IndexingPipeline(query_document_store, dense_embedding_model=cfg["dense_embedding_model"], semantic=True)
indexer.index_docs(docs)
```

7. Set up the retrieval pipeline

You have three options here: (1) BM25 retrieval, (2) dense embedding (semantic) retrieval, (3) hybrid (BM25 + dense embedding) retrieval:

BM25:
```
bm25_pipeline = RetrievalPipeline(query_document_store).setup_bm25_pipeline()
bm25_search_init = Search(bm25_pipeline)
```

Semantic:
```
semantic_pipeline = RetrievalPipeline(
    query_document_store,
    dense_embedding_model=cfg['dense_embedding_model'],
    rerank_model=cfg['rerank_model']
).setup_semantic_pipeline()
semantic_search_init = Search(semantic_pipeline)
```

Hybrid:
```
hybrid_pipeline = RetrievalPipeline(
    query_document_store,
    dense_embedding_model=cfg['dense_embedding_model'],
    rerank_model=cfg['rerank_model']
).setup_hybrid_pipeline()
hybrid_search_init = Search(hybrid_pipeline)
```

8. Run a search

BM25:
```
test_query = "lighthouse"
results = bm25_search_init.bm25_search(test_query, top_k=3)

for doc in results:
    print(f'{doc.meta["title"]} - Score: {doc.score}')
    print(doc.content)
```

Semantic:
```
test_query = "wonder that features plants"
results = semantic_search_init.semantic_search(test_query, top_k=3, threshold=0.00001)

for doc in results:
    print(f'{doc.meta["title"]} - Score: {doc.score}')
    print(doc.content)
```

Hybrid:
```
test_query = "wonder that features plants"
results = hybrid_search_init.hybrid_search(test_query, top_k=3, threshold=0.00001)

for doc in results:
    print(f'{doc.meta["title"]} - Score: {doc.score}')
    print(doc.content)
```


## Preparing data

Data should be converted into the following format to be compatible with the
Haystack framework:

```
document1 = {
    'meta': {
        # Insert any metadata in this dictionary, e.g:
        'title': 'Document title',
    }
    'content': 'Document content',
}

dataset = [
    document1,
    # Populate with more document dictionaries
]
```


 ## Dev

Working on the app relies on Python dependencies being installed locally.
First set up a virtualenv and install dependencies:

```
python3 -m venv venv
source venv/bin/activate
pip install -e '.[dev, search_backend]'
```

Prior to pushing commits to GitHub, run the pre-commit hooks with:
`pre-commit run --all-files`


### Run the unit tests

```
pytest tests
```

### Adding new dependencies

If you need to add a new dependency, insert it into pyproject.toml. Set upper
and lower bounds for the versions.

### Start the stack locally

```
docker compose build
docker compose up
```

To clear out existing containers:
```
docker system prune -a
```
