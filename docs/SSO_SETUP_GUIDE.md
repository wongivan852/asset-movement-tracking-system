# SSO Setup Guide - Asset Movement Tracking System

**Quick Start Guide for Phase 1 SSO Integration**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [SSO Provider Setup](#sso-provider-setup)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

## Prerequisites

Before setting up SSO, ensure you have:

- [x] Python 3.8 or higher installed
- [x] PostgreSQL (for production) or SQLite (for development)
- [x] Access to your SSO provider's admin console
- [x] OAuth 2.0 Client ID and Secret from your SSO provider
- [x] Network access to your SSO provider's endpoints

---

## Installation

### Step 1: Install Dependencies

```bash
# Create and activate virtual environment (if not already done)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies including SSO packages
pip install -r requirements.txt
```

**What gets installed:**
- `django-allauth` - SSO authentication framework
- `djangorestframework` - REST API support
- `djangorestframework-simplejwt` - JWT token authentication
- `django-cors-headers` - Cross-origin resource sharing
- `django-csp` - Content Security Policy

### Step 2: Create Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

### Step 3: Run Migrations

```bash
# Create database tables for allauth
python manage.py migrate

# Create logs directory
mkdir -p logs
```

### Step 4: Create Django Sites Entry

```bash
# Open Django shell
python manage.py shell

# Run this Python code
from django.contrib.sites.models import Site
site = Site.objects.get(pk=1)
site.domain = 'your-domain.com'  # Change to your actual domain
site.name = 'Asset Tracker'
site.save()
exit()
```

Or for localhost development:

```python
site.domain = 'localhost:8000'
site.name = 'Asset Tracker (Development)'
```

---

## Configuration

### Option A: OpenID Connect (OIDC) - Recommended

**Best for:** Azure AD, Okta, Auth0, Keycloak, Google

**Edit .env file:**

```bash
OAUTH_CLIENT_ID=your-client-id-here
OAUTH_CLIENT_SECRET=your-client-secret-here
OAUTH_SERVER_URL=https://your-sso-provider.com

# Example for Azure AD:
# OAUTH_SERVER_URL=https://login.microsoftonline.com/your-tenant-id/v2.0

# Example for Okta:
# OAUTH_SERVER_URL=https://your-domain.okta.com

# Example for Keycloak:
# OAUTH_SERVER_URL=https://keycloak.com/realms/your-realm
```

### Option B: Generic OAuth 2.0

**Best for:** Custom OAuth providers, legacy systems

1. **Edit `asset_tracker/settings.py`:**

Comment out the OIDC configuration (lines 287-302) and uncomment the OAuth 2.0 section (lines 304-321):

```python
# Comment this out:
# SOCIALACCOUNT_PROVIDERS = {
#     'openid_connect': { ... }
# }

# Uncomment this:
SOCIALACCOUNT_PROVIDERS = {
    'oauth2': {
        'APPS': [
            {
                'client_id': config('OAUTH_CLIENT_ID', default=''),
                'secret': config('OAUTH_CLIENT_SECRET', default=''),
                'key': '',
                'settings': {
                    'authorize_url': config('OAUTH_AUTHORIZE_URL', default=''),
                    'access_token_url': config('OAUTH_TOKEN_URL', default=''),
                    'profile_url': config('OAUTH_PROFILE_URL', default=''),
                }
            }
        ]
    }
}
```

2. **Edit .env file:**

```bash
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_AUTHORIZE_URL=https://sso.example.com/oauth/authorize
OAUTH_TOKEN_URL=https://sso.example.com/oauth/token
OAUTH_PROFILE_URL=https://sso.example.com/oauth/userinfo
```

### Platform URL Configuration

```bash
# Set the URL of the Integrated Business Platform
PLATFORM_URL=https://integrated-platform.company.com
```

This is used for:
- CORS (allowing API requests from the platform)
- CSP (allowing iframe embedding)

---

## SSO Provider Setup

### 1. Register Application with SSO Provider

Log in to your SSO provider's admin console and create a new application/client.

**Application Settings:**

| Setting | Value |
|---------|-------|
| Application Name | Asset Movement Tracking System |
| Application Type | Web Application |
| Grant Type | Authorization Code |
| PKCE | Enabled (recommended) |

### 2. Configure Redirect URIs

**For Production:**
```
https://your-domain.com/accounts/openid_connect/integrated_platform/login/callback/
```

**For Development:**
```
http://localhost:8000/accounts/openid_connect/integrated_platform/login/callback/
```

**Logout Redirect URI:**
```
https://your-domain.com/accounts/login/
```

### 3. Configure Scopes

Request these scopes from your SSO provider:

- `openid` - Required for OIDC
- `profile` - For user profile information
- `email` - For user email address

### 4. Configure Claims/Attributes

Ensure your SSO provider sends these claims in the ID token:

**Required:**
- `sub` or `user_id` - Unique user identifier
- `email` - User's email address

**Optional but recommended:**
- `given_name` - First name
- `family_name` - Last name
- `employee_id` - Employee ID
- `department` - Department name
- `phone` - Phone number
- `role` or `roles` - User role(s)

### 5. Role Mapping

Configure your SSO provider to send roles in one of these formats:

**Single role (string):**
```json
{
  "role": "admin"
}
```

**Multiple roles (array):**
```json
{
  "roles": ["user", "manager"]
}
```

**Supported role values:**

| SSO Role | Application Role | Permissions |
|----------|-----------------|-------------|
| `admin`, `administrator`, `system_admin` | Administrator | Full system access |
| `manager`, `location_manager`, `site_manager` | Location Manager | Location & staff management |
| `user`, `employee`, `staff`, `personnel` | Personnel | Basic operations |
| Any other value | Personnel | Basic operations (default) |

---

## Testing

### 1. Start Development Server

```bash
python manage.py runserver
```

### 2. Test Local Authentication

**Verify Django authentication still works:**

1. Go to: http://localhost:8000/admin/
2. Login with Django superuser credentials
3. Should work normally

### 3. Test SSO Authentication

**Option A: Manual Testing**

1. Go to: http://localhost:8000/accounts/login/
2. You should see "Sign in with Integrated Business Platform" button
3. Click the button
4. You'll be redirected to your SSO provider
5. Login with SSO credentials
6. You'll be redirected back to the application
7. Check that:
   - New user was created
   - User information is correct
   - Role is correctly assigned
   - Redirected to dashboard

**Option B: Direct SSO Link**

Go directly to:
```
http://localhost:8000/accounts/openid_connect/integrated_platform/login/
```

### 4. Test User Auto-Provisioning

1. Login with a new SSO user (never logged in before)
2. Check Django admin: http://localhost:8000/admin/accounts/user/
3. Verify:
   - User was created automatically
   - Email, name populated correctly
   - Employee ID set (if provided by SSO)
   - Role assigned based on SSO role

### 5. Test API Authentication

**Get JWT Token:**

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your-username", "password": "your-password"}'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Use Token:**

```bash
curl http://localhost:8000/dashboard/api/stats/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### 6. Test Iframe Embedding

Create a test HTML file:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Embed Test</title>
</head>
<body>
    <h1>Asset Tracker Embedded</h1>
    <iframe
        src="http://localhost:8000/"
        width="100%"
        height="800"
        frameborder="0">
    </iframe>
</body>
</html>
```

Open this file in a browser and verify the application loads in the iframe.

---

## Troubleshooting

### Issue: "Site matching query does not exist"

**Solution:**
```bash
python manage.py shell
from django.contrib.sites.models import Site
Site.objects.create(pk=1, domain='localhost:8000', name='Asset Tracker')
```

### Issue: "Refused to display in a frame"

**Check:**
1. `X_FRAME_OPTIONS = 'SAMEORIGIN'` in settings.py (line 208)
2. `CSP_FRAME_ANCESTORS` includes your platform URL (line 411)

**Solution:**
```python
# settings.py
X_FRAME_OPTIONS = 'SAMEORIGIN'
CSP_FRAME_ANCESTORS = ["'self'", "https://your-platform.com"]
```

### Issue: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Check:**
1. `PLATFORM_URL` in .env file
2. `CORS_ALLOWED_ORIGINS` in settings.py (line 332)

**Solution:**
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    'https://your-platform.com',
]
CORS_ALLOW_CREDENTIALS = True
```

### Issue: SSO login redirects but no user created

**Check logs:**
```bash
tail -f logs/django.log
```

**Common causes:**
1. SSO provider not sending required claims (email, sub)
2. Signal handlers not registered (check accounts/apps.py)
3. Error in role mapping (check sso_handlers.py)

**Debug:**
```bash
# Enable debug logging for accounts app
# settings.py - already configured to use DEBUG level when DEBUG=True
DEBUG=True
```

### Issue: "Invalid client_id or client_secret"

**Check:**
1. OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET in .env
2. Credentials match those in SSO provider console
3. No extra spaces or quotes in .env file

### Issue: JWT token authentication not working

**Check:**
1. Token included in Authorization header: `Bearer <token>`
2. Token not expired (1 hour lifetime)
3. REST_FRAMEWORK settings configured (lines 422-447)

**Test token:**
```bash
curl http://localhost:8000/api/token/verify/ \
  -H "Content-Type: application/json" \
  -d '{"token": "your-access-token"}'
