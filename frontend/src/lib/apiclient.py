import requests
from requests import Response
from urllib.parse import urljoin


class ApiClient:

    def __init__(self, api_url: str):
        self.api_url = api_url
        self.client = requests.Session()

    def get(self, path: str, params: dict[str, str] = None) -> Response:
        if params is None:
            params = {}

        return requests.get(urljoin(self.api_url, path), params=params)

    def post(self, path: str, data: dict) -> Response:
        return requests.post(urljoin(self.api_url, path), json=data)
