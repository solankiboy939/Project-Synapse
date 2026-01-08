"""
Tests for core Synapse functionality
"""

import pytest
import numpy as np
from unittest.mock import Mock, AsyncMock

from synapse.core import FederatedIndexer, PrivacyAwareQueryEngine, KnowledgeSynthesizer
from synapse.security import DifferentialPrivacyManager, PermissionEngine
from synapse.models import (
    SiloMetadata, UserContext, QueryRequest, KnowledgeResult,
    AccessLevel, SiloType
)


@pytest.fixture
def sample_silo():
    """Create a sample silo for testing"""
    return SiloMetadata(
        silo_id="test_silo",
        name="Test Silo",
        silo_type=SiloType.DOCUMENTATION,
        organization_id="test_org",
        team_id="test_team",
        access_rules={"public_within_org": True},
        data_classification=AccessLevel.INTERNAL
    )


@pytest.fixture
def sample_user():
    """Create a sample user context for testing"""
    return UserContext(
        user_id="test_user",
        organization_id="test_org",
        team_ids=["test_team"],
        access_levels=[AccessLevel.INTERNAL]
    )


@pytest.fixture
def privacy_manager():
    """Create privacy manager for testing"""
    return DifferentialPrivacyManager(global_privacy_budget=5.0)


class TestFederatedIndexer:
    """Test the FederatedIndexer class"""
    
    @pytest.mark.asyncio
    async def test_build_global_index(self, sample_silo, privacy_manager):
        """Test building global index"""
        indexer = FederatedIndexer(privacy_manager=privacy_manager)
        
        # Mock document retrieval
        indexer._retrieve_silo_documents = AsyncMock(return_value=[
            {"id": "doc1", "content": "test content 1", "metadata": {}},
            {"id": "doc2", "content": "test content 2", "metadata": {}}
        ])
        
        global_index = await indexer.build_global_index([sample_silo])
        
        assert global_index["total_silos"] == 1
        assert global_index["indexed_silos"] == 1
        assert sample_silo.silo_id in indexer.silo_indexes
        
    def test_generate_permission_aware_hashes(self, privacy_manager):
        """Test secure hash generation"""
        indexer = FederatedIndexer(privacy_manager=privacy_manager)
        
        embeddings = np.random.rand(3, 768)
        access_rules = {"public_within_org": True}
        
        hashes = indexer._generate_permission_aware_hashes(embeddings, access_rules)
        
        assert len(hashes) == 3
        assert all(isinstance(h, str) for h in hashes)
        assert all(len(h) == 64 for h in hashes)  # SHA-256 hex length
        
    def test_find_candidate_silos(self, sample_silo, sample_user, privacy_manager):
        """Test finding candidate silos for query"""
        indexer = FederatedIndexer(privacy_manager=privacy_manager)
        
        # Mock silo index
        mock_index = Mock()
        mock_index.search.return_value = (np.array([[0.8]]), np.array([[0]]))
        
        indexer.silo_indexes[sample_silo.silo_id] = {
            "index": mock_index,
            "metadata": sample_silo
        }
        
        query_embedding = np.random.rand(768)
        candidates = indexer.find_candidate_silos(query_embedding, sample_user)
        
        assert sample_silo.silo_id in candidates


class TestPrivacyAwareQueryEngine:
    """Test the PrivacyAwareQueryEngine class"""
    
    @pytest.mark.asyncio
    async def test_route_query(self, sample_silo, sample_user, privacy_manager):
        """Test query routing"""
        indexer = FederatedIndexer(privacy_manager=privacy_manager)
        query_engine = PrivacyAwareQueryEngine(indexer)
        
        # Mock indexer methods
        indexer.find_candidate_silos = Mock(return_value=[sample_silo.silo_id])
        query_engine._execute_silo_search = AsyncMock(return_value=[
            KnowledgeResult(
                silo_id=sample_silo.silo_id,
                content="test result",
                metadata={},
                relevance_score=0.8,
                privacy_score=0.1,
                source_attribution={"silo": "Test Silo"},
                access_level=AccessLevel.INTERNAL
            )
        ])
        
        query_request = QueryRequest(
            query="test query",
            user_context=sample_user,
            max_results=5,
            privacy_budget=0.2
        )
        
        results = await query_engine.route_query(query_request)
        
        assert len(results) == 1
        assert results[0].silo_id == sample_silo.silo_id
        
    def test_check_data_classification_access(self, sample_user):
        """Test data classification access checking"""
        indexer = Mock()
        query_engine = PrivacyAwareQueryEngine(indexer)
        
        # User has INTERNAL access, should access INTERNAL data
        assert query_engine._check_data_classification_access(
            AccessLevel.INTERNAL, sample_user
        )
        
        # User doesn't have CONFIDENTIAL access
        assert not query_engine._check_data_classification_access(
            AccessLevel.CONFIDENTIAL, sample_user
        )


