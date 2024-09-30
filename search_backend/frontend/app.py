import os
from pathlib import Path

from flask import Flask, jsonify, request

from search_backend.frontend.lib.routes.all import main
from search_backend.frontend.lib.services import SERVICES

app = Flask("frontend", static_folder=Path(__file__).parent / "static")

# start sessions
app.secret_key = os.environ["FRONTEND_SESSION_KEY"]

# set up our own logging handler
for handler in app.logger.handlers:
    app.logger.removeHandler(handler)
app.logger.addHandler(SERVICES["logginghandler"])

app.register_blueprint(main)


# call with ?full=true to include the API health check in this one
@app.route("/health-check", methods=["GET"])
def health_check():
    result = {"web": "ok"}
    status_code = 200

    if request.args.get("full") is not None:
        try:
            response = SERVICES["apiclient"].get("/health-check", {"full": "true"})
            if response.status_code != 200:
                result["api"] = f"ERROR response from API /health-check: {response.status_code} - {response.json()}"
                status_code = 500
            else:
                result["api"] = "ok"
        except Exception as e:
            result["api"] = str(e)
            status_code = 500

    return jsonify(result), status_code
