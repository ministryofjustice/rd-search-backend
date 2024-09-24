FROM python:3-alpine3.17

WORKDIR /app

RUN apk add curl

HEALTHCHECK --interval=5s --timeout=3s CMD curl -f http://0.0.0.0:8080/health-check || exit 1

COPY setup.py setup.py

RUN pip install --upgrade pip && \
    pip install pip-tools

RUN pip-compile --extra frontend setup.py > requirements.txt && \
    rm setup.py && \
    pip uninstall -y pip-tools

RUN pip install -r requirements.txt && rm requirements.txt

COPY frontend/src/app.py .
COPY frontend/src/lib ./lib
COPY frontend/src/static ./static
COPY frontend/src/templates ./templates

RUN addgroup flaskgroup && adduser -g flaskgroup -u 2107 -D flaskuser && chown -R flaskuser:flaskgroup /app

USER 2107

CMD flask run --host 0.0.0.0 --port 8080 --debug

