"""
Encryption Manager - Secure Data Handling and Storage
"""

import logging
import secrets
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Manages encryption and decryption for secure cross-silo communication
    and data storage.
    """
    
    def __init__(self):
        self.symmetric_keys = {}  # Store symmetric keys per silo
        self.asymmetric_keys = {}  # Store public/private key pairs
        
    def generate_silo_keys(self, silo_id: str) -> Dict[str, Any]:
        """Generate encryption keys for a specific silo"""
        
        # Generate symmetric key for fast encryption/decryption
        symmetric_key = Fernet.generate_key()
        
        # Generate asymmetric key pair for secure key exchange
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        
        # Store keys
        self.symmetric_keys[silo_id] = symmetric_key
        self.asymmetric_keys[silo_id] = {
            'private': private_key,
            'public': public_key
        }
        
        # Serialize public key for sharing
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return {
            'silo_id': silo_id,
            'symmetric_key': base64.b64encode(symmetric_key).decode(),
            'public_key': public_key_bytes.decode(),
            'key_fingerprint': self._generate_key_fingerprint(public_key_bytes)
        }
        
    def encrypt_silo_data(self, silo_id: str, data: str) -> str:
        """Encrypt data for a specific silo"""
        
        if silo_id not in self.symmetric_keys:
            raise ValueError(f"No encryption key found for silo {silo_id}")
            
        symmetric_key = self.symmetric_keys[silo_id]
        fernet = Fernet(symmetric_key)
        
        encrypted_data = fernet.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
        
    def decrypt_silo_data(self, silo_id: str, encrypted_data: str) -> str:
        """Decrypt data from a specific silo"""
        
        if silo_id not in self.symmetric_keys:
            raise ValueError(f"No decryption key found for silo {silo_id}")
            
        symmetric_key = self.symmetric_keys[silo_id]
        fernet = Fernet(symmetric_key)
        
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = fernet.decrypt(encrypted_bytes)
        
        return decrypted_data.decode()
        
    def encrypt_cross_silo_message(self, sender_silo_id: str, 
                                 receiver_silo_id: str, 
                                 message: str) -> Dict[str, str]:
        """
        Encrypt message for cross-silo communication using hybrid encryption.
        Uses receiver's public key to encrypt a session key, then uses session
        key to encrypt the actual message.
        """
        
        if receiver_silo_id not in self.asymmetric_keys:
            raise ValueError(f"No public key found for receiver silo {receiver_silo_id}")
            
        # Generate session key for this message
        session_key = Fernet.generate_key()
        
        # Encrypt message with session key
        fernet = Fernet(session_key)
        encrypted_message = fernet.encrypt(message.encode())
        
        # Encrypt session key with receiver's public key
        receiver_public_key = self.asymmetric_keys[receiver_silo_id]['public']
        encrypted_session_key = receiver_public_key.encrypt(
            session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return {
            'sender_silo_id': sender_silo_id,
            'receiver_silo_id': receiver_silo_id,
            'encrypted_message': base64.b64encode(encrypted_message).decode(),
            'encrypted_session_key': base64.b64encode(encrypted_session_key).decode(),
            'message_hash': self._generate_message_hash(message)
        }
        
    def decrypt_cross_silo_message(self, encrypted_package: Dict[str, str]) -> str:
        """Decrypt cross-silo message"""
        
        receiver_silo_id = encrypted_package['receiver_silo_id']
        
        if receiver_silo_id not in self.asymmetric_keys:
            raise ValueError(f"No private key found for silo {receiver_silo_id}")
            
        # Decrypt session key with private key
        private_key = self.asymmetric_keys[receiver_silo_id]['private']
        encrypted_session_key = base64.b64decode(
            encrypted_package['encrypted_session_key'].encode()
        )
        
        session_key = private_key.decrypt(
            encrypted_session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Decrypt message with session key
        fernet = Fernet(session_key)
        encrypted_message = base64.b64decode(
            encrypted_package['encrypted_message'].encode()
        )
        
        decrypted_message = fernet.decrypt(encrypted_message).decode()
        
        # Verify message integrity
        expected_hash = encrypted_package.get('message_hash')
        if expected_hash:
            actual_hash = self._generate_message_hash(decrypted_message)
            if actual_hash != expected_hash:
                raise ValueError("Message integrity check failed")
                
        return decrypted_message
        
    def create_secure_index_hash(self, content: str, silo_id: str) -> str:
        """
        Create secure hash for indexing that includes silo-specific salt.
        This allows global search while maintaining privacy.
        """
        
        # Get or create silo-specific salt
        silo_salt = self._get_silo_salt(silo_id)
        
        # Combine content with silo salt
        salted_content = f"{content}:{silo_salt}"
        
        # Create secure hash
        hash_object = hashlib.sha256(salted_content.encode())
        secure_hash = hash_object.hexdigest()
        
        return secure_hash
        
    def encrypt_embedding_vector(self, embedding: List[float], 
                               silo_id: str) -> str:
        """Encrypt embedding vector for secure storage"""
        
        # Convert embedding to string representation
        embedding_str = ','.join(map(str, embedding))
        
        # Encrypt using silo-specific key
        encrypted_embedding = self.encrypt_silo_data(silo_id, embedding_str)
        
        return encrypted_embedding
        
    def decrypt_embedding_vector(self, encrypted_embedding: str, 
                               silo_id: str) -> List[float]:
        """Decrypt embedding vector"""
        
        # Decrypt embedding string
        embedding_str = self.decrypt_silo_data(silo_id, encrypted_embedding)
        
        # Convert back to float list
        embedding = [float(x) for x in embedding_str.split(',')]
        
        return embedding
        
    def create_permission_token(self, user_id: str, silo_id: str, 
                              permissions: List[str], 
                              expiry_timestamp: int) -> str:
        """
        Create encrypted permission token for cross-silo access.
        Token contains user permissions and expiry time.
        """
        
        token_data = {
            'user_id': user_id,
            'silo_id': silo_id,
            'permissions': permissions,
            'expiry': expiry_timestamp,
            'nonce': secrets.token_hex(16)
        }
        
        # Serialize token data
        token_str = str(token_data)
        
        # Encrypt token
        encrypted_token = self.encrypt_silo_data(silo_id, token_str)
        
        return encrypted_token
        
    def verify_permission_token(self, token: str, silo_id: str) -> Optional[Dict[str, Any]]:
        """Verify and decode permission token"""
        
        try:
            # Decrypt token
            token_str = self.decrypt_silo_data(silo_id, token)
            
            # Parse token data (in production, use proper JSON serialization)
            token_data = eval(token_str)  # WARNING: Use json.loads in production
            
            # Check expiry
            import time
            if time.time() > token_data['expiry']:
                logger.warning(f"Permission token expired for silo {silo_id}")
                return None
                
            return token_data
            
        except Exception as e:
            logger.error(f"Failed to verify permission token: {e}")
            return None
            
    def rotate_silo_keys(self, silo_id: str) -> Dict[str, Any]:
        """Rotate encryption keys for a silo"""
        
        logger.info(f"Rotating keys for silo {silo_id}")
        
        # Generate new keys
        new_keys = self.generate_silo_keys(silo_id)
        
        # In production, you would:
        # 1. Re-encrypt all data with new keys
        # 2. Update key distribution to other silos
        # 3. Maintain old keys temporarily for transition
        
        return new_keys
        
    def _generate_key_fingerprint(self, public_key_bytes: bytes) -> str:
        """Generate fingerprint for public key"""
        hash_object = hashlib.sha256(public_key_bytes)
        fingerprint = hash_object.hexdigest()[:16]  # First 16 chars
        return fingerprint
        
    def _generate_message_hash(self, message: str) -> str:
        """Generate hash for message integrity verification"""
        hash_object = hashlib.sha256(message.encode())
        return hash_object.hexdigest()
        
    def _get_silo_salt(self, silo_id: str) -> str:
        """Get or create silo-specific salt for hashing"""
        
        # In production, store salts securely
        salt_key = f"salt_{silo_id}"
        
        if not hasattr(self, '_silo_salts'):
            self._silo_salts = {}
            
        if salt_key not in self._silo_salts:
            self._silo_salts[salt_key] = secrets.token_hex(32)
            
        return self._silo_salts[salt_key]
        
    def export_public_keys(self) -> Dict[str, str]:
        """Export all public keys for sharing with other silos"""
        
        public_keys = {}
        
        for silo_id, keys in self.asymmetric_keys.items():
            public_key = keys['public']
            public_key_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            public_keys[silo_id] = public_key_bytes.decode()
            
        return public_keys
        
    def import_public_key(self, silo_id: str, public_key_pem: str) -> bool:
        """Import public key from another silo"""
        
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode()
            )
            
            if silo_id not in self.asymmetric_keys:
                self.asymmetric_keys[silo_id] = {}
                
            self.asymmetric_keys[silo_id]['public'] = public_key
            
            logger.info(f"Imported public key for silo {silo_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import public key for silo {silo_id}: {e}")
            return False
            
    def get_encryption_status(self) -> Dict[str, Any]:
        """Get status of encryption keys and operations"""
        
        return {
            'total_silos_with_symmetric_keys': len(self.symmetric_keys),
            'total_silos_with_asymmetric_keys': len(self.asymmetric_keys),
            'silos_with_complete_keys': len(
                set(self.symmetric_keys.keys()) & set(self.asymmetric_keys.keys())
            ),
            'key_fingerprints': {
                silo_id: self._generate_key_fingerprint(
                    keys['public'].public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                )
                for silo_id, keys in self.asymmetric_keys.items()
                if 'public' in keys
            }
        }