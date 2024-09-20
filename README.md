# rd-hr-smart-knowledge-management

## Dev

Working on the app relies on Python dependencies being installed locally. First set up a virtualenv and install 
dependencies:

```
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev,frontend,api]"
```

### Adding new dependencies

If you need to add a new dependency, insert it into setup.py, using the `dev`, `frontend`, or `api` section of 
the `extras_require` block, depending on where the dependency is required.

Set upper and lower bounds for the versions if adding a dependency to frontend or api.

The requirements.txt files for the frontend and api are generated at the point when the docker images are built, using
`pip-compile` running against the setup.py file.

### Start the stack locally

```
docker compose build
docker compose up
```

The UI will then be available at http://localhost:8080/.

### Run the frontend without building the Docker image

First start the API:

```
docker compose up api
```

Then run the frontend app in a separate console:

```
cd frontend/src/
API_URL=http://0.0.0.0:8081 flask run --port 8080
```

The UI will then be available at http://localhost:8080/ (note that this is the same URL as the docker container so
they will clash if you run the frontend like this plus run it from Docker at the same time).

### Full health checks

The frontend has a health-check endpoint which will test connectivity to the API. It is accessible at:

http://localhost:8080/health-check?full=true

The same path can also be called from the deployed application, e.g.

https://rd-hr-smart-knowledge-management-dev.apps.live.cloud-platform.service.justice.gov.uk/health-check?full=true

### Indexing and searching documents in local OpenSearch

Before doing the steps below, you'll need to install the datapipeline dependencies with:

```
pip install -e ".[datapipeline]"
```

1. Start the stack:

```
docker compose build ; docker compose up
```

2. Get policy docs as a zip file, e.g. ~/Downloads/gdd_capability_pay.zip

3. Upload to local S3 bucket:

```
cd scripts
python upload_zip_to_s3.py --local ~/Downloads/gdd_capability_pay.zip build/unzip
```

4. Run process.py to download docs from local S3 and write index into opensearch:

```
cd ../api/src
AWS_URL_S3=http://0.0.0.0:4566 OPENSEARCH_URL=http://0.0.0.0:4566/opensearch/eu-west-2/rd-hr python process.py
```

5. Run a test query against the index:

```
OPENSEARCH_URL=http://0.0.0.0:4566/opensearch/eu-west-2/rd-hr python search.py
```

## Deployment

### Indexing documents in the Cloud Platform (UNTESTED)

There is no need to upload docs to S3 bucket, as they are already present (added manually to the Analytical Platform).
If they do need to be uploaded, the upload_zip_to_s3.py script can be used for that (see above).

To perform indexing into the OpenSearch cluster, 
[log in to a Kubernetes API pod](https://dsdmoj.atlassian.net/wiki/spaces/HRE/pages/5057576974/Running+scripts+on+pods+in+the+Cloud+Platform) 
and run these commands:

```
cd /app
pip install -e ".[datapipeline]"
cd datapipeline
python process.py
```

Note that environment variables which have to be set locally are not required when running the script from the 
Cloud Platform.
