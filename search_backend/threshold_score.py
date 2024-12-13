from haystack import Document, component, default_from_dict, default_to_dict
from typing import List, Dict, Optional, Any


@component
class ThresholdScore:
    """
    A Haystack component to filter results based on a threshold match score.
    """

    def __init__(
        self,
        score_threshold: float = 0.0 
    ):
        
        self.score_threshold = score_threshold


    @component.output_types(documents=List[Document])
    def run(
        self,
        documents: List[Document],
        score_threshold: Optional[float] = None
    ):
        
        if not documents:
            return {"documents": []}
        
        score_threshold = score_threshold or self.score_threshold

        if score_threshold < 0 or score_threshold > 1:
            raise ValueError(f"threshold must be between 0 and 1 (inclusive), but got {score_threshold}")

        return {"documents": [doc for doc in documents if doc.score > score_threshold]}