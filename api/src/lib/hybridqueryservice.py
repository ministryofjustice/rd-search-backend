from typing import Optional

from .searchfunctions import formatted_search_results


class HybridQueryService:

    def __init__(self, pipeline):
        self.pipe = pipeline

    def ask(self, question: str) -> tuple[Optional[dict], Optional[str]]:
        """

        :param question: user's question
        :return: <best answer or None>, <error or None>

        best answer has this structure:
        {
          "answer": "<text of answer>",
          "sources": [
            {"title": "<title of source>", "url": "<url of source>"},
            ...
          ]
        }
        """
        results = formatted_search_results(question, self.pipe, top_k=5)

        print("+" * 100)
        print(results)

        if len(results) == 0:
            return None, None

        return results, None
