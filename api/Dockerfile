FROM python:3.10-bookworm

WORKDIR /app

HEALTHCHECK --interval=5s --timeout=3s CMD curl -f http://0.0.0.0:8081/health-check || exit 1

COPY setup.py setup.py

RUN pip install --upgrade pip && \
    pip install pip-tools

RUN pip-compile --extra api setup.py -o requirements.txt && \
    pip-compile --extra datapipeline setup.py -o requirements_pipeline.txt && \
    rm setup.py && \
    pip uninstall -y pip-tools

RUN pip install -r requirements.txt && rm requirements.txt
RUN pip install -r requirements_pipeline.txt

COPY api/src/app.py .
COPY api/src/process.py .
COPY api/src/test_search_components.py .
COPY api/src/lib ./lib
COPY api/src/fixtures ./fixtures
# COPY datapipeline ./datapipeline

RUN addgroup --system flaskgroup && \
    adduser --system --ingroup flaskgroup --uid 977 --no-create-home flaskuser

ENV HAYSTACK_TELEMETRY_ENABLED="False"
ENV HUGGINGFACE_HUB_CACHE="/app/.cache/huggingface/hub"
RUN mkdir -p /app/embedding_cache
RUN mkdir -p /app/.cache/huggingface/hub
RUN chown -R flaskuser:flaskgroup /app

USER 977

CMD flask run --host 0.0.0.0 --port 8081 --debug
