"""
Store user/system interaction data, to be saved to storage when interaction ends.
Resets whenever the user POSTs to the index page.

{
   "created_at": timestamp,
   "reference": "string",
   "original_question": "string",
   "suggested_answer": "string",
   "sources": [
      ...
   ],
   "suggested_answer_status": "ACCEPTED" | "NOT_ACCEPTED" | "NOT_FOUND",
   "hr_question": "string",
   "hr_created_at": timestamp,
   "hr_answer": "string"
}

We may add more values to suggested_answer_status enum if we decide to record
incomplete, errored or partial sessions with the user, e.g.

* ERROR
* PENDING (waiting for user to accept/decline)
* IN_PROGRESS (query service is processing the question)
"""
import uuid
from datetime import datetime

from flask import current_app, session

from .services import SERVICES


def start_interaction():
    if session.get("interaction") is None:
        session["interaction"] = {
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reference": str(uuid.uuid4()),
        }
        current_app.logger.debug(f"Starting interaction {session.get('interaction').get('reference')}")


def update_interaction(values: dict) -> bool:
    """
    Set multiple values on the interaction session property.
    Any existing key will be overwritten.
    """
    data = session.get("interaction")
    if data is None:
        current_app.logger.error("ERROR: attempted to update interaction but it does not exist")
        return False

    data.update(values)
    session["interaction"] = data
    current_app.logger.debug(f"Updated interaction {session.get('interaction').get('reference')}")

    return True


def persist_and_clear_interaction():
    session["interaction"] = None

    """
    // currently unusable as writing to dynamodb takes about 30 seconds; just reset the session for now (see above)
    interaction = session.pop("interaction")
    response = SERVICES["apiclient"].post("/interactions", interaction)

    current_app.logger.debug(f"Persisting interaction {interaction.get('reference')}")
    current_app.logger.debug(f"Response from API: {response.content}")
    """
