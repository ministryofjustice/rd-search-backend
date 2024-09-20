from flask import render_template, request

from ..services import SERVICES
from ..interaction import start_interaction, update_interaction


def index_get():
    return render_template("index.html")


def index_post():
    start_interaction()
    question = request.form.get("question")
    response = SERVICES["apiclient"].get("/query", {"question": question})
    resp_body = response.json()

    template_data = {
        "question": question,
        "question_response": resp_body,
    }

    if resp_body is not None:
        err = resp_body.get("error")
        if err is not None:
            template_data["error"] = err

    template_data["question_has_response"] = 0
    if resp_body is not None:
        template_data["question_has_response"] = 1

    return render_template("index.html", **template_data)
