"""
Embedded Mode Middleware - Phase 3

Detects when the application is running in embedded mode (iframe) and
provides context variables for template rendering and session management.
"""

import json
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class EmbeddedModeMiddleware(MiddlewareMixin):
    """
    Middleware to detect and handle embedded mode requests.

    Features:
    - Detects iframe embedding
    - Provides embedded mode context to templates
    - Handles session token from parent platform
    - Supports custom theming from parent platform
    """

    def process_request(self, request):
        """
        Process incoming request to detect embedded mode.
        """
        # Check if request is from iframe
        is_embedded = self._is_embedded(request)

        # Add embedded mode flag to request
        request.is_embedded = is_embedded

        # Handle session synchronization if enabled
        if is_embedded and getattr(settings, 'EMBEDDED_SESSION_SYNC_ENABLED', True):
            self._sync_session(request)

        # Handle theme synchronization if enabled
        if is_embedded and getattr(settings, 'EMBEDDED_THEME_SYNC_ENABLED', True):
            request.embedded_theme = self._get_theme_config(request)

    def process_template_response(self, request, response):
        """
        Add embedded mode context variables to template response.
        """
        if hasattr(response, 'context_data'):
            # Add embedded mode flag
            response.context_data['is_embedded'] = getattr(request, 'is_embedded', False)

            # Add embedded mode type (normal, minimal, no-nav)
            response.context_data['embedded_mode'] = request.GET.get('embedded', 'normal')

            # Add platform origin for PostMessage security
            platform_origin = getattr(settings, 'PLATFORM_URL', None)
            response.context_data['platform_origin'] = platform_origin

            # Add custom theme configuration
            if hasattr(request, 'embedded_theme'):
                response.context_data['custom_theme'] = request.embedded_theme

            # Add debug flag
            response.context_data['debug_embedded'] = request.GET.get('debug_embedded', 'false')

        return response

    def _is_embedded(self, request):
        """
        Detect if request is from an embedded iframe.

        Detection methods:
        1. Check for 'embedded' query parameter
        2. Check for custom header from parent platform
        3. Check Referer header (less reliable)
        """
        # Method 1: Check query parameter
        if 'embedded' in request.GET:
            return True

        # Method 2: Check custom header from parent platform
        if request.headers.get('X-Embedded-Mode') == 'true':
            return True

        # Method 3: Check for platform session token (indicates SSO from platform)
        if 'platform_session_token' in request.GET:
            return True

        # Method 4: Check Referer header (less reliable due to privacy)
        referer = request.headers.get('Referer', '')
        platform_url = getattr(settings, 'PLATFORM_URL', None)
        if platform_url and referer.startswith(platform_url):
            return True

        return False

    def _sync_session(self, request):
        """
        Synchronize session with parent platform.

        Handles platform session token and user data synchronization.
        """
        # Get platform session token from query parameter
        platform_token = request.GET.get('platform_session_token')

        if platform_token:
            # Store in session for later use
            request.session['platform_session_token'] = platform_token

            # Optionally validate token with platform API
            if getattr(settings, 'EMBEDDED_VALIDATE_PLATFORM_TOKEN', False):
                self._validate_platform_token(request, platform_token)

    def _validate_platform_token(self, request, token):
        """
        Validate platform session token with parent platform API.

        This is an optional security enhancement that verifies the
        session token with the parent platform before trusting it.
        """
        import requests
        from django.core.cache import cache

        # Check cache first to avoid repeated API calls
        cache_key = f'platform_token_{token[:20]}'
        cached_result = cache.get(cache_key)

        if cached_result is not None:
            return cached_result

        # Get platform API URL from settings
        platform_api_url = getattr(settings, 'PLATFORM_TOKEN_VALIDATION_URL', None)

        if not platform_api_url:
            return False

        try:
            # Call platform API to validate token
            response = requests.post(
                platform_api_url,
                json={'token': token},
                timeout=5
            )

            is_valid = response.status_code == 200 and response.json().get('valid', False)

            # Cache result for 5 minutes
            cache.set(cache_key, is_valid, 300)

            return is_valid

        except Exception as e:
            # Log error but don't fail the request
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error validating platform token: {e}')
            return False

    def _get_theme_config(self, request):
        """
        Extract theme configuration from request.

        Theme can be provided via:
        1. Query parameters
        2. HTTP headers
        3. Session storage (from previous sync)
        """
        theme = {}

        # Get theme from query parameters
        theme_params = ['primary_color', 'secondary_color', 'navbar_bg', 'body_bg']

        for param in theme_params:
            value = request.GET.get(param)
            if value:
                theme[param] = value

        # Get theme from custom header (JSON encoded)
        theme_header = request.headers.get('X-Embedded-Theme')
        if theme_header:
            try:
                header_theme = json.loads(theme_header)
                theme.update(header_theme)
            except json.JSONDecodeError:
                pass

        # Get theme from session (previously synced)
        session_theme = request.session.get('embedded_theme')
        if session_theme:
            # Session theme is lower priority than request theme
            for key, value in session_theme.items():
                if key not in theme:
                    theme[key] = value

        # Store current theme in session for future requests
        if theme:
            request.session['embedded_theme'] = theme

        return theme if theme else None


class EmbeddedSecurityMiddleware(MiddlewareMixin):
    """
    Security middleware for embedded mode.

    Provides additional security checks when running in embedded mode:
    - Validates platform origin
    - Enforces HTTPS in production
    - Adds security headers for iframe embedding
    """

    def process_request(self, request):
        """
        Perform security checks for embedded mode.
        """
        is_embedded = getattr(request, 'is_embedded', False)

        if not is_embedded:
            return None

        # In production, enforce HTTPS for embedded mode
        if not settings.DEBUG and not request.is_secure():
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden(
                'Embedded mode requires HTTPS in production'
            )

        # Validate platform origin if configured
        if getattr(settings, 'EMBEDDED_VALIDATE_ORIGIN', True):
            if not self._validate_origin(request):
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden(
                    'Access from this origin is not allowed'
                )

        return None

    def process_response(self, request, response):
        """
        Add security headers for embedded mode.
        """
        is_embedded = getattr(request, 'is_embedded', False)

        if is_embedded:
            # Add Permissions-Policy header to control features in iframe
            permissions = getattr(settings, 'EMBEDDED_PERMISSIONS_POLICY', {
                'camera': '()',
                'microphone': '()',
                'geolocation': '()',
                'payment': '()',
            })

            if permissions:
                policy_str = ', '.join([f'{k}={v}' for k, v in permissions.items()])
                response['Permissions-Policy'] = policy_str

            # Add Referrer-Policy for privacy
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        return response

    def _validate_origin(self, request):
        """
        Validate that the request is coming from an allowed origin.
        """
        # Get allowed origins from settings
        allowed_origins = getattr(settings, 'EMBEDDED_ALLOWED_ORIGINS', [])

        if not allowed_origins:
            # If no origins configured, allow all (not recommended for production)
            return True

        # Check Referer header
        referer = request.headers.get('Referer', '')

        if not referer:
            # No referer, might be direct access or privacy settings
            # Allow if EMBEDDED_ALLOW_NO_REFERER is True
            return getattr(settings, 'EMBEDDED_ALLOW_NO_REFERER', False)

        # Check if referer starts with any allowed origin
        for origin in allowed_origins:
            if referer.startswith(origin):
                return True

        return False
