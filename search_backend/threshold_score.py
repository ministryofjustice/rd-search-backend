from haystack import Document, component, default_from_dict, default_to_dict
from typing import List, Dict, Optional, Any


@component
class ThresholdScore:
    """
    A Haystack component to filter results based on a threshold match score.
    """

    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document], score_threshold: float = 0.0):

        if not documents:
            return {"documents": []}

        if score_threshold < 0 or score_threshold > 1:
            raise ValueError(
                f"score_threshold must be a float between 0 and 1 (inclusive), but got {score_threshold}"
            )

        return {
            "documents": [
                doc for doc in documents if doc.score > score_threshold
            ]
        }
