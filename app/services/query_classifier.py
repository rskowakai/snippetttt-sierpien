import logging
from app.models.enums import QueryType

logger = logging.getLogger(__name__)

class QueryClassifier:
    def __init__(self):
        logger.info("Initializing QueryClassifier stub")

    async def classify_query(self, question: str) -> QueryType:
        """
        Classifies the query into one of the predefined types.
        This is a simple stub implementation. A real implementation would
        use a machine learning model or a more sophisticated rule-based system.
        """
        question_lower = question.lower()
        if "what is" in question_lower or "who is" in question_lower or "when was" in question_lower:
            return QueryType.FACTUAL
        elif "compare" in question_lower or "difference between" in question_lower:
            return QueryType.COMPARATIVE
        elif "how to" in question_lower or "what are the steps" in question_lower:
            return QueryType.PROCEDURAL
        elif "what is the meaning of" in question_lower or "interpret" in question_lower:
            return QueryType.INTERPRETIVE
        else:
            return QueryType.FACTUAL # Default