```

---

## FAQ

### Q: Can I use both SSO and local Django authentication?

**A:** Yes! The system supports dual authentication:
- SSO users: Login via "Sign in with Integrated Business Platform"
- Local users: Login at /admin/ with Django credentials

### Q: How do I disable SSO temporarily?

**A:** Comment out the allauth authentication backend in settings.py:

```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # 'allauth.account.auth_backends.AuthenticationBackend',  # Commented out
]
```

### Q: Can I customize the role mapping?

**A:** Yes! Edit `accounts/sso_handlers.py`, function `map_sso_role_to_app_role()` (lines 87-145).

Add your custom role mappings to the `role_mapping` dictionary:

```python
role_mapping = {
    'custom_role': 'location_manager',  # Add your mappings here
    'admin': 'admin',
    ...
}
```

### Q: How do I sync user data on each login?

**A:** Uncomment the `update_user_on_login` signal handler in `accounts/sso_handlers.py` (lines 222-227):

```python
@receiver(post_social_login)
def update_user_on_login(sender, request, sociallogin, **kwargs):
    """Update user data from SSO on each login"""
    user = sociallogin.user
    extra_data = sociallogin.account.extra_data
    sync_user_from_sso(user, extra_data)
```

### Q: Can I use SAML instead of OAuth?

**A:** The current implementation supports OAuth 2.0/OIDC. For SAML:

1. Install: `pip install python3-saml django-saml2-auth`
2. Follow SAML configuration in VALIDATION_REPORT.md section 11.2
3. Replace allauth with django-saml2-auth

### Q: How do I configure for multiple SSO providers?

**A:** Add multiple provider configurations in `SOCIALACCOUNT_PROVIDERS`:

```python
SOCIALACCOUNT_PROVIDERS = {
    'openid_connect': {
        'APPS': [
            {
                'provider_id': 'platform1',
                'name': 'Platform 1',
                'client_id': config('OAUTH1_CLIENT_ID'),
                'secret': config('OAUTH1_CLIENT_SECRET'),
                'settings': {'server_url': config('OAUTH1_SERVER_URL')},
            },
            {
                'provider_id': 'platform2',
                'name': 'Platform 2',
                'client_id': config('OAUTH2_CLIENT_ID'),
                'secret': config('OAUTH2_CLIENT_SECRET'),
                'settings': {'server_url': config('OAUTH2_SERVER_URL')},
            }
        ],
    }
}
```

### Q: Where are SSO sessions stored?

**A:** Sessions are stored in Django's session framework (database by default). Configure in settings.py:

```python
# Use database sessions (default)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Or use cache sessions (faster)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
```

---

## Next Steps

After successfully setting up SSO:

1. **Phase 2:** Implement comprehensive REST API
   - See `docs/PHASE2_API_IMPLEMENTATION.md` (coming soon)

2. **Phase 3:** UI/UX adjustments for embedded view
   - Customize navigation for embedded mode
   - Implement shared session with platform

3. **Phase 4:** Production deployment
   - Enable HTTPS security settings
   - Configure production SSO endpoints
   - Set up monitoring and logging

---

## Support

For issues or questions:

1. Check logs: `tail -f logs/django.log`
2. Review: `docs/VALIDATION_REPORT.md`
3. See: `docs/PHASE1_SSO_IMPLEMENTATION.md`

---

**Document Version:** 1.0
**Last Updated:** November 20, 2025
