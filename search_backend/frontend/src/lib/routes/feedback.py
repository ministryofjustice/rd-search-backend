from datetime import datetime

from flask import current_app, render_template, request

from search_backend.frontend.src.lib.interaction import update_interaction, persist_and_clear_interaction


def feedback_get():
    return render_template("feedback.html", step="ask-question")


def feedback_post():
    # has user just pressed the "Yes" or "No" button?
    question_answered = request.form.get("question-answered")
    original_question_asked = request.form.get("original-question-asked")

    step = None
    if question_answered == "Yes":
        update_interaction({"suggested_answer_status": "ACCEPTED"})

        current_app.logger.debug(f"User accepted answer to question")
        step = "question-answered"

        # reached final step in journey
        persist_and_clear_interaction()
    elif question_answered == "No":
        update_interaction({"suggested_answer_status": "NOT_ACCEPTED"})

        current_app.logger.debug(f"User rejected answer to question")
        step = "question-not-answered"
    elif question_answered == "NoAnswerAvailable":
        update_interaction({"suggested_answer_status": "NOT_FOUND"})

        current_app.logger.debug(f"No answers were available for question")
        step = "question-not-answered"

    # user has already pressed "Yes"/"No" and is now supplying their question for submission to capability team
    if step is None:
        question_asked = request.form.get("question-asked")
        if question_asked is not None:
            update_interaction({
                "hr_question": question_asked,
                "hr_created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

            # reached final step in journey
            persist_and_clear_interaction()

            current_app.logger.debug(f"User submitted question to capability team")
            step = "question-submitted"

    template_data = {
        "step": step,
        "original_question_asked": original_question_asked
    }

    return render_template("feedback.html", **template_data)
