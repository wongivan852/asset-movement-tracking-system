# Phase 1: SSO Integration Implementation Guide

**Project:** Asset Movement Tracking System
**Phase:** 1 - SSO Integration
**Duration:** 4-6 weeks
**Status:** In Progress
**Started:** November 20, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Decision](#architecture-decision)
3. [Implementation Steps](#implementation-steps)
4. [Configuration Guide](#configuration-guide)
5. [Testing Strategy](#testing-strategy)
6. [Rollback Plan](#rollback-plan)
7. [Security Considerations](#security-considerations)

---

## Overview

### Objectives

Implement Single Sign-On (SSO) authentication to enable seamless integration with the Integrated Business Platform while maintaining backward compatibility with existing Django authentication.

### Goals

- ✅ Enable OAuth 2.0 authentication
- ✅ Support SAML 2.0 as alternative
- ✅ Implement user auto-provisioning
- ✅ Map SSO roles to application roles
- ✅ Maintain backward compatibility
- ✅ Configure iframe embedding
- ✅ Enable CORS for API access

### Success Criteria

1. Users can authenticate via SSO provider
2. New users are automatically provisioned
3. Roles are correctly mapped from SSO
4. Existing Django admin accounts continue to work
5. Application can be embedded in iframe
6. API accepts cross-origin requests with proper authentication

---

## Architecture Decision

### Chosen Solution: Dual Authentication Backend

We will implement a **dual authentication system** that supports both:
1. **OAuth 2.0/OIDC** - For SSO integration with Integrated Business Platform
2. **Django Authentication** - For admin/local accounts (fallback)

### Why This Approach?

- ✅ Flexible - Supports multiple SSO providers
- ✅ Backward compatible - Existing accounts continue to work
- ✅ Secure - Industry-standard protocols
- ✅ Scalable - Easy to add more providers
- ✅ Modern - Token-based authentication for APIs

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| SSO Framework | django-allauth | OAuth/OIDC provider integration |
| API Auth | djangorestframework-simplejwt | JWT tokens for API |
| REST API | Django REST Framework | Comprehensive API endpoints |
| CORS | django-cors-headers | Cross-origin request handling |
| CSP | django-csp | Content Security Policy |

---

## Implementation Steps

### Week 1-2: Setup & Configuration

#### Step 1: Install Dependencies ✅

```bash
# Core SSO packages
pip install django-allauth==0.57.0
pip install djangorestframework==3.14.0
pip install djangorestframework-simplejwt==5.3.1

# CORS and Security
pip install django-cors-headers==4.3.1
pip install django-csp==3.8

# Additional utilities
pip install requests-oauthlib==1.3.1
```

#### Step 2: Update Django Settings ✅

**Add to INSTALLED_APPS:**
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required for allauth

    # Third-party apps
    'crispy_forms',
    'crispy_bootstrap5',
    'django_bootstrap5',

    # SSO and API
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'csp',

    # Local apps
    'accounts',
    'assets',
    'locations',
    'movements',
    'dashboard',
]
```

**Add Authentication Backends:**
```python
AUTHENTICATION_BACKENDS = [
    # Django default (for admin/local accounts)
    'django.contrib.auth.backends.ModelBackend',

    # OAuth/OIDC authentication
    'allauth.account.auth_backends.AuthenticationBackend',
]
```

#### Step 3: Configure Middleware ✅

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Add CORS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'csp.middleware.CSPMiddleware',  # Add CSP
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### Week 2-3: OAuth 2.0 Implementation

#### Step 4: Configure OAuth Provider ✅

**Generic OAuth 2.0 Configuration:**
```python
# settings.py

# Required for django-allauth
SITE_ID = 1

# OAuth Provider Configuration
SOCIALACCOUNT_PROVIDERS = {
    'openid_connect': {
        'APPS': [
            {
                'provider_id': 'integrated_platform',
                'name': 'Integrated Business Platform',
                'client_id': config('OAUTH_CLIENT_ID', default=''),
                'secret': config('OAUTH_CLIENT_SECRET', default=''),
                'settings': {
                    'server_url': config('OAUTH_SERVER_URL', default=''),
                },
            }
        ],
        'OAUTH_PKCE_ENABLED': True,
    }
}

# Allauth Configuration
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_USERNAME_REQUIRED = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'

# Redirect URLs
LOGIN_REDIRECT_URL = '/dashboard/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'
SOCIALACCOUNT_LOGIN_ON_GET = True
```

#### Step 5: URL Configuration ✅

```python
# asset_tracker/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Django-allauth URLs (includes OAuth callbacks)
    path('accounts/', include('allauth.urls')),

    # Original app URLs
    path('', include('dashboard.urls')),
    path('assets/', include('assets.urls')),
    path('locations/', include('locations.urls')),
    path('movements/', include('movements.urls')),

    # API URLs
    path('api/', include('api.urls')),  # New API routes
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### Week 3-4: User Auto-Provisioning

#### Step 6: Create SSO Signal Handlers ✅

**File: accounts/sso_handlers.py**
```python
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.socialaccount.signals import pre_social_login, social_account_added
from allauth.account.signals import user_signed_up
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(pre_social_login)
def link_to_local_user(sender, request, sociallogin, **kwargs):
    """
    Link social account to existing local account if email matches
    """
    if sociallogin.is_existing:
        return

    email = sociallogin.account.extra_data.get('email')
    if not email:
        return

    try:
        user = User.objects.get(email=email)
        sociallogin.connect(request, user)
        logger.info(f"Linked SSO account to existing user: {user.username}")
    except User.DoesNotExist:
        pass


@receiver(user_signed_up)
def populate_user_from_sso(sender, request, user, sociallogin=None, **kwargs):
    """
    Auto-provision user from SSO data
    """
    if not sociallogin:
        return

    extra_data = sociallogin.account.extra_data

    # Map basic user information
    user.first_name = extra_data.get('given_name', extra_data.get('first_name', ''))
    user.last_name = extra_data.get('family_name', extra_data.get('last_name', ''))
    user.email = extra_data.get('email', user.email)

    # Map custom fields
    user.employee_id = extra_data.get('employee_id', extra_data.get('employee_number', ''))
    user.phone = extra_data.get('phone', extra_data.get('phone_number', ''))
    user.department = extra_data.get('department', '')

    # Map role from SSO
    user.role = map_sso_role_to_app_role(extra_data)

    user.save()

    logger.info(f"Auto-provisioned user from SSO: {user.username} ({user.email})")


def map_sso_role_to_app_role(extra_data):
    """
    Map SSO roles to application roles

    SSO Role Mapping:
    - system_admin, admin, administrator -> admin
    - manager, location_manager, site_manager -> location_manager
    - user, employee, staff, personnel -> personnel

    Default: personnel
    """
    sso_roles = extra_data.get('roles', [])
    if isinstance(sso_roles, str):
        sso_roles = [sso_roles]

    # Also check single 'role' field
    if not sso_roles:
        role_field = extra_data.get('role', '').lower()
        if role_field:
            sso_roles = [role_field]

    # Role mapping
    role_mapping = {
        'system_admin': 'admin',
        'admin': 'admin',
        'administrator': 'admin',
        'manager': 'location_manager',
        'location_manager': 'location_manager',
        'site_manager': 'location_manager',
        'user': 'personnel',
        'employee': 'personnel',
        'staff': 'personnel',
        'personnel': 'personnel',
    }

    # Check each role in priority order
    for sso_role in sso_roles:
        app_role = role_mapping.get(sso_role.lower())
        if app_role:
            return app_role

    # Default to personnel
    return 'personnel'


@receiver(social_account_added)
def log_social_account_added(sender, request, sociallogin, **kwargs):
    """
    Log when a social account is added
    """
    logger.info(f"Social account added: {sociallogin.account.provider} for user {sociallogin.user.username}")
```

#### Step 7: Register Signal Handlers ✅

**File: accounts/apps.py**
```python
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import accounts.sso_handlers  # Register signal handlers
```

### Week 4-5: Security & Embedding

#### Step 8: Configure Iframe Embedding ✅

```python
# settings.py

# Modify X-Frame-Options for embedding
# Option 1: Same origin (if platform on same domain)
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Option 2: Specific domains (recommended)
# Remove X_FRAME_OPTIONS and use CSP instead

# Content Security Policy Configuration
CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = [
    "'self'",
    "'unsafe-inline'",  # Required for Bootstrap
    "https://cdn.jsdelivr.net",
    "https://cdnjs.cloudflare.com",
]
CSP_STYLE_SRC = [
    "'self'",
    "'unsafe-inline'",  # Required for Bootstrap
    "https://cdn.jsdelivr.net",
    "https://cdnjs.cloudflare.com",
]
CSP_IMG_SRC = ["'self'", "data:", "https:"]
CSP_FONT_SRC = ["'self'", "https://cdnjs.cloudflare.com"]
CSP_CONNECT_SRC = ["'self'"]

# Allow embedding from Integrated Business Platform
CSP_FRAME_ANCESTORS = [
    "'self'",
    config('PLATFORM_URL', default='https://integrated-platform.company.com'),
]
```

#### Step 9: Configure CORS ✅

```python
# settings.py

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    config('PLATFORM_URL', default='https://integrated-platform.company.com'),
]

# Allow credentials (cookies, auth headers)
CORS_ALLOW_CREDENTIALS = True

# Allowed methods
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Allowed headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Cache preflight requests for 1 hour
CORS_PREFLIGHT_MAX_AGE = 3600
```

### Week 5-6: REST API & JWT

#### Step 10: Configure REST Framework & JWT ✅

```python
# settings.py

from datetime import timedelta

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',
}
```

---

## Configuration Guide

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
TIME_ZONE=Asia/Hong_Kong

# Database Configuration
DB_NAME=asset_tracker
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# OAuth 2.0 / OIDC Configuration
OAUTH_CLIENT_ID=your-oauth-client-id
OAUTH_CLIENT_SECRET=your-oauth-client-secret
OAUTH_SERVER_URL=https://sso.integrated-platform.com

# Platform Integration
PLATFORM_URL=https://integrated-platform.company.com

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@company.com
EMAIL_HOST_PASSWORD=your-email-password
```

### SSO Provider Configuration

#### For OAuth 2.0 / OpenID Connect:

**Required Information from Integrated Business Platform:**
1. Client ID
2. Client Secret
3. Authorization URL
4. Token URL
5. User Info URL
6. Redirect URI (callback URL)

**Callback URL Format:**
```
https://your-asset-tracker.com/accounts/openid_connect/integrated_platform/login/callback/
```

#### SSO Claim Mapping:

| SSO Claim | Application Field | Required |
|-----------|-------------------|----------|
| `sub` or `user_id` | username | Yes |
| `email` | email | Yes |
| `given_name` | first_name | No |
| `family_name` | last_name | No |
| `employee_id` | employee_id | No |
| `department` | department | No |
| `phone` | phone | No |
| `roles` or `role` | role (mapped) | No |

---

## Testing Strategy

### Unit Tests

**File: accounts/tests/test_sso.py**

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.sso_handlers import map_sso_role_to_app_role

User = get_user_model()


class SSOIntegrationTests(TestCase):

    def test_role_mapping_admin(self):
        """Test that admin roles are mapped correctly"""
        extra_data = {'role': 'admin'}
        role = map_sso_role_to_app_role(extra_data)
        self.assertEqual(role, 'admin')

    def test_role_mapping_manager(self):
        """Test that manager roles are mapped correctly"""
        extra_data = {'role': 'manager'}
        role = map_sso_role_to_app_role(extra_data)
        self.assertEqual(role, 'location_manager')

    def test_role_mapping_default(self):
        """Test that unknown roles default to personnel"""
        extra_data = {'role': 'unknown_role'}
        role = map_sso_role_to_app_role(extra_data)
        self.assertEqual(role, 'personnel')

    def test_role_mapping_multiple_roles(self):
        """Test that multiple roles return highest priority"""
        extra_data = {'roles': ['user', 'admin']}
        role = map_sso_role_to_app_role(extra_data)
        self.assertEqual(role, 'admin')
```

### Integration Testing

**Manual Test Checklist:**

- [ ] SSO login redirects to OAuth provider
- [ ] After authentication, user is redirected back to application
- [ ] New user is created with correct data
- [ ] User role is correctly mapped
- [ ] Existing user with same email is linked (not duplicated)
- [ ] Django admin login still works
- [ ] Logout works correctly
- [ ] Application works in iframe
- [ ] API accepts JWT tokens
- [ ] CORS allows requests from platform

---

## Rollback Plan

### If SSO Implementation Fails:

1. **Disable SSO in settings:**
   ```python
   # Comment out in AUTHENTICATION_BACKENDS
   # 'allauth.account.auth_backends.AuthenticationBackend',
   ```

2. **Revert URL configuration:**
   ```python
   # Comment out allauth URLs
   # path('accounts/', include('allauth.urls')),

   # Restore original accounts URLs
   path('accounts/', include('accounts.urls')),
   ```

3. **Keep packages installed but inactive**
   - No need to uninstall packages
   - Just disable in settings

4. **Database migrations are safe**
   - Allauth creates its own tables
   - Original User model unchanged

---

## Security Considerations

### Authentication Security

1. **Always use HTTPS in production**
   - Set `SECURE_SSL_REDIRECT = True`
   - Set `SESSION_COOKIE_SECURE = True`
   - Set `CSRF_COOKIE_SECURE = True`

2. **Validate OAuth tokens**
   - Use PKCE flow for OAuth 2.0
   - Verify token signatures
   - Check token expiration

3. **Session security**
   - Set reasonable session timeout
   - Use secure session cookies
   - Implement CSRF protection

### API Security

1. **JWT token security**
   - Short access token lifetime (1 hour)
   - Rotating refresh tokens
   - Token blacklist on logout

2. **CORS security**
   - Only allow specific origins
   - Don't use wildcard (`*`)
   - Validate credentials

3. **Rate limiting**
   - Implement for API endpoints
   - Protect against brute force

### Iframe Security

1. **CSP configuration**
   - Specify allowed frame ancestors
   - Don't allow all origins

2. **Clickjacking protection**
   - Use CSP frame-ancestors
   - Or use X-Frame-Options: SAMEORIGIN

---

## Next Steps

After Phase 1 completion:

1. **Phase 2:** API Enhancement (3-4 weeks)
   - Implement comprehensive REST API
   - Add API documentation (Swagger)
   - Create API versioning

2. **Phase 3:** Embedding Configuration (2-3 weeks)
   - UI/UX adjustments for embedded view
   - Navigation integration
   - Shared session management

3. **Phase 4:** Production Deployment (2 weeks)
   - Production server setup
   - Monitoring and logging
   - Performance optimization

---

## Support & Documentation

### Useful Links

- Django-allauth docs: https://django-allauth.readthedocs.io/
- Django REST Framework: https://www.django-rest-framework.org/
- JWT Authentication: https://django-rest-framework-simplejwt.readthedocs.io/
- CORS Headers: https://github.com/adamchainz/django-cors-headers

### Team Contacts

- **Technical Lead:** [Your Name]
- **Platform Team:** [Platform Team Contact]
- **Security Team:** [Security Team Contact]

---

**Document Version:** 1.0
**Last Updated:** November 20, 2025
**Next Review:** Upon Phase 1 completion
