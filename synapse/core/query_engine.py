"""
Privacy-Aware Query Engine - Federated Query Routing Layer
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import numpy as np
from sentence_transformers import SentenceTransformer

from ..models import UserContext, KnowledgeResult, QueryRequest, AccessLevel
from ..security import PermissionEngine, DifferentialPrivacyManager
from .indexer import FederatedIndexer

logger = logging.getLogger(__name__)


class PrivacyAwareQueryEngine:
    """
    Routes queries across organizational silos while preserving privacy
    and respecting access controls.
    """
    
    def __init__(self, 
                 federated_indexer: FederatedIndexer,
                 embedding_model: str = "all-MiniLM-L6-v2"):
        self.federated_indexer = federated_indexer
        self.embedding_model = SentenceTransformer(embedding_model)
        self.permission_engine = PermissionEngine()
        self.privacy_manager = DifferentialPrivacyManager()
        
    async def route_query(self, query_request: QueryRequest) -> List[KnowledgeResult]:
        """
        Route a query across silos with privacy preservation.
        
        Steps:
        1. Find candidate silos that might have relevant information
        2. Filter by user permissions and data classifications  
        3. Execute federated search with differential privacy
        4. Rank and return results
        """
        logger.info(f"Routing query: {query_request.query[:50]}...")
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query_request.query])[0]
        
        # Step 1: Find candidate silos
        candidate_silos = self.federated_indexer.find_candidate_silos(
            query_embedding, query_request.user_context
        )
        
        # Step 2: Filter by permissions
        accessible_silos = await self._filter_accessible_silos(
            candidate_silos, query_request.user_context
        )
        
        # Step 3: Execute federated search
        all_results = []
        privacy_budget_per_silo = query_request.privacy_budget / max(len(accessible_silos), 1)
        
        search_tasks = [
            self._execute_silo_search(
                silo_id, 
                query_embedding, 
                query_request.user_context,
                privacy_budget_per_silo,
                query_request.max_results
            )
            for silo_id in accessible_silos
        ]
        
        silo_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        for results in silo_results:
            if not isinstance(results, Exception):
                all_results.extend(results)
                
        # Step 4: Rank results globally
        ranked_results = self._rank_results(all_results, query_request.query)
        
        # Limit to max_results
        final_results = ranked_results[:query_request.max_results]
        
        logger.info(f"Query completed: {len(final_results)} results from {len(accessible_silos)} silos")
        return final_results
        
    async def _filter_accessible_silos(self, candidate_silos: List[str], 
                                     user_context: UserContext) -> List[str]:
        """Filter silos by user permissions and data classification"""
        accessible_silos = []
        
        for silo_id in candidate_silos:
            if silo_id in self.federated_indexer.silo_indexes:
                silo_metadata = self.federated_indexer.silo_indexes[silo_id]["metadata"]
                
                # Check access permissions
                if self.permission_engine.check_silo_access(silo_metadata, user_context):
                    # Check data classification level
                    if self._check_data_classification_access(
                        silo_metadata.data_classification, user_context
                    ):
                        accessible_silos.append(silo_id)
                        
        return accessible_silos
        
    def _check_data_classification_access(self, data_level: AccessLevel, 
                                        user_context: UserContext) -> bool:
        """Check if user can access data at this classification level"""
        user_levels = user_context.access_levels
        
        # Define access hierarchy
        level_hierarchy = {
            AccessLevel.PUBLIC: 0,
            AccessLevel.INTERNAL: 1, 
            AccessLevel.CONFIDENTIAL: 2,
            AccessLevel.RESTRICTED: 3
        }
        
        required_level = level_hierarchy.get(data_level, 3)
        user_max_level = max(level_hierarchy.get(level, 0) for level in user_levels)
        
        return user_max_level >= required_level
        
    async def _execute_silo_search(self, silo_id: str, 
                                 query_embedding: np.ndarray,
                                 user_context: UserContext,
                                 privacy_budget: float,
                                 max_results: int) -> List[KnowledgeResult]:
        """Execute search within a single silo with privacy preservation"""
        try:
            silo_data = self.federated_indexer.silo_indexes[silo_id]
            silo_index = silo_data["index"]
            silo_metadata = silo_data["metadata"]
            
            # Perform similarity search
            query_embedding = query_embedding.reshape(1, -1)
            scores, indices = silo_index.search(query_embedding, k=max_results * 2)
            
            # Convert to KnowledgeResult objects
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx == -1:  # FAISS returns -1 for empty results
                    continue
                    
                # Apply differential privacy to score
                private_score = self.privacy_manager.add_noise_to_score(
                    float(score), privacy_budget / max_results
                )
                
                # Mock document retrieval (in real implementation, fetch actual content)
                content = await self._retrieve_document_content(silo_id, idx, user_context)
                
                if content:  # Only include if user has access to content
                    result = KnowledgeResult(
                        silo_id=silo_id,
                        content=content,
                        metadata={
                            "silo_name": silo_metadata.name,
                            "silo_type": silo_metadata.silo_type,
                            "document_index": int(idx)
                        },
                        relevance_score=private_score,
                        privacy_score=privacy_budget / max_results,
                        source_attribution={
                            "silo": silo_metadata.name,
                            "team": silo_metadata.team_id,
                            "organization": silo_metadata.organization_id
                        },
                        access_level=silo_metadata.data_classification
                    )
                    results.append(result)
                    
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching silo {silo_id}: {e}")
            return []
            
    async def _retrieve_document_content(self, silo_id: str, doc_index: int, 
                                       user_context: UserContext) -> Optional[str]:
        """Retrieve actual document content with permission checks"""
        # Mock implementation - in reality, this would:
        # 1. Fetch the actual document from the silo's data source
        # 2. Apply fine-grained permission checks
        # 3. Redact sensitive information if needed
        
        silo_data = self.federated_indexer.silo_indexes[silo_id]
        silo_metadata = silo_data["metadata"]
        
        # Check if user can access this specific document
        if not self.permission_engine.check_document_access(
            silo_metadata, doc_index, user_context
        ):
            return None
            
        # Mock content - replace with actual document retrieval
        return f"Document {doc_index} content from {silo_metadata.name}. " \
               f"This contains relevant information for the user's query."
               
    def _rank_results(self, results: List[KnowledgeResult], 
                     query: str) -> List[KnowledgeResult]:
        """Rank results globally across all silos"""
        # Combine relevance score with privacy cost and recency
        def ranking_score(result: KnowledgeResult) -> float:
            relevance_weight = 0.7
            privacy_weight = 0.2  # Lower privacy cost = higher score
            diversity_weight = 0.1
            
            privacy_penalty = result.privacy_score * privacy_weight
            diversity_bonus = self._calculate_diversity_bonus(result, results) * diversity_weight
            
            return (result.relevance_score * relevance_weight) - privacy_penalty + diversity_bonus
            
        # Sort by ranking score
        ranked_results = sorted(results, key=ranking_score, reverse=True)
        
        return ranked_results
        
    def _calculate_diversity_bonus(self, result: KnowledgeResult, 
                                 all_results: List[KnowledgeResult]) -> float:
        """Calculate diversity bonus to promote results from different silos"""
        same_silo_count = sum(1 for r in all_results if r.silo_id == result.silo_id)
        total_results = len(all_results)
        
        # Bonus for results from less-represented silos
        if total_results > 0:
            return 1.0 - (same_silo_count / total_results)
        return 0.0
        
    async def get_query_suggestions(self, partial_query: str, 
                                  user_context: UserContext) -> List[str]:
        """Get query suggestions based on accessible content"""
        # Mock implementation - in reality, this would:
        # 1. Analyze query patterns from accessible silos
        # 2. Use NLP to suggest completions
        # 3. Respect privacy constraints
        
        suggestions = [
            f"{partial_query} best practices",
            f"{partial_query} implementation guide", 
            f"{partial_query} troubleshooting",
            f"{partial_query} architecture patterns",
            f"{partial_query} security considerations"
        ]
        
        return suggestions[:3]  # Return top 3 suggestions