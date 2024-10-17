# rd-search-backend

Backend developed by the Digital R&D team for hybrid search apps. Related repos:

 - https://github.com/ministryofjustice/rd-service-catalogue
 - https://github.com/ministryofjustice/rd-ai-nexus

## Installation

Install with `pip install git+ssh://git@github.com/ministryofjustice/rd-search-backend.git`

## Dev

Working on the app relies on Python dependencies being installed locally. First set up a virtualenv and install 
dependencies:

```
python3 -m venv venv
source venv/bin/activate
pip install -e '.[dev, search_backend]'
```

To build the package manifest with hatchling, run `hatchling build` from
terminal at the project root. By default this writes to ./dist/, but can be
directed with the `-d` flag.

### Adding new dependencies

If you need to add a new dependency, insert it into pyproject.toml. Set upper and lower bounds for the versions.

### Start the stack locally

```
docker compose build
docker compose up
```

The UI will then be available at http://localhost:8080/.

### Full health checks

The frontend has a health-check endpoint which will test connectivity to the API. It is accessible locally at:

http://localhost:8080/health-check?full=true

### Preparing data

Data should be converted into the following format to be compatible with the Haystack framework:

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

### Indexing and searching documents in local OpenSearch

1. Open Docker Desktop

2. Start the stack:

```
docker compose build ; docker compose up
```

3. Get docs as a json file, e.g. ~/Downloads/documents.json

...to be continued.



4. Run process.py to process data and write index into opensearch:

```
AWS_URL_S3=http://0.0.0.0:4566 OPENSEARCH_URL=http://0.0.0.0:4566/opensearch/eu-west-2/rd-hr python scripts/process.py
```

You should now be able to access the application at http://localhost:8080/ and perform a search.

