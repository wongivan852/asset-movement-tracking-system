# Business Platform API Setup Guide
## For Asset Management Integration (Remote API Mode)

This guide provides the exact code to add to your Business Platform to enable Asset Management System integration.

---

## 🔑 Generated API Key

**Save this securely!**

```
API Key: qLzxsUsGic0ANefhzeXilZj9pPxyygJsr48V8SGBhiU
```

You'll need this in both applications.

---

## 📝 Changes to Business Platform

### Step 1: Add API Views

Create a new file or add to existing views: `api_views.py` or `views.py`

```python
# ============================================================================
# File: api_views.py (or add to existing views.py)
# Location: In your Business Platform app
# ============================================================================

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@csrf_exempt  # API uses Bearer token authentication
@require_http_methods(["GET"])
def validate_session(request):
    """
    API endpoint to validate session and return user info

    Used by Asset Management System to verify user authentication

    Request:
        GET /api/auth/validate/
        Headers:
            Cookie: sessionid=<session_key>
            Authorization: Bearer <api_key>

    Response 200:
        {
            "id": 123,
            "username": "john.doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "is_active": true,
            "role": "admin",
            "department": "IT"
        }

    Response 401:
        {"error": "Invalid API key"}
        {"error": "Not authenticated"}
    """
    # Verify API key
    api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
    expected_api_key = getattr(settings, 'ASSET_MANAGEMENT_API_KEY', '')

    if not expected_api_key:
        logger.error("ASSET_MANAGEMENT_API_KEY not configured in settings")
        return JsonResponse({'error': 'API not configured'}, status=500)

    if api_key != expected_api_key:
        logger.warning(f"Invalid API key attempt from {request.META.get('REMOTE_ADDR')}")
        return JsonResponse({'error': 'Invalid API key'}, status=401)

    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    # Log successful validation
    logger.info(f"Session validated for user: {request.user.username}")

    # Return user data
    user_data = {
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'is_active': request.user.is_active,
        'is_staff': request.user.is_staff,
        'is_superuser': request.user.is_superuser,
    }

    # Add custom fields if they exist on your User model
    if hasattr(request.user, 'role'):
        user_data['role'] = request.user.role

    if hasattr(request.user, 'department'):
        user_data['department'] = request.user.department

    if hasattr(request.user, 'employee_id'):
        user_data['employee_id'] = request.user.employee_id

    if hasattr(request.user, 'phone'):
        user_data['phone'] = request.user.phone

    return JsonResponse(user_data)


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """
    Optional: API login endpoint

    Allows Asset Management System to validate credentials directly

    Request:
        POST /api/auth/login/
        Content-Type: application/json
        {
            "username": "john.doe",
            "password": "password123"
        }

    Response 200:
        {
            "id": 123,
            "username": "john.doe",
            "email": "john@example.com",
            ...
        }

    Response 401:
        {"error": "Invalid credentials"}
    """
    import json
    from django.contrib.auth import authenticate

    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Username and password required'}, status=400)

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active:
            logger.info(f"API login successful for user: {username}")

            # Return user data (same as validate_session)
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
            }

            # Add custom fields
            if hasattr(user, 'role'):
                user_data['role'] = user.role
            if hasattr(user, 'department'):
                user_data['department'] = user.department

            return JsonResponse(user_data)
        else:
            logger.warning(f"Failed API login attempt for username: {username}")
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"API login error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_health(request):
    """
    Health check endpoint

    Request:
        GET /api/auth/health/

    Response 200:
        {
            "status": "ok",
            "service": "Business Platform Auth API",
            "version": "1.0.0"
        }
    """
    return JsonResponse({
        'status': 'ok',
        'service': 'Business Platform Auth API',
        'version': '1.0.0'
    })
```

---

### Step 2: Add URL Patterns

Add to your Business Platform's `urls.py`:

```python
# ============================================================================
# File: urls.py
# Location: Your Business Platform project
# ============================================================================

from django.urls import path
# Import the views you created above
from . import api_views  # or wherever you put the views

urlpatterns = [
    # ... your existing URL patterns ...

    # Asset Management API endpoints
    path('api/auth/validate/', api_views.validate_session, name='api_validate_session'),
    path('api/auth/login/', api_views.api_login, name='api_login'),
    path('api/auth/health/', api_views.api_health, name='api_health'),
]
```

---

### Step 3: Add Settings

Add to your Business Platform's `settings.py`:

```python
# ============================================================================
# File: settings.py
# Location: Your Business Platform project
# ============================================================================

# Asset Management API Configuration
ASSET_MANAGEMENT_API_KEY = 'qLzxsUsGic0ANefhzeXilZj9pPxyygJsr48V8SGBhiU'

# Optional: Configure CORS if Asset Management is on different domain
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://your-asset-management-server:8000',
]

CORS_ALLOW_CREDENTIALS = True
```

