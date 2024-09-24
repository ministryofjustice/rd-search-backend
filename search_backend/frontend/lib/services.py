import logging
import os
import sys

from search_backend.frontend.lib.apiclient import ApiClient

# logger
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - [%(levelname)s] : %(message)s")
handler.setFormatter(formatter)

SERVICES = {
    "apiclient": ApiClient(os.environ.get("API_URL")),
    "logginghandler": handler,
}
