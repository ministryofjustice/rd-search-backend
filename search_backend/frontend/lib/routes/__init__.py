from flask import Blueprint

from search_backend.frontend.lib.routes.index import index_get, index_post
from search_backend.frontend.lib.routes.feedback import feedback_get, feedback_post

main = Blueprint("mainroutes", __name__, template_folder="templates")

main.add_url_rule("/", methods=["GET"], view_func=index_get)
main.add_url_rule("/", methods=["POST"], view_func=index_post)

main.add_url_rule("/feedback", methods=["GET"], view_func=feedback_get)
main.add_url_rule("/feedback", methods=["POST"], view_func=feedback_post)
