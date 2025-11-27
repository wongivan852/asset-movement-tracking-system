"""
SSO Integration with Business Platform
Handles authentication and user synchronization
Includes JWT token management for secure SSO
"""
import requests
import uuid
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import jwt
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class SSOTokenManager:
    """Manager for SSO JWT tokens."""

    @staticmethod
    def get_secret_key():
        """Get SSO secret key from settings."""
        return getattr(settings, 'SSO_SECRET_KEY', settings.SECRET_KEY)
    
    @staticmethod
    def get_algorithm():
        """Get JWT algorithm from settings."""
        return getattr(settings, 'SSO_ALGORITHM', 'HS256')
    
    @staticmethod
    def get_token_lifetime():
        """Get access token lifetime in seconds."""
        return getattr(settings, 'SSO_TOKEN_LIFETIME', 3600)  # 1 hour default
    
    @staticmethod
    def get_refresh_lifetime():
        """Get refresh token lifetime in seconds."""
        return getattr(settings, 'SSO_REFRESH_LIFETIME', 86400)  # 24 hours default
    
    @classmethod
    def generate_token(cls, user, request=None):
        """
        Generate JWT access and refresh tokens for a user.
        
        Args:
            user: Django User instance
            request: HTTP request (for audit logging)
        
        Returns:
            dict: {
                'access': access_token,
                'refresh': refresh_token,
                'jti': token_id,
                'expires_at': expiration_datetime
            }
        """
        now = timezone.now()
        jti = str(uuid.uuid4())
        
        # Access token payload
        access_payload = {
            'jti': jti,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': getattr(user, 'role', 'personnel'),
            'department': getattr(user, 'department', ''),
            'employee_id': getattr(user, 'employee_id', ''),
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(seconds=cls.get_token_lifetime())).timestamp()),
            'token_type': 'access',
        }
        
        # Refresh token payload (minimal data)
        refresh_payload = {
            'jti': jti + '_refresh',
            'user_id': user.id,
            'username': user.username,
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(seconds=cls.get_refresh_lifetime())).timestamp()),
            'token_type': 'refresh',
        }
        
        # Generate tokens
        access_token = jwt.encode(
            access_payload,
            cls.get_secret_key(),
            algorithm=cls.get_algorithm()
        )
        refresh_token = jwt.encode(
            refresh_payload,
            cls.get_secret_key(),
            algorithm=cls.get_algorithm()
        )
        
        logger.info(f"Generated SSO token for user {user.username} (jti: {jti})")
        
        return {
            'access': access_token,
            'refresh': refresh_token,
            'jti': jti,
            'expires_at': now + timedelta(seconds=cls.get_token_lifetime())
        }
    
    @classmethod
    def validate_token(cls, token, request=None):
        """
        Validate a JWT token.
        
        Args:
            token: JWT token string
            request: HTTP request (for audit logging)
        
        Returns:
            dict: Decoded token payload if valid
            None: If token is invalid
        
        Raises:
            jwt.ExpiredSignatureError: If token is expired
            jwt.InvalidTokenError: If token is invalid
        """
        try:
            # Decode token
            payload = jwt.decode(
                token,
                cls.get_secret_key(),
                algorithms=[cls.get_algorithm()]
            )
            
            # Check token type
            if payload.get('token_type') != 'access':
                raise jwt.InvalidTokenError('Invalid token type')
            
            logger.info(f"Token validated successfully for user_id: {payload.get('user_id')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token validation failed: Token expired")
            raise
        
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token validation failed: {str(e)}")
            raise
    
    @classmethod
    def refresh_token(cls, refresh_token, request=None):
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: Refresh token string
            request: HTTP request (for audit logging)
        
        Returns:
            dict: New access and refresh tokens
        
        Raises:
            jwt.InvalidTokenError: If refresh token is invalid
        """
        try:
            # Decode refresh token
            payload = jwt.decode(
                refresh_token,
                cls.get_secret_key(),
                algorithms=[cls.get_algorithm()]
            )
            
            # Check token type
            if payload.get('token_type') != 'refresh':
                raise jwt.InvalidTokenError('Invalid token type')
            
            # Get user and generate new tokens
            user_id = payload.get('user_id')
            user = User.objects.get(id=user_id)
            
            if not user.is_active:
                raise jwt.InvalidTokenError('User account is disabled')
            
            # Generate new token pair
            new_tokens = cls.generate_token(user, request)
            
            logger.info(f"Token refreshed for user {user.username}")
            return new_tokens
            
        except User.DoesNotExist:
            logger.error(f"Token refresh failed: User not found")
            raise jwt.InvalidTokenError('User not found')
        
        except jwt.ExpiredSignatureError:
            logger.warning("Token refresh failed: Refresh token expired")
            raise
        
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token refresh failed: {str(e)}")
            raise


class BusinessPlatformSSO:
    """
    SSO Client for integrating with the Business Platform
    """
    
    def __init__(self):
        self.base_url = getattr(settings, 'BUSINESS_PLATFORM_URL', 'http://localhost:8001')
        self.api_key = getattr(settings, 'BUSINESS_PLATFORM_API_KEY', '')
        self.client_id = getattr(settings, 'BUSINESS_PLATFORM_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'SSO_SECRET_KEY', '')
        
    def get_headers(self):
        """Get authentication headers for API requests"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
    
    def authenticate_user(self, username, password):
        """
        Authenticate user against business platform
        Returns user data if successful, None otherwise
        """
        try:
            response = requests.post(
                f'{self.base_url}/api/auth/login/',
                json={'username': username, 'password': password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                logger.warning(f"Authentication failed for user {username}: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error authenticating user {username}: {str(e)}")
            return None
    
    def get_user_info(self, user_id=None, username=None):
        """
        Fetch user information from business platform
        """
        try:
            params = {}
            if user_id:
                params['id'] = user_id
            if username:
                params['username'] = username
                
            response = requests.get(
                f'{self.base_url}/api/users/info/',
                headers=self.get_headers(),
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to fetch user info: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error fetching user info: {str(e)}")
            return None
    
    def sync_all_users(self):
        """
        Synchronize all users from business platform
        Returns tuple (created_count, updated_count, errors)
        """
        created = 0
        updated = 0
        errors = []
        
        try:
            response = requests.get(
                f'{self.base_url}/api/users/list/',
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch users: {response.status_code}")
                return (0, 0, [f"API returned status {response.status_code}"])
            
            users_data = response.json()
            
            for user_data in users_data.get('users', []):
                try:
                    result = self.sync_user(user_data)
                    if result == 'created':
                        created += 1
                    elif result == 'updated':
                        updated += 1
                except Exception as e:
                    errors.append(f"Error syncing user {user_data.get('username')}: {str(e)}")
                    logger.error(f"Error syncing user: {str(e)}")
            
            return (created, updated, errors)
            
        except requests.RequestException as e:
            logger.error(f"Error syncing users: {str(e)}")
            return (0, 0, [str(e)])
    
    def sync_user(self, user_data):
        """
        Create or update a local user from business platform data
        Returns 'created', 'updated', or None
        """
        username = user_data.get('username')
        if not username:
            return None
        
        # Map business platform fields to local user model
        user_fields = {
            'email': user_data.get('email', ''),
            'first_name': user_data.get('first_name', ''),
            'last_name': user_data.get('last_name', ''),
            'is_active': user_data.get('is_active', True),
            'phone': user_data.get('phone', ''),
            'department': user_data.get('department', ''),
            'employee_id': user_data.get('employee_id', ''),
        }
        
        # Map role from business platform to asset tracker role
        bp_role = user_data.get('role', 'user')
        role_mapping = {
            'admin': 'admin',
            'manager': 'location_manager',
            'user': 'personnel',
            'staff': 'personnel',
        }
        user_fields['role'] = role_mapping.get(bp_role, 'personnel')
        
        # Check if user exists
        user, created = User.objects.update_or_create(
            username=username,
            defaults=user_fields
        )
        
        # Set staff and superuser flags based on role
        if user_fields['role'] == 'admin':
            user.is_staff = True
            user.is_superuser = True
            user.save()
        
        return 'created' if created else 'updated'
    
    def verify_token(self, token):
        """
        Verify JWT token from business platform
        Returns user data if valid, None otherwise
        """
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                self.client_secret,
                algorithms=['HS256'],
                options={'verify_exp': True}
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
    
    def create_local_token(self, user):
        """
        Create a local JWT token for the user
        """
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
        }
        
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token


# Singleton instance
sso_client = BusinessPlatformSSO()