class TestKnowledgeSynthesizer:
    """Test the KnowledgeSynthesizer class"""
    
    @pytest.mark.asyncio
    async def test_synthesize_answers(self, sample_user):
        """Test knowledge synthesis"""
        synthesizer = KnowledgeSynthesizer()
        
        # Mock LLM client
        synthesizer.llm_client = Mock()
        synthesizer.llm_client.synthesize = AsyncMock(return_value="Synthesized answer")
        
        results = [
            KnowledgeResult(
                silo_id="silo1",
                content="Content from silo 1",
                metadata={},
                relevance_score=0.9,
                privacy_score=0.1,
                source_attribution={"silo": "Silo 1"},
                access_level=AccessLevel.INTERNAL
            ),
            KnowledgeResult(
                silo_id="silo2", 
                content="Content from silo 2",
                metadata={},
                relevance_score=0.8,
                privacy_score=0.1,
                source_attribution={"silo": "Silo 2"},
                access_level=AccessLevel.INTERNAL
            )
        ]
        
        synthesis = await synthesizer.synthesize_answers(
            "test query", results, sample_user
        )
        
        assert synthesis.query == "test query"
        assert synthesis.synthesized_answer == "Synthesized answer"
        assert len(synthesis.source_results) == 2
        assert synthesis.confidence_score > 0
        
    def test_calculate_confidence_score(self):
        """Test confidence score calculation"""
        synthesizer = KnowledgeSynthesizer()
        
        results = [
            KnowledgeResult(
                silo_id="silo1",
                content="test",
                metadata={},
                relevance_score=0.9,
                privacy_score=0.1,
                source_attribution={"silo": "Silo 1"},
                access_level=AccessLevel.INTERNAL
            )
        ]
        
        confidence = synthesizer._calculate_confidence_score(results, "test answer")
        
        assert 0 <= confidence <= 1
        
    def test_group_results_by_source(self):
        """Test grouping results by source"""
        synthesizer = KnowledgeSynthesizer()
        
        results = [
            KnowledgeResult(
                silo_id="silo1",
                content="content1",
                metadata={},
                relevance_score=0.9,
                privacy_score=0.1,
                source_attribution={"silo": "Silo A"},
                access_level=AccessLevel.INTERNAL
            ),
            KnowledgeResult(
                silo_id="silo2",
                content="content2", 
                metadata={},
                relevance_score=0.8,
                privacy_score=0.1,
                source_attribution={"silo": "Silo A"},
                access_level=AccessLevel.INTERNAL
            ),
            KnowledgeResult(
                silo_id="silo3",
                content="content3",
                metadata={},
                relevance_score=0.7,
                privacy_score=0.1,
                source_attribution={"silo": "Silo B"},
                access_level=AccessLevel.INTERNAL
            )
        ]
        
        grouped = synthesizer._group_results_by_source(results)
        
        assert len(grouped) == 2
        assert "Silo A" in grouped
        assert "Silo B" in grouped
        assert len(grouped["Silo A"]) == 2
        assert len(grouped["Silo B"]) == 1


