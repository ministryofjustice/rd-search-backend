# rd-hr-smart-knowledge-management

## Dev

Working on the app relies on Python dependencies being installed locally. First set up a virtualenv and install 
dependencies:

```
python3 -m venv venv
source venv/bin/activate
pip install hatchling
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

### Indexing and searching documents in local OpenSearch

1. Start the stack:

```
docker compose build ; docker compose up
```

2. Get docs as a zip file, e.g. ~/Downloads/gdd_capability_pay.zip

3. Upload to local S3 bucket:

```
python scripts/upload_zip_to_s3.py --local ~/Downloads/gdd_capability_pay.zip build/unzip
```

4. Run process.py to download docs from local S3 and write index into opensearch:

```
AWS_URL_S3=http://0.0.0.0:4566 OPENSEARCH_URL=http://0.0.0.0:4566/opensearch/eu-west-2/rd-hr python search_backend/api/process.py
```

5. Run a test query against the index:

```
OPENSEARCH_URL=http://0.0.0.0:4566/opensearch/eu-west-2/rd-hr python search.py
```