---

### Step 4: Install Dependencies (if needed)

If you don't have CORS headers package:

```bash
# In Business Platform directory
pip install django-cors-headers
```

Then add to `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'corsheaders',
    # ...
]

MIDDLEWARE = [
    # ...
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ...
]
```

---

## 🧪 Testing Business Platform API

After making these changes, test the API:

### Test 1: Health Check

```bash
curl http://192.168.0.104:8000/api/auth/health/
```

Expected response:
```json
{
  "status": "ok",
  "service": "Business Platform Auth API",
  "version": "1.0.0"
}
```

### Test 2: Session Validation

First, login to Business Platform and get session cookie:

```bash
# Login (this will save cookies to cookies.txt)
curl -c cookies.txt -X POST http://192.168.0.104:8000/auth/login/ \
  -d "username=testuser&password=testpass"

# Test validation endpoint
curl -b cookies.txt \
  -H "Authorization: Bearer qLzxsUsGic0ANefhzeXilZj9pPxyygJsr48V8SGBhiU" \
  http://192.168.0.104:8000/api/auth/validate/
```

Expected response:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "User",
  "is_active": true,
  "role": "admin"
}
```

### Test 3: API Login

```bash
curl -X POST http://192.168.0.104:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
```

Expected response:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  ...
}
```

---

## 🔒 Security Considerations

### 1. API Key Storage

**NEVER** commit the API key to version control!

Use environment variables:

```python
# In settings.py
import os
from decouple import config  # or use python-decouple

ASSET_MANAGEMENT_API_KEY = config('ASSET_MANAGEMENT_API_KEY')
```

Create `.env` file:
```bash
ASSET_MANAGEMENT_API_KEY=qLzxsUsGic0ANefhzeXilZj9pPxyygJsr48V8SGBhiU
```

Add `.env` to `.gitignore`:
```
.env
```

### 2. Rate Limiting

Consider adding rate limiting to prevent abuse:

```python
# Using django-ratelimit
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h')
@csrf_exempt
@require_http_methods(["GET"])
def validate_session(request):
    # ... existing code ...
```

### 3. IP Whitelisting (Optional)

Restrict API access to Asset Management server IP:

```python
ALLOWED_API_IPS = ['192.168.0.105', '127.0.0.1']  # Asset Management server

def validate_session(request):
    # Check IP
    client_ip = request.META.get('REMOTE_ADDR')
    if client_ip not in settings.ALLOWED_API_IPS:
        return JsonResponse({'error': 'Unauthorized IP'}, status=403)

    # ... rest of code ...
```

### 4. HTTPS in Production

**Always use HTTPS in production!**

Update CORS settings:
```python
CORS_ALLOWED_ORIGINS = [
    'https://asset-management.yourdomain.com',
]
```

---

## 📊 Monitoring & Logging

The API views include logging. Monitor these logs:

```python
# Check logs for:
- "Session validated for user: ..." (successful validations)
- "Invalid API key attempt from ..." (security alerts)
- "Failed API login attempt for username: ..." (failed logins)
```

Setup log rotation:

```python
# In settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/business-platform/api.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'api_views': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

---

## ✅ Deployment Checklist

Before deploying to production:

- [ ] API key stored in environment variable (not hardcoded)
- [ ] `.env` file added to `.gitignore`
- [ ] CORS configured for production domain
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Logging configured and monitored
- [ ] Health check endpoint tested
- [ ] Session validation tested
- [ ] Error handling tested
- [ ] Documentation updated

---

## 🆘 Troubleshooting

### Issue: 401 Unauthorized

**Cause**: Invalid API key

**Fix**: Verify API key matches in both applications

### Issue: CORS Error

**Cause**: Asset Management domain not in CORS_ALLOWED_ORIGINS

**Fix**: Add domain to `CORS_ALLOWED_ORIGINS` in settings

### Issue: Session Not Found

**Cause**: Session expired or cookie not sent

**Fix**: Check cookie settings, ensure `CORS_ALLOW_CREDENTIALS = True`

---

## 🎯 Summary

**What you added to Business Platform:**
1. ✅ 3 API endpoints (validate, login, health)
2. ✅ 1 setting (ASSET_MANAGEMENT_API_KEY)
3. ✅ CORS configuration

**Impact:**
- ✅ Minimal code change (~100 lines)
- ✅ No database modifications
- ✅ No impact on other apps
- ✅ Can be disabled anytime

**Next Steps:**
1. Add the code above to Business Platform
2. Test the API endpoints
3. Configure Asset Management (see next document)
4. Test end-to-end integration

---

**API Key (save this):** `qLzxsUsGic0ANefhzeXilZj9pPxyygJsr48V8SGBhiU`
