"""
Differential Privacy Manager - Privacy-Preserving Data Processing
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import secrets
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class DifferentialPrivacyManager:
    """
    Implements differential privacy mechanisms to protect sensitive
    information while enabling federated knowledge sharing.
    """
    
    def __init__(self, global_privacy_budget: float = 1.0):
        self.global_privacy_budget = global_privacy_budget
        self.used_privacy_budget = 0.0
        self.privacy_accountant = PrivacyAccountant()
        
    def add_noise_to_embeddings(self, embeddings: np.ndarray, 
                              privacy_budget: float,
                              sensitivity: float = 1.0) -> np.ndarray:
        """
        Add calibrated noise to embeddings to ensure differential privacy.
        
        Uses Gaussian mechanism for continuous data.
        """
        if not self._check_privacy_budget(privacy_budget):
            raise ValueError("Insufficient privacy budget")
            
        # Calculate noise scale based on privacy parameters
        # σ = √(2 ln(1.25/δ)) * Δf / ε
        # where δ = 1e-5 (failure probability), Δf = sensitivity, ε = privacy_budget
        
        delta = 1e-5
        noise_scale = np.sqrt(2 * np.log(1.25 / delta)) * sensitivity / privacy_budget
        
        # Generate Gaussian noise
        noise = np.random.normal(0, noise_scale, embeddings.shape)
        
        # Add noise to embeddings
        noisy_embeddings = embeddings + noise
        
        # Update privacy budget
        self._consume_privacy_budget(privacy_budget)
        
        # Record privacy usage
        self.privacy_accountant.record_mechanism_usage(
            mechanism="gaussian_noise",
            privacy_budget=privacy_budget,
            sensitivity=sensitivity,
            data_size=embeddings.shape[0]
        )
        
        logger.debug(f"Added Gaussian noise with scale {noise_scale:.4f} to {embeddings.shape[0]} embeddings")
        return noisy_embeddings
        
    def add_noise_to_score(self, score: float, privacy_budget: float) -> float:
        """Add noise to similarity scores for privacy preservation"""
        
        if not self._check_privacy_budget(privacy_budget):
            return score  # Return original if no budget
            
        # Use Laplace mechanism for scores (bounded sensitivity)
        sensitivity = 0.1  # Assume bounded similarity scores
        noise_scale = sensitivity / privacy_budget
        
        # Generate Laplace noise
        noise = np.random.laplace(0, noise_scale)
        noisy_score = score + noise
        
        # Clamp to valid score range [0, 1]
        noisy_score = np.clip(noisy_score, 0.0, 1.0)
        
        self._consume_privacy_budget(privacy_budget)
        
        return float(noisy_score)
        
    def create_private_histogram(self, data: List[Any], 
                               bins: int, privacy_budget: float) -> Dict[str, int]:
        """Create differentially private histogram"""
        
        if not self._check_privacy_budget(privacy_budget):
            raise ValueError("Insufficient privacy budget")
            
        # Create true histogram
        histogram = {}
        for item in data:
            key = str(item)
            histogram[key] = histogram.get(key, 0) + 1
            
        # Add Laplace noise to each bin
        sensitivity = 1  # Adding/removing one item changes count by at most 1
        noise_scale = sensitivity / privacy_budget
        
        private_histogram = {}
        for key, count in histogram.items():
            noise = np.random.laplace(0, noise_scale)
            noisy_count = max(0, int(count + noise))  # Ensure non-negative
            private_histogram[key] = noisy_count
            
        self._consume_privacy_budget(privacy_budget)
        
        self.privacy_accountant.record_mechanism_usage(
            mechanism="laplace_histogram",
            privacy_budget=privacy_budget,
            sensitivity=sensitivity,
            data_size=len(data)
        )
        
        return private_histogram
        
    def private_top_k(self, items: Dict[str, float], k: int, 
                     privacy_budget: float) -> List[Tuple[str, float]]:
        """
        Return top-k items with differential privacy using exponential mechanism.
        """
        
        if not self._check_privacy_budget(privacy_budget):
            raise ValueError("Insufficient privacy budget")
            
        if not items:
            return []
            
        # Exponential mechanism for selecting top-k
        sensitivity = 1.0  # Removing one item changes rank by at most 1
        
        # Calculate selection probabilities
        items_list = list(items.items())
        scores = np.array([score for _, score in items_list])
        
        # Apply exponential mechanism
        probabilities = np.exp(privacy_budget * scores / (2 * sensitivity))
        probabilities = probabilities / np.sum(probabilities)
        
        # Sample k items without replacement
        selected_indices = np.random.choice(
            len(items_list), 
            size=min(k, len(items_list)), 
            replace=False, 
            p=probabilities
        )
        
        # Add noise to selected scores
        result = []
        for idx in selected_indices:
            item_name, original_score = items_list[idx]
            noisy_score = self.add_noise_to_score(original_score, privacy_budget / k)
            result.append((item_name, noisy_score))
            
        # Sort by noisy scores
        result.sort(key=lambda x: x[1], reverse=True)
        
        self._consume_privacy_budget(privacy_budget)
        
        return result
        
    def anonymize_text(self, text: str, privacy_level: str = "medium") -> str:
        """
        Anonymize text content while preserving semantic meaning.
        """
        
        # Define anonymization strategies by privacy level
        strategies = {
            "low": ["remove_emails", "remove_phone_numbers"],
            "medium": ["remove_emails", "remove_phone_numbers", "replace_names", "generalize_numbers"],
            "high": ["remove_emails", "remove_phone_numbers", "replace_names", 
                    "generalize_numbers", "remove_dates", "generalize_locations"]
        }
        
        anonymized_text = text
        
        for strategy in strategies.get(privacy_level, strategies["medium"]):
            anonymized_text = self._apply_anonymization_strategy(anonymized_text, strategy)
            
        return anonymized_text
        
    def _apply_anonymization_strategy(self, text: str, strategy: str) -> str:
        """Apply specific anonymization strategy"""
        
        import re
        
        if strategy == "remove_emails":
            # Replace email addresses with [EMAIL]
            text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
            
        elif strategy == "remove_phone_numbers":
            # Replace phone numbers with [PHONE]
            text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
            
        elif strategy == "replace_names":
            # Replace common name patterns with [NAME]
            # This is a simplified implementation
            name_patterns = [
                r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # First Last
                r'\b[A-Z]\. [A-Z][a-z]+\b',      # F. Last
            ]
            for pattern in name_patterns:
                text = re.sub(pattern, '[NAME]', text)
                
        elif strategy == "generalize_numbers":
            # Replace specific numbers with ranges
            text = re.sub(r'\b\d{4,}\b', '[LARGE_NUMBER]', text)
            
        elif strategy == "remove_dates":
            # Replace dates with [DATE]
            date_patterns = [
                r'\b\d{1,2}/\d{1,2}/\d{4}\b',
                r'\b\d{4}-\d{2}-\d{2}\b',
                r'\b[A-Za-z]+ \d{1,2}, \d{4}\b'
            ]
            for pattern in date_patterns:
                text = re.sub(pattern, '[DATE]', text)
                
        elif strategy == "generalize_locations":
            # Replace specific addresses with [LOCATION]
            text = re.sub(r'\b\d+ [A-Za-z ]+ (Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)\b', 
                         '[LOCATION]', text)
                         
        return text
        
    def create_secure_hash(self, data: str, salt: Optional[str] = None) -> str:
        """Create secure hash with optional salt for privacy preservation"""
        
        if salt is None:
            salt = secrets.token_hex(16)
            
        # Combine data with salt
        salted_data = f"{data}:{salt}"
        
        # Create SHA-256 hash
        hash_object = hashlib.sha256(salted_data.encode())
        secure_hash = hash_object.hexdigest()
        
        return secure_hash
        
    def encrypt_sensitive_data(self, data: str, key: Optional[bytes] = None) -> Tuple[str, bytes]:
        """Encrypt sensitive data for secure storage"""
        
        if key is None:
            key = Fernet.generate_key()
            
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode())
        
        return encrypted_data.decode(), key
        
    def decrypt_sensitive_data(self, encrypted_data: str, key: bytes) -> str:
        """Decrypt sensitive data"""
        
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data.encode())
        
        return decrypted_data.decode()
        
    def _check_privacy_budget(self, requested_budget: float) -> bool:
        """Check if sufficient privacy budget is available"""
        return (self.used_privacy_budget + requested_budget) <= self.global_privacy_budget
        
    def _consume_privacy_budget(self, budget: float) -> None:
        """Consume privacy budget"""
        self.used_privacy_budget += budget
        logger.debug(f"Consumed {budget:.4f} privacy budget. Remaining: {self.get_remaining_budget():.4f}")
        
    def get_remaining_budget(self) -> float:
        """Get remaining privacy budget"""
        return self.global_privacy_budget - self.used_privacy_budget
        
    def reset_privacy_budget(self) -> None:
        """Reset privacy budget (use carefully!)"""
        self.used_privacy_budget = 0.0
        self.privacy_accountant.reset()
        logger.info("Privacy budget reset")
        
    def get_privacy_report(self) -> Dict[str, Any]:
        """Generate privacy usage report"""
        return {
            "global_budget": self.global_privacy_budget,
            "used_budget": self.used_privacy_budget,
            "remaining_budget": self.get_remaining_budget(),
            "usage_percentage": (self.used_privacy_budget / self.global_privacy_budget) * 100,
            "mechanism_usage": self.privacy_accountant.get_usage_summary()
        }


class PrivacyAccountant:
    """Tracks privacy budget usage across different mechanisms"""
    
    def __init__(self):
        self.usage_log = []
        
    def record_mechanism_usage(self, mechanism: str, privacy_budget: float,
                             sensitivity: float, data_size: int) -> None:
        """Record usage of a privacy mechanism"""
        
        usage_record = {
            "timestamp": np.datetime64('now'),
            "mechanism": mechanism,
            "privacy_budget": privacy_budget,
            "sensitivity": sensitivity,
            "data_size": data_size
        }
        
        self.usage_log.append(usage_record)
        
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get summary of privacy mechanism usage"""
        
        if not self.usage_log:
            return {"total_mechanisms": 0, "total_budget_used": 0.0}
            
        mechanisms = {}
        total_budget = 0.0
        
        for record in self.usage_log:
            mechanism = record["mechanism"]
            budget = record["privacy_budget"]
            
            if mechanism not in mechanisms:
                mechanisms[mechanism] = {
                    "count": 0,
                    "total_budget": 0.0,
                    "avg_budget": 0.0
                }
                
            mechanisms[mechanism]["count"] += 1
            mechanisms[mechanism]["total_budget"] += budget
            total_budget += budget
            
        # Calculate averages
        for mechanism_data in mechanisms.values():
            mechanism_data["avg_budget"] = mechanism_data["total_budget"] / mechanism_data["count"]
            
        return {
            "total_mechanisms": len(self.usage_log),
            "total_budget_used": total_budget,
            "mechanisms": mechanisms
        }
        
    def reset(self) -> None:
        """Reset usage log"""
        self.usage_log = []