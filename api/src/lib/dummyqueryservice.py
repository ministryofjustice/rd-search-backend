import json
from pathlib import Path
from typing import Optional


class DummyQueryService:

    def __init__(self, dummy_answers_file_path: Path):
        with open(dummy_answers_file_path, "r") as dummy_answers_file:
            self.dummy_answers = json.loads(dummy_answers_file.read())

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
        question = question.lower()

        selected_answers = []

        for item in self.dummy_answers:
            phrases_list = item["phrases_list"]
            best_score = 0

            for phrases in phrases_list:
                score = 0
                for phrase in phrases:
                    if phrase.lower() in question:
                        score += 1
                if score > best_score:
                    best_score = score

            if best_score > 0:
                selected_answers.append({"answer": "???", "sources": [{"title": item["title"], "url": item["url"]}], "score": best_score})

        selected_answers = sorted(selected_answers, key=lambda x: x["score"], reverse=True)

        if len(selected_answers) == 0:
            return None, None

        return selected_answers[0], None
