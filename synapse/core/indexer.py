"""
Federated Indexer - Secure Cross-Silo Indexing Layer
"""

import asyncio
import hashlib
import logging
from typing import Dict, List, Optional, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

from ..models import SiloMetadata, IndexingJob, AccessLevel
from ..security import DifferentialPrivacyManager, PermissionEngine

logger = logging.getLogger(__name__)


class FederatedIndexer:
    """
    Builds secure, privacy-preserving indexes across organizational silos.
    Each team maintains their own vector embeddings while only sharing
    metadata and permission tokens.
    """
    
    def __init__(self, 
                 embedding_model: str = "all-MiniLM-L6-v2",
                 privacy_manager: Optional[DifferentialPrivacyManager] = None):
        self.embedding_model = SentenceTransformer(embedding_model)
        self.privacy_manager = privacy_manager or DifferentialPrivacyManager()
        self.permission_engine = PermissionEngine()
        
        # Global index stores only metadata and secure hashes
        self.global_index = {}
        self.silo_indexes = {}  # Local FAISS indexes per silo
        
    async def build_global_index(self, silos: List[SiloMetadata]) -> Dict[str, Any]:
        """
        Build the global federated index across all silos.
        Only indexes metadata and permission-aware hashes.
        """
        logger.info(f"Building global index for {len(silos)} silos")
        
        indexing_jobs = []
        for silo in silos:
            job = await self._index_silo(silo)
            indexing_jobs.append(job)
            
        # Wait for all indexing jobs to complete
        completed_jobs = await asyncio.gather(*indexing_jobs, return_exceptions=True)
        
        # Build the global metadata index
        global_metadata = {
            "total_silos": len(silos),
            "indexed_silos": len([j for j in completed_jobs if not isinstance(j, Exception)]),
            "embedding_dimension": self.embedding_model.get_sentence_embedding_dimension(),
            "privacy_budget_used": sum(job.privacy_budget_used for job in completed_jobs 
                                     if hasattr(job, 'privacy_budget_used')),
        }
        
        self.global_index = global_metadata
        logger.info(f"Global index built: {global_metadata}")
        return global_metadata
        
    async def _index_silo(self, silo: SiloMetadata) -> IndexingJob:
        """Index a single silo with privacy preservation"""
        job = IndexingJob(silo_id=silo.silo_id, status="running")
        
        try:
            # Simulate document retrieval from silo
            documents = await self._retrieve_silo_documents(silo)
            
            # Generate embeddings locally within the silo
            embeddings = await self._generate_embeddings(documents, silo)
            
            # Create privacy-preserving secure hashes
            secure_hashes = self._generate_permission_aware_hashes(
                embeddings, silo.access_rules
            )
            
            # Build local FAISS index
            local_index = self._build_faiss_index(embeddings)
            self.silo_indexes[silo.silo_id] = {
                "index": local_index,
                "metadata": silo,
                "secure_hashes": secure_hashes,
                "document_count": len(documents)
            }
            
            job.status = "completed"
            job.documents_processed = len(documents)
            job.progress = 1.0
            
        except Exception as e:
            logger.error(f"Failed to index silo {silo.silo_id}: {e}")
            job.status = "failed"
            job.error_message = str(e)
            
        return job
        
    async def _retrieve_silo_documents(self, silo: SiloMetadata) -> List[Dict[str, Any]]:
        """Retrieve documents from a silo (mock implementation)"""
        # In real implementation, this would connect to actual data sources
        # like Git repos, Confluence, Slack, etc.
        
        mock_documents = [
            {
                "id": f"doc_{i}",
                "content": f"Sample document {i} from {silo.name}",
                "metadata": {
                    "source": silo.name,
                    "type": silo.silo_type,
                    "access_level": silo.data_classification
                }
            }
            for i in range(100)  # Mock 100 documents per silo
        ]
        
        return mock_documents
        
    async def _generate_embeddings(self, documents: List[Dict[str, Any]], 
                                 silo: SiloMetadata) -> np.ndarray:
        """Generate embeddings for documents with privacy preservation"""
        texts = [doc["content"] for doc in documents]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts)
        
        # Apply differential privacy noise
        if self.privacy_manager:
            embeddings = self.privacy_manager.add_noise_to_embeddings(
                embeddings, 
                privacy_budget=0.1,
                sensitivity=1.0
            )
            
        return embeddings
        
    def _generate_permission_aware_hashes(self, embeddings: np.ndarray, 
                                        access_rules: Dict[str, Any]) -> List[str]:
        """
        Generate secure hashes that encode both content and permission information.
        These hashes allow global search without revealing actual content.
        """
        secure_hashes = []
        
        for embedding in embeddings:
            # Combine embedding with access rules for secure hash
            content_hash = hashlib.sha256(embedding.tobytes()).hexdigest()
            permission_hash = hashlib.sha256(
                str(access_rules).encode()
            ).hexdigest()
            
            # Create composite hash
            secure_hash = hashlib.sha256(
                f"{content_hash}:{permission_hash}".encode()
            ).hexdigest()
            
            secure_hashes.append(secure_hash)
            
        return secure_hashes
        
    def _build_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Build FAISS index for fast similarity search"""
        dimension = embeddings.shape[1]
        
        # Use IndexFlatIP for cosine similarity
        index = faiss.IndexFlatIP(dimension)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        index.add(embeddings)
        
        return index
        
    def find_candidate_silos(self, query_embedding: np.ndarray, 
                           user_context: Any) -> List[str]:
        """
        Find silos that might contain relevant information for the query.
        Uses secure hashes to preserve privacy.
        """
        candidate_silos = []
        
        # Normalize query embedding
        query_embedding = query_embedding.reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        
        for silo_id, silo_data in self.silo_indexes.items():
            # Check if user has permission to access this silo
            if self.permission_engine.check_silo_access(
                silo_data["metadata"], user_context
            ):
                # Perform similarity search in local index
                scores, indices = silo_data["index"].search(query_embedding, k=1)
                
                # If similarity is above threshold, include silo
                if scores[0][0] > 0.3:  # Configurable threshold
                    candidate_silos.append(silo_id)
                    
        return candidate_silos
        
    async def update_silo_index(self, silo_id: str, 
                              new_documents: List[Dict[str, Any]]) -> bool:
        """Incrementally update a silo's index with new documents"""
        if silo_id not in self.silo_indexes:
            logger.error(f"Silo {silo_id} not found in indexes")
            return False
            
        try:
            silo_data = self.silo_indexes[silo_id]
            silo_metadata = silo_data["metadata"]
            
            # Generate embeddings for new documents
            new_embeddings = await self._generate_embeddings(new_documents, silo_metadata)
            
            # Add to existing FAISS index
            faiss.normalize_L2(new_embeddings)
            silo_data["index"].add(new_embeddings)
            
            # Update document count
            silo_data["document_count"] += len(new_documents)
            
            logger.info(f"Updated silo {silo_id} with {len(new_documents)} new documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update silo {silo_id}: {e}")
            return False