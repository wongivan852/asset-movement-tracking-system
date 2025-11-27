"""
Custom authentication backend for Business Platform SSO
Supports both password authentication and JWT token authentication
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .sso import sso_client, SSOTokenManager
import jwt
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class BusinessPlatformAuthBackend(ModelBackend):
    """
    Custom authentication backend that tries:
    1. JWT token authentication (if token provided)
    2. Business Platform SSO (if username/password provided)
    3. Falls back to local authentication
    """
    
    def authenticate(self, request, username=None, password=None, token=None, **kwargs):
        # Try JWT token authentication if token is provided
        if token:
            try:
                payload = SSOTokenManager.validate_token(token, request)
                user_id = payload.get('user_id')
                user = User.objects.get(id=user_id)
                
                if self.user_can_authenticate(user):
                    logger.info(f"User {user.username} authenticated via JWT token")
                    return user
            except (jwt.InvalidTokenError, jwt.ExpiredSignatureError, User.DoesNotExist) as e:
                logger.warning(f"JWT token authentication failed: {str(e)}")
                return None
        
        # Require username and password for other authentication methods
        if username is None or password is None:
            return None
        
        # Try SSO authentication first
        try:
            user_data = sso_client.authenticate_user(username, password)
            
            if user_data:
                # Sync user from business platform
                user = self._sync_and_get_user(user_data)
                if user:
                    logger.info(f"User {username} authenticated via SSO")
                    return user
        except Exception as e:
            logger.error(f"SSO authentication error: {str(e)}")
        
        # Fall back to local authentication
        try:
            user = User.objects.get(username=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                logger.info(f"User {username} authenticated locally")
                return user
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            User().set_password(password)
        
        return None
    
    def _sync_and_get_user(self, user_data):
        """
        Synchronize user data from business platform and return User object
        """
        try:
            username = user_data.get('username') or user_data.get('user', {}).get('username')
            if not username:
                return None
            
            # Get or create user
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': user_data.get('email', ''),
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                }
            )
            
            # Update user fields
            if not created:
                user.email = user_data.get('email', user.email)
                user.first_name = user_data.get('first_name', user.first_name)
                user.last_name = user_data.get('last_name', user.last_name)
            
            # Map role
            bp_role = user_data.get('role', 'user')
            role_mapping = {
                'admin': 'admin',
                'manager': 'location_manager',
                'user': 'personnel',
                'staff': 'personnel',
            }
            user.role = role_mapping.get(bp_role, 'personnel')
            
            # Update additional fields
            user.phone = user_data.get('phone', user.phone or '')
            user.department = user_data.get('department', user.department or '')
            user.employee_id = user_data.get('employee_id', user.employee_id or '')
            user.is_active = user_data.get('is_active', True)
            
            # Set password unusable for SSO users (they authenticate via business platform)
            if created:
                user.set_unusable_password()
            
            user.save()
            
            return user if self.user_can_authenticate(user) else None
            
        except Exception as e:
            logger.error(f"Error syncing user: {str(e)}")
            return None
    
    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            return user if self.user_can_authenticate(user) else None
        except User.DoesNotExist:
            return None
