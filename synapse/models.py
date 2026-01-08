"""
Core data models for Project Synapse
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import uuid


class AccessLevel(str, Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class SiloType(str, Enum):
    """Types of organizational silos"""
    CODE_REPOSITORY = "code_repository"
    DOCUMENTATION = "documentation"
    KNOWLEDGE_BASE = "knowledge_base"
    CHAT_HISTORY = "chat_history"
    ISSUE_TRACKER = "issue_tracker"


class UserContext(BaseModel):
    """User context for permission-aware queries"""
    user_id: str
    organization_id: str
    team_ids: List[str]
    access_levels: List[AccessLevel]
    security_clearance: Optional[str] = None
    temporal_constraints: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True


class SiloMetadata(BaseModel):
    """Metadata about an organizational silo"""
    silo_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    silo_type: SiloType
    organization_id: str
    team_id: str
    access_rules: Dict[str, Any]
    data_classification: AccessLevel
    last_indexed: Optional[datetime] = None
    embedding_dimension: int = 768
    document_count: int = 0
    
    class Config:
        use_enum_values = True


class KnowledgeResult(BaseModel):
    """Result from federated knowledge search"""
    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    silo_id: str
    content: str
    metadata: Dict[str, Any]
    relevance_score: float
    privacy_score: float  # How much privacy budget was used
    source_attribution: Dict[str, str]
    access_level: AccessLevel
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True


class QueryRequest(BaseModel):
    """Federated query request"""
    query: str
    user_context: UserContext
    max_results: int = 10
    privacy_budget: float = 0.1
    include_silos: Optional[List[str]] = None
    exclude_silos: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None


class SynthesisOutput(BaseModel):
    """Output from knowledge synthesis"""
    synthesis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query: str
    synthesized_answer: str
    source_results: List[KnowledgeResult]
    confidence_score: float
    privacy_preserving: bool
    limitations: List[str]  # What couldn't be accessed due to permissions
    created_at: datetime = Field(default_factory=datetime.utcnow)


class IndexingJob(BaseModel):
    """Background indexing job status"""
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    silo_id: str
    status: str  # pending, running, completed, failed
    progress: float = 0.0
    documents_processed: int = 0
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None