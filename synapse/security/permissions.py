"""
Permission Engine - Access Control and Authorization
"""

import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta

from ..models import UserContext, SiloMetadata, KnowledgeResult, AccessLevel

logger = logging.getLogger(__name__)


class PermissionEngine:
    """
    Manages access control across organizational silos with fine-grained
    permissions and temporal constraints.
    """
    
    def __init__(self):
        # Cache for permission decisions to improve performance
        self.permission_cache = {}
        self.cache_ttl = timedelta(minutes=5)
        
    def check_silo_access(self, silo_metadata: SiloMetadata, 
                         user_context: UserContext) -> bool:
        """Check if user can access a specific silo"""
        
        cache_key = f"{user_context.user_id}:{silo_metadata.silo_id}"
        cached_result = self._get_cached_permission(cache_key)
        if cached_result is not None:
            return cached_result
            
        # Check organizational boundary
        if not self._check_organizational_access(silo_metadata, user_context):
            self._cache_permission(cache_key, False)
            return False
            
        # Check team membership
        if not self._check_team_access(silo_metadata, user_context):
            self._cache_permission(cache_key, False)
            return False
            
        # Check data classification level
        if not self._check_classification_access(silo_metadata, user_context):
            self._cache_permission(cache_key, False)
            return False
            
        # Check temporal constraints
        if not self._check_temporal_constraints(silo_metadata, user_context):
            self._cache_permission(cache_key, False)
            return False
            
        # Check custom access rules
        if not self._check_custom_rules(silo_metadata, user_context):
            self._cache_permission(cache_key, False)
            return False
            
        self._cache_permission(cache_key, True)
        return True
        
    def _check_organizational_access(self, silo_metadata: SiloMetadata,
                                   user_context: UserContext) -> bool:
        """Check organizational boundary access"""
        
        # Same organization - allow
        if silo_metadata.organization_id == user_context.organization_id:
            return True
            
        # Cross-organizational access requires special permissions
        if hasattr(user_context, 'cross_org_permissions'):
            allowed_orgs = user_context.cross_org_permissions.get('organizations', [])
            return silo_metadata.organization_id in allowed_orgs
            
        return False
        
    def _check_team_access(self, silo_metadata: SiloMetadata,
                          user_context: UserContext) -> bool:
        """Check team-level access"""
        
        # Direct team membership
        if silo_metadata.team_id in user_context.team_ids:
            return True
            
        # Check for cross-team access rules
        access_rules = silo_metadata.access_rules
        if 'allowed_teams' in access_rules:
            allowed_teams = set(access_rules['allowed_teams'])
            user_teams = set(user_context.team_ids)
            if allowed_teams.intersection(user_teams):
                return True
                
        # Check for public team access
        if access_rules.get('public_within_org', False):
            return silo_metadata.organization_id == user_context.organization_id
            
        return False
        
    def _check_classification_access(self, silo_metadata: SiloMetadata,
                                   user_context: UserContext) -> bool:
        """Check data classification level access"""
        
        # Define classification hierarchy
        classification_levels = {
            AccessLevel.PUBLIC: 0,
            AccessLevel.INTERNAL: 1,
            AccessLevel.CONFIDENTIAL: 2, 
            AccessLevel.RESTRICTED: 3
        }
        
        required_level = classification_levels.get(silo_metadata.data_classification, 3)
        
        # Check user's maximum clearance level
        user_max_level = 0
        for access_level in user_context.access_levels:
            level_value = classification_levels.get(access_level, 0)
            user_max_level = max(user_max_level, level_value)
            
        return user_max_level >= required_level
        
    def _check_temporal_constraints(self, silo_metadata: SiloMetadata,
                                  user_context: UserContext) -> bool:
        """Check time-based access constraints"""
        
        if not user_context.temporal_constraints:
            return True
            
        current_time = datetime.utcnow()
        constraints = user_context.temporal_constraints
        
        # Check access window
        if 'access_start' in constraints and 'access_end' in constraints:
            start_time = datetime.fromisoformat(constraints['access_start'])
            end_time = datetime.fromisoformat(constraints['access_end'])
            
            if not (start_time <= current_time <= end_time):
                return False
                
        # Check business hours constraint
        if constraints.get('business_hours_only', False):
            # Assume business hours are 9 AM to 6 PM UTC
            if not (9 <= current_time.hour < 18):
                return False
                
        # Check data freshness requirements
        if 'max_data_age_days' in constraints:
            max_age = timedelta(days=constraints['max_data_age_days'])
            if silo_metadata.last_indexed:
                data_age = current_time - silo_metadata.last_indexed
                if data_age > max_age:
                    return False
                    
        return True
        
    def _check_custom_rules(self, silo_metadata: SiloMetadata,
                          user_context: UserContext) -> bool:
        """Check custom access rules defined in silo metadata"""
        
        access_rules = silo_metadata.access_rules
        
        # Check required roles
        if 'required_roles' in access_rules:
            required_roles = set(access_rules['required_roles'])
            user_roles = set(getattr(user_context, 'roles', []))
            if not required_roles.intersection(user_roles):
                return False
                
        # Check forbidden users
        if 'forbidden_users' in access_rules:
            if user_context.user_id in access_rules['forbidden_users']:
                return False
                
        # Check minimum security clearance
        if 'min_security_clearance' in access_rules:
            required_clearance = access_rules['min_security_clearance']
            user_clearance = user_context.security_clearance
            
            if not user_clearance or not self._compare_clearance_levels(
                user_clearance, required_clearance
            ):
                return False
                
        # Check project-specific access
        if 'required_projects' in access_rules:
            required_projects = set(access_rules['required_projects'])
            user_projects = set(getattr(user_context, 'project_access', []))
            if not required_projects.intersection(user_projects):
                return False
                
        return True
        
    def _compare_clearance_levels(self, user_clearance: str, 
                                required_clearance: str) -> bool:
        """Compare security clearance levels"""
        
        clearance_hierarchy = {
            'public': 0,
            'confidential': 1,
            'secret': 2,
            'top_secret': 3
        }
        
        user_level = clearance_hierarchy.get(user_clearance.lower(), 0)
        required_level = clearance_hierarchy.get(required_clearance.lower(), 3)
        
        return user_level >= required_level
        
    def check_document_access(self, silo_metadata: SiloMetadata, 
                            doc_index: int, user_context: UserContext) -> bool:
        """Check access to a specific document within a silo"""
        
        # First check silo-level access
        if not self.check_silo_access(silo_metadata, user_context):
            return False
            
        # Document-level access rules (mock implementation)
        # In reality, this would check document-specific metadata
        
        access_rules = silo_metadata.access_rules
        
        # Check for document-level restrictions
        if 'restricted_documents' in access_rules:
            if doc_index in access_rules['restricted_documents']:
                # Check if user has special permission for restricted docs
                if not getattr(user_context, 'can_access_restricted_docs', False):
                    return False
                    
        return True
        
    async def check_synthesis_access(self, result: KnowledgeResult,
                                   user_context: UserContext) -> bool:
        """Final permission check before including result in synthesis"""
        
        # Check if result's access level is still valid for user
        if not self._check_result_access_level(result, user_context):
            return False
            
        # Check for synthesis-specific restrictions
        if hasattr(result, 'synthesis_restrictions'):
            restrictions = result.synthesis_restrictions
            
            # Check if user can see this result in synthesis context
            if restrictions.get('no_synthesis', False):
                return False
                
            # Check minimum confidence threshold for synthesis
            min_confidence = restrictions.get('min_confidence_for_synthesis', 0.0)
            if result.relevance_score < min_confidence:
                return False
                
        return True
        
    def _check_result_access_level(self, result: KnowledgeResult,
                                 user_context: UserContext) -> bool:
        """Check if user can access result based on its access level"""
        
        classification_levels = {
            AccessLevel.PUBLIC: 0,
            AccessLevel.INTERNAL: 1,
            AccessLevel.CONFIDENTIAL: 2,
            AccessLevel.RESTRICTED: 3
        }
        
        required_level = classification_levels.get(result.access_level, 3)
        user_max_level = max(
            classification_levels.get(level, 0) 
            for level in user_context.access_levels
        ) if user_context.access_levels else 0
        
        return user_max_level >= required_level
        
    def _get_cached_permission(self, cache_key: str) -> Optional[bool]:
        """Get cached permission decision if still valid"""
        
        if cache_key in self.permission_cache:
            cached_time, result = self.permission_cache[cache_key]
            if datetime.utcnow() - cached_time < self.cache_ttl:
                return result
                
        return None
        
    def _cache_permission(self, cache_key: str, result: bool) -> None:
        """Cache permission decision with timestamp"""
        self.permission_cache[cache_key] = (datetime.utcnow(), result)
        
        # Clean old cache entries periodically
        if len(self.permission_cache) > 1000:
            self._clean_permission_cache()
            
    def _clean_permission_cache(self) -> None:
        """Remove expired cache entries"""
        current_time = datetime.utcnow()
        expired_keys = [
            key for key, (cached_time, _) in self.permission_cache.items()
            if current_time - cached_time > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.permission_cache[key]
            
        logger.debug(f"Cleaned {len(expired_keys)} expired permission cache entries")
        
    def audit_access_attempt(self, user_context: UserContext, 
                           silo_metadata: SiloMetadata, 
                           granted: bool, reason: str = "") -> None:
        """Log access attempt for audit trail"""
        
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_context.user_id,
            'organization_id': user_context.organization_id,
            'silo_id': silo_metadata.silo_id,
            'silo_name': silo_metadata.name,
            'access_granted': granted,
            'reason': reason,
            'user_access_levels': user_context.access_levels,
            'data_classification': silo_metadata.data_classification
        }
        
        # In production, this would write to a secure audit log
        logger.info(f"Access audit: {audit_entry}")
        
    def get_accessible_silos(self, user_context: UserContext,
                           all_silos: List[SiloMetadata]) -> List[SiloMetadata]:
        """Get list of all silos accessible to user"""
        
        accessible_silos = []
        
        for silo in all_silos:
            if self.check_silo_access(silo, user_context):
                accessible_silos.append(silo)
                
        return accessible_silos