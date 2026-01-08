"""
Project Synapse - Cross-Silo Enterprise Knowledge Fabric

A privacy-preserving, federated knowledge fabric that connects information 
across organizational boundaries without violating access controls.
"""

__version__ = "0.1.0"
__author__ = "Synapse Team"

# Import models first (no external dependencies)
from .models import UserContext, KnowledgeResult, SiloMetadata

# Try to import core components (may fail if dependencies not installed)
try:
    from .core import FederatedIndexer, PrivacyAwareQueryEngine, KnowledgeSynthesizer
    from .security import PermissionEngine, DifferentialPrivacyManager
    
    __all__ = [
        "FederatedIndexer",
        "PrivacyAwareQueryEngine", 
        "KnowledgeSynthesizer",
        "PermissionEngine",
        "DifferentialPrivacyManager",
        "UserContext",
        "KnowledgeResult",
        "SiloMetadata",
    ]
except ImportError as e:
    # Core components not available, only export models
    __all__ = [
        "UserContext",
        "KnowledgeResult", 
        "SiloMetadata",
    ]