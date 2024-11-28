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

4. Define some data

```
doc_list = [
    {
        "meta": {"title": "Great Pyramid of Giza"},
        "content": "The Great Pyramid of Giza is the largest Egyptian pyramid. It served as the tomb of pharaoh Khufu, who ruled during the Fourth Dynasty of the Old Kingdom. Built c. 2600 BC, over a period of about 26 years, the pyramid is the oldest of the Seven Wonders of the Ancient World, and the only wonder that has remained largely intact. It is the most famous monument of the Giza pyramid complex, which is part of the UNESCO World Heritage Site 'Memphis and its Necropolis'. It is situated at the northeastern end of the line of the three main pyramids at Giza.",
    },
    {
        "meta": {"title": "Hanging Gardens of Babylon"},
        "content": "The Hanging Gardens of Babylon were one of the Seven Wonders of the Ancient World listed by Hellenic culture. They were described as a remarkable feat of engineering with an ascending series of tiered gardens containing a wide variety of trees, shrubs, and vines, resembling a large green mountain constructed of mud bricks. It was said to have been built in the ancient city of Babylon, near present-day Hillah, Babil province, in Iraq. The Hanging Gardens' name is derived from the Greek word κρεμαστός (kremastós, lit. 'overhanging'), which has a broader meaning than the modern English word 'hanging' and refers to trees being planted on a raised structure such as a terrace.",
    },
    {
        "meta": {"title": "Statue of Zeus at Olympia"},
        "content": "The Statue of Zeus at Olympia was a giant seated figure, about 12.4 m (41 ft) tall, made by the Greek sculptor Phidias around 435 BC at the sanctuary of Olympia, Greece, and erected in the Temple of Zeus there. Zeus is the sky and thunder god in ancient Greek religion, who rules as king of the gods on Mount Olympus.",
    },
    {
        "meta": {"title": "Temple of Artemis"},
        "content": "The Temple of Artemis or Artemision (Greek: Ἀρτεμίσιον; Turkish: Artemis Tapınağı), also known as the Temple of Diana, was a Greek temple dedicated to an ancient, localised form of the goddess Artemis (equated with the Roman goddess Diana). It was located in Ephesus (near the modern town of Selçuk in present-day Turkey). By AD 401 it is belived it had been ruined or destroyed.[1] Only foundations and fragments of the last temple remain at the site. ",
    },
    {
        "meta": {"title": "Mausoleum at Halicarnassus"},
        "content": "The Mausoleum at Halicarnassus or Tomb of Mausolus[a] (Ancient Greek: Μαυσωλεῖον τῆς Ἁλικαρνασσοῦ; Turkish: Halikarnas Mozolesi) was a tomb built between 353 and 351 BC in Halicarnassus (present Bodrum, Turkey) for Mausolus, an Anatolian from Caria and a satrap in the Achaemenid Persian Empire, and his sister-wife Artemisia II of Caria. The structure was designed by the Greek architects Satyros and Pythius of Priene. Its elevated tomb structure is derived from the tombs of neighbouring Lycia, a territory Mausolus had invaded and annexed c. 360 BC, such as the Nereid Monument.",
    },
    {
        "meta": {"title": "Colossus of Rhodes"},
        "content": "The Colossus of Rhodes (Ancient Greek: ὁ Κολοσσὸς Ῥόδιος, romanized: ho Kolossòs Rhódios; Modern Greek: Κολοσσός της Ρόδου, romanized: Kolossós tis Ródou) was a statue of the Greek sun god Helios, erected in the city of Rhodes, on the Greek island of the same name, by Chares of Lindos in 280 BC. One of the Seven Wonders of the Ancient World, it was constructed to celebrate the successful defence of Rhodes city against an attack by Demetrius I of Macedon, who had besieged it for a year with a large army and navy.",
    },
    {
        "meta": {"title": "Lighthouse of Alexandria"},
        "content": "The Lighthouse of Alexandria, sometimes called the Pharos of Alexandria (/ˈfɛərɒs/ FAIR-oss; Ancient Greek: ὁ Φάρος τῆς Ἀλεξανδρείας, romanized: ho Pháros tês Alexandreías, contemporary Koine Greek pronunciation: [ho pʰáros tɛ̂ːs aleksandrěːaːs]; Arabic: فنار الإسكندرية), was a lighthouse built by the Ptolemaic Kingdom of Ancient Egypt, during the reign of Ptolemy II Philadelphus (280–247 BC). It has been estimated to have been at least 100 metres (330 ft) in overall height. One of the Seven Wonders of the Ancient World, for many centuries it was one of the tallest man-made structures in the world.",
    },
]

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