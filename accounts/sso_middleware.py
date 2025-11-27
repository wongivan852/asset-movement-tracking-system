"""
SSO Auto-login Middleware
Automatically logs in users when they arrive with a valid SSO token
"""
from django.contrib.auth import login, get_user_model
from django.shortcuts import redirect
from .sso import SSOTokenManager
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class SSOAutoLoginMiddleware:
    """Middleware to handle SSO token auto-login"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check for SSO token in URL parameters
        sso_token = request.GET.get('sso_token')
        
        if sso_token and not request.user.is_authenticated:
            try:
                # Validate the SSO token
                payload = SSOTokenManager.validate_token(sso_token, request)
                
                # Get the user
                username = payload.get('username')
                
                try:
                    user = User.objects.get(username=username)
                    
                    # Log the user in
                    # Set backend attribute required by Django auth
                    user.backend = 'accounts.auth_backends.BusinessPlatformAuthBackend'
                    login(request, user)
                    
                    logger.info(f"SSO auto-login successful for user: {username}")
                    
                    # Redirect to clean URL without token (root path)
                    return redirect('/')
                    
                except User.DoesNotExist:
                    logger.warning(f"SSO token valid but user not found: {username}")
                    # Continue to normal flow - user will see login page
                    
            except Exception as e:
                logger.error(f"SSO auto-login failed: {str(e)}")
                # Continue to normal flow on error
        
        response = self.get_response(request)
        return response
