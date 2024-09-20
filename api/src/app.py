import logging, sys

from flask import Flask, jsonify, request
from opensearchpy.exceptions import OpenSearchException

from lib.services import SERVICES

app = Flask("backend")

# set up our own logging handler
for handler in app.logger.handlers:
    app.logger.removeHandler(handler)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - [%(levelname)s] : %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)


# send question to query service
@app.route("/query", methods=["GET"])
def query():
    question = request.args.get("question")
    answer, err = SERVICES["queryservicefactory"]().ask(question)

    if err is not None:
        return jsonify({"error": err}), 500

    if answer is None:
        return jsonify(None), 404

    return jsonify(answer)


# save session to back-end storage;
# see https://dsdmoj.atlassian.net/wiki/spaces/HRE/pages/5045190805/Data+model for expected POST JSON;
# curl example to test:
# curl -X POST -H "Content-Type:application/json" -d '{"uid":"12345","original_question":"When can I claim maternity allowance?"}' http://0.0.0.0:8081/interactions
@app.route("/interactions", methods=["POST"])
def interactions():
    """
    data = request.get_json()
    reference = data.pop("reference")
    created_at = data.pop("created_at")

    _, err = SERVICES["dynamodbclient"].put(reference, created_at, data)

    if err is not None:
        return jsonify({"saved": False, "error": err}), 500

    return jsonify({"saved": True, "reference": reference}), 200
    """
    return "SAVING INTERACTIONS IS NOT IMPLEMENTED"


@app.route("/interactions/<reference>", methods=["GET"])
def get_interaction(reference):
    """
    response, err = SERVICES["dynamodbclient"].get(reference)

    if err is not None:
        return jsonify({"error": err}), 500

    return jsonify(response), 200
    """
    return "SAVING INTERACTIONS IS NOT IMPLEMENTED"


# call with ?full=true to include S3 connectivity check
@app.route("/health-check", methods=["GET"])
def health_check():
    result = {"web": "ok"}
    status_code = 200

    if request.args.get("full") is not None:
        _, err = SERVICES["s3clientfactory"]().list()
        if err is not None:
            result["s3_connectivity"] = err
            status_code = 500
        else:
            result["s3_connectivity"] = "ok"

        try:
            SERVICES["opensearchclientfactory"]().info()
            result["opensearch_connectivity"] = "ok"
        except OpenSearchException as e:
            result["opensearch_connectivity"] = repr(e)

    return jsonify(result), status_code
