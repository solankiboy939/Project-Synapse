"""
Core components of Project Synapse
"""

from .indexer import FederatedIndexer
from .query_engine import PrivacyAwareQueryEngine
from .synthesizer import KnowledgeSynthesizer

__all__ = [
    "FederatedIndexer",
    "PrivacyAwareQueryEngine", 
    "KnowledgeSynthesizer",
]