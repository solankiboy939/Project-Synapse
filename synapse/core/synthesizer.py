"""
Knowledge Synthesizer - Cross-Domain Knowledge Synthesis Layer
"""

import logging
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime

from ..models import KnowledgeResult, SynthesisOutput, UserContext
from ..security import PermissionEngine

logger = logging.getLogger(__name__)


class KnowledgeSynthesizer:
    """
    Synthesizes knowledge from multiple silos while maintaining
    attribution and privacy constraints.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        self.llm_client = llm_client or MockLLMClient()
        self.permission_engine = PermissionEngine()
        
    async def synthesize_answers(self, query: str, 
                               federated_results: List[KnowledgeResult],
                               user_context: UserContext) -> SynthesisOutput:
        """
        Synthesize answers from federated results while preserving
        source attribution and privacy constraints.
        """
        logger.info(f"Synthesizing answer from {len(federated_results)} results")
        
        # Filter results by final permission check
        accessible_results = await self._final_permission_filter(
            federated_results, user_context
        )
        
        # Group results by source for better attribution
        grouped_results = self._group_results_by_source(accessible_results)
        
        # Generate synthesis prompt
        synthesis_prompt = self._create_synthesis_prompt(
            query, grouped_results, user_context
        )
        
        # Call LLM for synthesis
        synthesized_answer = await self.llm_client.synthesize(synthesis_prompt)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            accessible_results, synthesized_answer
        )
        
        # Identify limitations due to access restrictions
        limitations = self._identify_limitations(
            federated_results, accessible_results, user_context
        )
        
        synthesis_output = SynthesisOutput(
            query=query,
            synthesized_answer=synthesized_answer,
            source_results=accessible_results,
            confidence_score=confidence_score,
            privacy_preserving=True,
            limitations=limitations
        )
        
        logger.info(f"Synthesis completed with confidence: {confidence_score:.2f}")
        return synthesis_output
        
    async def _final_permission_filter(self, results: List[KnowledgeResult],
                                     user_context: UserContext) -> List[KnowledgeResult]:
        """Final permission check before synthesis"""
        accessible_results = []
        
        for result in results:
            # Double-check permissions at synthesis time
            if await self.permission_engine.check_synthesis_access(result, user_context):
                accessible_results.append(result)
            else:
                logger.debug(f"Filtered result from {result.silo_id} due to permissions")
                
        return accessible_results
        
    def _group_results_by_source(self, results: List[KnowledgeResult]) -> Dict[str, List[KnowledgeResult]]:
        """Group results by source silo for better attribution"""
        grouped = {}
        
        for result in results:
            silo_name = result.source_attribution.get("silo", result.silo_id)
            if silo_name not in grouped:
                grouped[silo_name] = []
            grouped[silo_name].append(result)
            
        return grouped
        
    def _create_synthesis_prompt(self, query: str, 
                               grouped_results: Dict[str, List[KnowledgeResult]],
                               user_context: UserContext) -> str:
        """Create synthesis prompt for LLM"""
        
        # Format results by source
        formatted_sources = []
        for silo_name, results in grouped_results.items():
            source_content = f"\n**Source: {silo_name}**\n"
            for i, result in enumerate(results, 1):
                source_content += f"{i}. {result.content}\n"
                source_content += f"   (Relevance: {result.relevance_score:.2f})\n"
            formatted_sources.append(source_content)
            
        sources_text = "\n".join(formatted_sources)
        
        synthesis_prompt = f"""You are an expert at synthesizing information from different organizational teams and systems.

QUERY: {query}

AVAILABLE INFORMATION:
{sources_text}

USER CONTEXT:
- Organization: {user_context.organization_id}
- Teams: {', '.join(user_context.team_ids)}
- Access Level: {', '.join(user_context.access_levels)}

SYNTHESIS REQUIREMENTS:
1. Provide a comprehensive answer that connects insights across different sources
2. Maintain clear attribution to each source (use format: [Source: silo_name])
3. Only use information the user is authorized to see
4. If information seems incomplete due to access restrictions, note this limitation
5. Highlight patterns or connections that span multiple teams/systems
6. Be specific about which team or system provided each insight

CONSTRAINTS:
- Do not infer or speculate beyond the provided information
- Preserve technical accuracy from each source
- Note any conflicting information between sources
- Keep the response focused and actionable

