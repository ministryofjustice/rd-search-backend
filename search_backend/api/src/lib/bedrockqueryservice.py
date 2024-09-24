from typing import Optional

from search_backend.api.src.lib.searchfunctions import query_answer


class BedrockQueryService:

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
        results = query_answer(question, self.pipe)

        print(("+" * 100) + " RESULTS FROM BEDROCK")
        print(results)

        if len(results) == 0:
            return None, None

        return results, None