class TestDifferentialPrivacyManager:
    """Test the DifferentialPrivacyManager class"""
    
    def test_add_noise_to_embeddings(self):
        """Test adding noise to embeddings"""
        privacy_manager = DifferentialPrivacyManager(global_privacy_budget=5.0)
        
        embeddings = np.random.rand(10, 768)
        original_embeddings = embeddings.copy()
        
        noisy_embeddings = privacy_manager.add_noise_to_embeddings(
            embeddings, privacy_budget=0.5, sensitivity=1.0
        )
        
        # Check that noise was added
        assert not np.array_equal(original_embeddings, noisy_embeddings)
        assert noisy_embeddings.shape == original_embeddings.shape
        
        # Check privacy budget was consumed
        assert privacy_manager.used_privacy_budget == 0.5
        
    def test_add_noise_to_score(self):
        """Test adding noise to similarity scores"""
        privacy_manager = DifferentialPrivacyManager(global_privacy_budget=5.0)
        
        original_score = 0.8
        noisy_score = privacy_manager.add_noise_to_score(original_score, 0.1)
        
        # Score should be in valid range
        assert 0.0 <= noisy_score <= 1.0
        
        # Privacy budget should be consumed
        assert privacy_manager.used_privacy_budget == 0.1
        
    def test_privacy_budget_management(self):
        """Test privacy budget management"""
        privacy_manager = DifferentialPrivacyManager(global_privacy_budget=1.0)
        
        # Should allow operation within budget
        assert privacy_manager._check_privacy_budget(0.5)
        
        # Consume budget
        privacy_manager._consume_privacy_budget(0.8)
        
        # Should not allow operation exceeding budget
        assert not privacy_manager._check_privacy_budget(0.5)
        
        # Check remaining budget
        assert privacy_manager.get_remaining_budget() == 0.2
        
    def test_create_private_histogram(self):
        """Test creating private histogram"""
        privacy_manager = DifferentialPrivacyManager(global_privacy_budget=5.0)
        
        data = ["A", "B", "A", "C", "B", "A"]
        histogram = privacy_manager.create_private_histogram(data, bins=3, privacy_budget=0.5)
        
        assert isinstance(histogram, dict)
        assert "A" in histogram
        assert "B" in histogram
        assert "C" in histogram
        
        # Counts should be non-negative integers
        assert all(isinstance(count, int) and count >= 0 for count in histogram.values())
        
    def test_anonymize_text(self):
        """Test text anonymization"""
        privacy_manager = DifferentialPrivacyManager()
        
        text = "Contact John Doe at john.doe@example.com or call 555-123-4567"
        anonymized = privacy_manager.anonymize_text(text, privacy_level="medium")
        
        # Should remove email and phone
        assert "john.doe@example.com" not in anonymized
        assert "555-123-4567" not in anonymized
        assert "[EMAIL]" in anonymized
        assert "[PHONE]" in anonymized


class TestPermissionEngine:
    """Test the PermissionEngine class"""
    
    def test_check_silo_access_same_org(self, sample_silo, sample_user):
        """Test silo access within same organization"""
        permission_engine = PermissionEngine()
        
        # Same org and team - should allow
        assert permission_engine.check_silo_access(sample_silo, sample_user)
        
    def test_check_silo_access_different_org(self, sample_silo, sample_user):
        """Test silo access across organizations"""
        permission_engine = PermissionEngine()
        
        # Different organization - should deny
        sample_user.organization_id = "different_org"
        assert not permission_engine.check_silo_access(sample_silo, sample_user)
        
    def test_check_classification_access(self, sample_silo, sample_user):
        """Test data classification access"""
        permission_engine = PermissionEngine()
        
        # User has INTERNAL access, silo is INTERNAL - should allow
        assert permission_engine._check_classification_access(sample_silo, sample_user)
        
        # Silo is CONFIDENTIAL, user only has INTERNAL - should deny
        sample_silo.data_classification = AccessLevel.CONFIDENTIAL
        assert not permission_engine._check_classification_access(sample_silo, sample_user)
        
    def test_check_team_access(self, sample_silo, sample_user):
        """Test team-level access"""
        permission_engine = PermissionEngine()
        
        # Same team - should allow
        assert permission_engine._check_team_access(sample_silo, sample_user)
        
        # Different team - should deny unless public
        sample_user.team_ids = ["different_team"]
        assert not permission_engine._check_team_access(sample_silo, sample_user)
        
        # Public within org - should allow
        sample_silo.access_rules["public_within_org"] = True
        assert permission_engine._check_team_access(sample_silo, sample_user)
        
    def test_get_accessible_silos(self, sample_user):
        """Test getting accessible silos for user"""
        permission_engine = PermissionEngine()
        
        silos = [
            SiloMetadata(
                silo_id="accessible",
                name="Accessible Silo",
                silo_type=SiloType.DOCUMENTATION,
                organization_id="test_org",
                team_id="test_team",
                access_rules={"public_within_org": True},
                data_classification=AccessLevel.INTERNAL
            ),
            SiloMetadata(
                silo_id="restricted",
                name="Restricted Silo", 
                silo_type=SiloType.DOCUMENTATION,
                organization_id="different_org",
                team_id="different_team",
                access_rules={},
                data_classification=AccessLevel.RESTRICTED
            )
        ]
        
        accessible = permission_engine.get_accessible_silos(sample_user, silos)
        
        assert len(accessible) == 1
        assert accessible[0].silo_id == "accessible"