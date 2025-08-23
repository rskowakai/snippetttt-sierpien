import asyncio
import time
import json
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from functools import lru_cache

import redis
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.core.config import settings, Settings
from app.models import User, Document, Query, QueryType
from app.services.ai_service import AIService
from app.services.vector_service import VectorService, SearchResult
from app.services.query_classifier import QueryClassifier

logger = logging.getLogger(__name__)


@dataclass
class QueryContext:
    document_id: str
    document_type: str
    document_category: str
    legal_area: List[str]
    jurisdiction: str
    user_preferences: Dict[str, Any]

class EnhancedRAGService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.ai_service = AIService(settings)
        self.vector_service = VectorService(settings)
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Could not connect to Redis: {e}")
            self.redis_client = None
        self.query_classifier = QueryClassifier()

    async def process_query(
        self,
        question: str,
        document_id: str,
        user: User,
        db: Session,
        context: Optional[Dict[str, Any]] = None
    ) -> Query:
        """Enhanced query processing with classification, caching, and optimization"""

        start_time = time.time()

        document = await self._get_document_cached(document_id, db)
        if not document or str(document.owner_id) != str(user.id):
            raise ValueError("Document not found or access denied")

        if not document.is_processed:
            raise ValueError("Document is still being processed")

        cache_key = self._generate_cache_key(question, document_id)
        cached_result = await self._get_cached_result(cache_key)
        if cached_result:
            return await self._create_query_from_cache(cached_result, question, user, document, db)

        query_type = await self.query_classifier.classify_query(question)

        query_context = QueryContext(
            document_id=document_id,
            document_type=document.document_type.value,
            document_category=document.document_category or "unknown",
            legal_area=document.legal_area or [],
            jurisdiction=document.jurisdiction or "PL",
            user_preferences=user.notification_preferences or {}
        )

        try:
            search_results = await self._search_with_optimization(
                question, document, query_type, query_context
            )

            answer, confidence = await self._generate_contextual_answer(
                question, search_results, query_context, query_type
            )

            processing_time = time.time() - start_time
            query = Query(
                question=question,
                answer=answer,
                confidence_score=confidence,
                processing_time=processing_time,
                query_type=query_type,
                user_id=user.id,
                document_id=document.id,
                answered_at=func.now()
            )

            db.add(query)
            db.commit()

            await self._cache_result(cache_key, {
                'answer': answer,
                'confidence': confidence,
                'processing_time': processing_time,
                'query_type': query_type.value
            })

            await self._update_usage_stats(user, db)

            return query

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            error_query = Query(
                question=question,
                answer=f"Przepraszam, wystąpił błąd podczas przetwarzania zapytania: {str(e)}",
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                user_id=user.id,
                document_id=document.id,
                has_error=True
            )
            db.add(error_query)
            db.commit()
            raise

    async def _search_with_optimization(
        self,
        question: str,
        document: Document,
        query_type: QueryType,
        context: QueryContext
    ) -> List[SearchResult]:
        """Optimized search with query type specific strategies"""

        if query_type == QueryType.FACTUAL:
            limit = 3
            similarity_threshold = 0.8
        elif query_type == QueryType.INTERPRETIVE:
            limit = 5
            similarity_threshold = 0.7
        else:
            limit = 6
            similarity_threshold = 0.75

        expanded_queries = await self.ai_service.expand_query(question, context)

        all_results = []
        for expanded_query in expanded_queries:
            results = await self.vector_service.search_similar(
                query_text=expanded_query,
                document_id=document.weaviate_id,
                limit=limit,
                similarity_threshold=similarity_threshold
            )
            all_results.extend(results)

        unique_results = self._deduplicate_results(all_results)
        ranked_results = self._rank_results(unique_results, question, query_type)

        return ranked_results[:limit]

    async def _generate_contextual_answer(
        self,
        question: str,
        search_results: List[SearchResult],
        context: QueryContext,
        query_type: QueryType
    ) -> Tuple[str, float]:
        """Generate answer with enhanced context awareness"""

        if not search_results:
            return "Nie znaleziono odpowiedniej informacji w dokumencie.", 0.0

        prompt = self._build_enhanced_prompt(
            question, search_results, context, query_type
        )

        answer = await self.ai_service._generate_with_retry(prompt)

        confidence = self._calculate_enhanced_confidence(
            search_results, answer, query_type
        )

        return answer, confidence

    def _build_enhanced_prompt(
        self,
        question: str,
        search_results: List[SearchResult],
        context: QueryContext,
        query_type: QueryType
    ) -> str:
        context_info = f"KONTEKST DOKUMENTU:\n- Typ: {context.document_type}\n- Kategoria: {context.document_category}"
        relevant_content = ""
        for i, result in enumerate(search_results, 1):
            relevant_content += f"\n[Fragment {i}] (pewność: {result.score:.2f})\n{result.content}\n"

        return f"PYTANIE: {question}\n{context_info}\n{relevant_content}\nODPOWIEDŹ:"

    async def _get_document_cached(self, document_id: str, db: Session) -> Optional[Document]:
        # Simple cache simulation
        return db.query(Document).filter(Document.id == document_id).first()

    def _generate_cache_key(self, question: str, document_id: str) -> str:
        return f"query_cache:{document_id}:{hash(question)}"

    async def _get_cached_result(self, key: str) -> Optional[Dict]:
        if not self.redis_client:
            return None
        try:
            cached = self.redis_client.get(key)
            return json.loads(cached) if cached else None
        except redis.exceptions.RedisError as e:
            logger.error(f"Redis GET failed: {e}")
            return None

    async def _create_query_from_cache(self, cached_result, question, user, document, db) -> Query:
        # This is a simplified version. In a real app, you might not want to create a new DB entry for a cache hit
        # or you might handle it differently.
        logger.info(f"Returning cached result for question: {question}")
        query = Query(
            question=question,
            answer=cached_result['answer'],
            confidence_score=cached_result['confidence'],
            processing_time=cached_result['processing_time'],
            query_type=QueryType(cached_result['query_type']),
            user_id=user.id,
            document_id=document.id,
            answered_at=func.now()
        )
        # Not saving to DB to avoid duplicates for this stub
        return query

    async def _cache_result(self, key: str, result: Dict):
        if not self.redis_client:
            return
        try:
            self.redis_client.set(key, json.dumps(result), ex=self.settings.CACHE_TTL_SECONDS)
        except redis.exceptions.RedisError as e:
            logger.error(f"Redis SET failed: {e}")


    async def _update_usage_stats(self, user: User, db: Session):
        # Placeholder for usage statistics update
        logger.info(f"Updating usage stats for user {user.id}")
        pass

    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        unique_results = {}
        for result in results:
            if result.content not in unique_results:
                unique_results[result.content] = result
        return list(unique_results.values())

    def _rank_results(self, results: List[SearchResult], question: str, query_type: QueryType) -> List[SearchResult]:
        # Simple ranking by score
        return sorted(results, key=lambda r: r.score, reverse=True)

    def _calculate_enhanced_confidence(self, search_results: List[SearchResult], answer: str, query_type: QueryType) -> float:
        if not search_results:
            return 0.0
        avg_score = sum(r.score for r in search_results) / len(search_results)
        return min(avg_score, 0.95) # Cap confidence at 0.95

    async def extract_citations(self, query: Query) -> List[Dict[str, Any]]:
        # Placeholder
        return [{"text": "citation text", "page": 1, "paragraph": 2}]

    async def generate_follow_up_questions(self, question: str, answer: str, document_id: str) -> List[str]:
        return await self.ai_service.generate_follow_up_questions(question, answer, document_id)