Please provide a synthesized answer that helps the user understand the complete picture across their organization."""

        return synthesis_prompt
        
    def _calculate_confidence_score(self, results: List[KnowledgeResult], 
                                  synthesized_answer: str) -> float:
        """Calculate confidence score for the synthesis"""
        if not results:
            return 0.0
            
        # Factors affecting confidence:
        # 1. Number of sources
        # 2. Average relevance score
        # 3. Source diversity (different silos)
        # 4. Answer completeness
        
        num_sources = len(results)
        avg_relevance = sum(r.relevance_score for r in results) / num_sources
        unique_silos = len(set(r.silo_id for r in results))
        
        # Source diversity bonus
        diversity_factor = min(unique_silos / 3.0, 1.0)  # Cap at 3 silos
        
        # Answer completeness (mock - in reality, analyze answer quality)
        completeness_factor = min(len(synthesized_answer) / 500.0, 1.0)
        
        # Combine factors
        confidence = (
            (avg_relevance * 0.4) +
            (diversity_factor * 0.3) + 
            (completeness_factor * 0.2) +
            (min(num_sources / 5.0, 1.0) * 0.1)  # Number of sources bonus
        )
        
        return min(confidence, 1.0)
        
    def _identify_limitations(self, all_results: List[KnowledgeResult],
                            accessible_results: List[KnowledgeResult],
                            user_context: UserContext) -> List[str]:
        """Identify what information couldn't be accessed due to permissions"""
        limitations = []
        
        # Check for filtered results
        filtered_count = len(all_results) - len(accessible_results)
        if filtered_count > 0:
            limitations.append(
                f"{filtered_count} additional results were filtered due to access permissions"
            )
            
        # Check for missing high-level access
        restricted_silos = set()
        for result in all_results:
            if result not in accessible_results:
                silo_name = result.source_attribution.get("silo", "Unknown")
                restricted_silos.add(silo_name)
                
        if restricted_silos:
            limitations.append(
                f"Information from the following sources was restricted: {', '.join(restricted_silos)}"
            )
            
        # Check access level limitations
        user_max_access = max(user_context.access_levels) if user_context.access_levels else "public"
        if user_max_access != "restricted":
            limitations.append(
                f"Some highly classified information may not be included (user access level: {user_max_access})"
            )
            
        return limitations
        
    async def generate_follow_up_questions(self, synthesis: SynthesisOutput,
                                         user_context: UserContext) -> List[str]:
        """Generate relevant follow-up questions based on the synthesis"""
        
        # Analyze the synthesis to suggest deeper exploration
        follow_ups = []
        
        # Questions based on source diversity
        unique_silos = set(r.silo_id for r in synthesis.source_results)
        if len(unique_silos) > 1:
            follow_ups.append(
                "How do the approaches differ between teams, and what are the trade-offs?"
            )
            
        # Questions based on limitations
        if synthesis.limitations:
            follow_ups.append(
                "What additional information might be available with higher access permissions?"
            )
            
        # Domain-specific follow-ups based on content
        if "implementation" in synthesis.query.lower():
            follow_ups.extend([
                "What are the common pitfalls and how to avoid them?",
                "Are there any recent updates or changes to these approaches?"
            ])
            
        if "architecture" in synthesis.query.lower():
            follow_ups.extend([
                "How does this scale in production environments?",
                "What monitoring and observability practices are recommended?"
            ])
            
        return follow_ups[:3]  # Return top 3 follow-ups


class MockLLMClient:
    """Mock LLM client for development/testing"""
    
    async def synthesize(self, prompt: str) -> str:
        """Mock synthesis - replace with actual LLM integration"""
        
        # Extract query and sources from prompt
        lines = prompt.split('\n')
        query_line = next((line for line in lines if line.startswith('QUERY:')), '')
        query = query_line.replace('QUERY:', '').strip()
        
        # Mock synthesis based on query keywords
        if "implementation" in query.lower():
            return f"""Based on the available sources, here's a comprehensive approach to {query}:

[Source: Engineering Team] The recommended implementation follows a modular architecture pattern with clear separation of concerns.

[Source: Documentation] Key considerations include error handling, logging, and performance monitoring.

[Source: DevOps Team] Deployment should use containerization with proper health checks and rollback capabilities.

The synthesis shows consistency across teams regarding best practices, with each team contributing specialized knowledge in their domain."""

        elif "troubleshooting" in query.lower():
            return f"""For troubleshooting {query}, the cross-team knowledge reveals:

[Source: Support Team] Common issues include configuration mismatches and network connectivity problems.

[Source: Engineering Team] Debug logging and metrics collection are essential for root cause analysis.

[Source: Infrastructure Team] Resource constraints and scaling issues are frequent causes of problems.

The pattern across teams emphasizes systematic diagnosis and comprehensive monitoring."""

        else:
            return f"""Regarding {query}, the federated knowledge synthesis reveals:

Multiple teams have addressed similar challenges with consistent approaches. The key insights span implementation details, operational considerations, and best practices.

[Source: Multiple Teams] Common themes include scalability, security, and maintainability as primary concerns.

This synthesis provides a comprehensive view while respecting organizational boundaries and access controls."""