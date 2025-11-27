"""
SSO Middleware for JWT token authentication
"""
from django.contrib.auth import get_user_model
from django.utils.functional import SimpleLazyObject
from .sso import SSOTokenManager
import jwt
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class SSOTokenAuthenticationMiddleware:
    """
    Middleware to authenticate users via JWT tokens in requests.
    Checks for JWT token in Authorization header and authenticates the user.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # Validate token and authenticate user
            request.user = SimpleLazyObject(lambda: self._authenticate_via_token(request, token))
        
        response = self.get_response(request)
        return response
    
    def _authenticate_via_token(self, request, token):
        """
        Authenticate user via JWT token.
        Returns authenticated user or AnonymousUser.
        """
        try:
            # Validate token
            payload = SSOTokenManager.validate_token(token, request)
            user_id = payload.get('user_id')
            
            # Get user from database
            user = User.objects.get(id=user_id, is_active=True)
            
            logger.info(f"User {user.username} authenticated via JWT token middleware")
            return user
            
        except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
            logger.debug("Invalid or expired JWT token in request")
            return request.user  # Return existing user (likely AnonymousUser)
            
        except User.DoesNotExist:
            logger.warning(f"User not found for JWT token")
            return request.user
            
        except Exception as e:
            logger.error(f"Error in SSO token authentication middleware: {str(e)}")
            return request.user


class SSOAuditMiddleware:
    """
    Middleware to log SSO-related activities.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Log SSO API requests
        if request.path.startswith('/accounts/api/sso/'):
            logger.info(
                f"SSO API Request: {request.method} {request.path} "
                f"from {self.get_client_ip(request)} "
                f"[Status: {response.status_code}]"
            )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip
