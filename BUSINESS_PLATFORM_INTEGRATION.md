# Business Platform Integration Guide
## Shared Django Backend Authentication

This guide explains how to integrate the Asset Management System with your existing Business Platform running at `http://192.168.0.104:8000`.

---

## Overview

The Asset Management System can share authentication with your Business Platform, allowing users to:
- ✅ Login once on Business Platform
- ✅ Access Asset Management System without logging in again
- ✅ Maintain single user session across both applications

---

## Integration Modes

### Mode 1: Shared Database (Recommended)

Both applications connect to the same PostgreSQL database and share:
- User table (`accounts_user`)
- Session table (`django_session`)
- Same Django SECRET_KEY

**Pros:**
- Simple configuration
- No API calls needed
- Instant session sharing
- No latency

**Cons:**
- Both apps must access same database
- Requires database network access

### Mode 2: Remote API Validation

Asset Management System validates sessions via Business Platform API.

**Pros:**
- Apps can use different databases
- Better separation of concerns
- More secure (API key required)

**Cons:**
- Requires API endpoint on Business Platform
- Slight latency for validation
- Depends on Business Platform availability

---

## Setup Instructions

### Prerequisites

Before configuring, you need to know:

1. **Business Platform Database Connection**:
   - Host: `_________________`
   - Port: `5432` (default PostgreSQL)
   - Database name: `_________________`
   - Username: `_________________`
   - Password: `_________________`

2. **Business Platform Configuration**:
   - Django SECRET_KEY: `_________________`
   - SESSION_COOKIE_NAME: `sessionid` (default)
   - SESSION_COOKIE_DOMAIN: `_________________` (if sharing cookies)

3. **Integration Mode**:
   - [ ] Shared Database
   - [ ] Remote API

---

## Configuration

### Step 1: Update `.env` File

Edit `/home/user/asset-movement-tracking-system/.env`:

#### For Shared Database Mode:

```bash
# ========================================
# Business Platform Integration
# ========================================

# Enable Business Platform integration
BUSINESS_PLATFORM_ENABLED=True
BUSINESS_PLATFORM_URL=http://192.168.0.104:8000

# Integration Mode: database or api
BUSINESS_PLATFORM_MODE=database

# ========================================
# Shared Database Configuration
# ========================================
# Use the SAME database as Business Platform

DB_NAME=business_platform_db
DB_USER=business_platform_user
DB_PASSWORD=your_shared_db_password
DB_HOST=192.168.0.104
DB_PORT=5432

# ========================================
# Shared Django Configuration
# ========================================
# CRITICAL: Must match Business Platform settings

# Use the SAME SECRET_KEY as Business Platform
SECRET_KEY=your_business_platform_secret_key

# Session Configuration (must match Business Platform)
SESSION_COOKIE_NAME=sessionid
SESSION_COOKIE_DOMAIN=.yourdomain.com
SESSION_COOKIE_AGE=1209600
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# Session backend (must match Business Platform)
SESSION_ENGINE=django.contrib.sessions.backends.db
```

#### For Remote API Mode:

```bash
# ========================================
# Business Platform Integration
# ========================================

# Enable Business Platform integration
BUSINESS_PLATFORM_ENABLED=True
BUSINESS_PLATFORM_URL=http://192.168.0.104:8000

# Integration Mode: database or api
BUSINESS_PLATFORM_MODE=api

# API Authentication
BUSINESS_PLATFORM_API_KEY=your_api_key_here

# ========================================
# Local Database Configuration
# ========================================
# This app uses its own database

DB_NAME=asset_tracker
DB_USER=asset_tracker_user
DB_PASSWORD=your_local_db_password
DB_HOST=localhost
DB_PORT=5432

# ========================================
# Session Configuration
# ========================================

SESSION_COOKIE_NAME=sessionid
SESSION_COOKIE_DOMAIN=.yourdomain.com
```

### Step 2: Update Django Settings

The settings have been pre-configured in `asset_tracker/settings.py`. The configuration automatically activates when you set `BUSINESS_PLATFORM_ENABLED=True`.

### Step 3: Configure Middleware

Middleware is automatically enabled. The order in `settings.py` is:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'accounts.business_platform_middleware.BusinessPlatformAuthMiddleware',  # Added
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### Step 4: Configure Authentication Backend

Add to `settings.py`:

```python
AUTHENTICATION_BACKENDS = [
    'accounts.business_platform_backend.SharedDatabaseBackend',  # For shared DB mode
    # OR
    'accounts.business_platform_backend.BusinessPlatformBackend',  # For API mode
    'django.contrib.auth.backends.ModelBackend',  # Fallback
]
```

---

## Database Migration (Shared Database Mode Only)

If using shared database mode:

### Option A: Use Existing Business Platform Users Table

If Business Platform already has a User model compatible with this app:

```bash
# Run migrations but skip creating new tables for existing models
python manage.py migrate --fake-initial
```

### Option B: Create Asset Management Tables Only

If Business Platform has users but different User model:

1. Configure database router to separate tables
2. Run migrations for asset-specific tables only

---

## Session Sharing Configuration

### For Same Domain

If both apps run on same domain (e.g., `platform.company.com` and `assets.company.com`):

```python
SESSION_COOKIE_DOMAIN = '.company.com'  # Note the leading dot
SESSION_COOKIE_SAMESITE = 'Lax'
```

### For Different Domains

If apps run on different domains, you need:

1. **CORS configuration** (already added)
2. **Shared session backend** (Redis recommended)
3. **API-based validation** (use Remote API mode)

```python
# In both apps
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://192.168.0.104:6379/1',
    }
}
```

---

## Business Platform API Endpoints (For Remote API Mode)

If using Remote API mode, the Business Platform must provide these endpoints:

### 1. Validate Session Endpoint

```
GET /api/auth/validate/
Headers:
  Cookie: sessionid=<session_key>
  Authorization: Bearer <api_key>

Response 200 OK:
{
  "id": 123,
  "username": "john.doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "admin",
  "department": "IT",
  "employee_id": "EMP001",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false
}

Response 401 Unauthorized:
{
  "error": "Invalid session"
}
```

### 2. Login API Endpoint (Optional)

```
POST /api/auth/login/
Content-Type: application/json

Request:
{
  "username": "john.doe",
  "password": "password123"
}

Response 200 OK:
{
  "id": 123,
  "username": "john.doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "admin",
  "token": "optional_jwt_token"
}

Response 401 Unauthorized:
{
  "error": "Invalid credentials"
}
```

---

## Testing the Integration

### Test 1: Shared Database Mode

1. Start both applications
2. Login to Business Platform at `http://192.168.0.104:8000/auth/login/`
3. Open Asset Management System at `http://localhost:8000/`
4. You should be automatically logged in

### Test 2: Session Validation

```bash
# Get session cookie from Business Platform
curl -c cookies.txt -X POST http://192.168.0.104:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# Use cookie to access Asset Management System
curl -b cookies.txt http://localhost:8000/dashboard/
```

### Test 3: User Synchronization

Check that users exist in both systems:

```sql
-- On Business Platform database
SELECT id, username, email FROM accounts_user WHERE username='john.doe';

-- On Asset Management database (if separate)
SELECT id, username, email, sso_provider FROM accounts_user WHERE username='john.doe';
```

---

## Troubleshooting

### Issue: Not Automatically Logged In

**Check:**
1. SESSION_COOKIE_DOMAIN matches in both apps
2. SECRET_KEY is identical (for shared DB mode)
3. Database connection is working
4. User exists in the users table
5. Check browser cookies - should see `sessionid` cookie

**Debug:**
```bash
# Check Django logs
tail -f logs/django.log

# Enable debug mode
DEBUG=True

# Check session
python manage.py shell
>>> from django.contrib.sessions.models import Session
>>> Session.objects.all()
```

### Issue: CSRF Token Mismatch

**Solution:**
Ensure CSRF_COOKIE_DOMAIN matches SESSION_COOKIE_DOMAIN:

```python
CSRF_COOKIE_DOMAIN = '.company.com'
CSRF_TRUSTED_ORIGINS = [
    'http://192.168.0.104:8000',
    'http://localhost:8000',
]
```

### Issue: Database Connection Fails

**Check:**
1. Business Platform database allows connections from Asset Management server
2. PostgreSQL `pg_hba.conf` configured for network access
3. Firewall allows port 5432
4. Credentials are correct

```bash
# Test database connection
psql -h 192.168.0.104 -p 5432 -U business_platform_user -d business_platform_db
```

### Issue: API Validation Fails

**Check:**
1. Business Platform API endpoints are accessible
2. API key is correct
3. CORS is configured on Business Platform
4. Session cookie is being sent

```bash
# Test API endpoint
curl http://192.168.0.104:8000/api/auth/validate/ \
  -H "Cookie: sessionid=xxx" \
  -H "Authorization: Bearer your_api_key"
```

---

## Security Considerations

### Shared Database Mode

✅ **Do:**
- Use same SECRET_KEY to decrypt sessions
- Use SSL/TLS for database connections
- Restrict database network access
- Use strong database passwords

❌ **Don't:**
- Expose database to public internet
- Share database credentials in code
- Use weak SECRET_KEY

### Remote API Mode

✅ **Do:**
- Use HTTPS for Business Platform
- Rotate API keys regularly
- Rate limit API endpoints
- Validate API requests
- Log authentication attempts

❌ **Don't:**
- Store API keys in code
- Allow unauthenticated API access
- Skip input validation

---

## Production Checklist

Before deploying to production:

- [ ] Database connection is secure (SSL enabled)
- [ ] SECRET_KEY matches Business Platform
- [ ] SESSION_COOKIE_DOMAIN is configured correctly
- [ ] SESSION_COOKIE_SECURE=True (for HTTPS)
- [ ] CSRF_COOKIE_SECURE=True (for HTTPS)
- [ ] CORS_ALLOWED_ORIGINS configured properly
- [ ] API keys are secure (if using API mode)
- [ ] Logging is configured and monitored
- [ ] Session timeout is appropriate
- [ ] User synchronization is tested
- [ ] Backup strategy is in place

---

## Additional Configuration Options

### User Synchronization

To keep user data in sync between platforms:

```python
# In .env
BUSINESS_PLATFORM_SYNC_USERS=True
BUSINESS_PLATFORM_SYNC_INTERVAL=3600  # Sync every hour
```

### Role Mapping

Map Business Platform roles to Asset Management roles:

```python
# In .env
BUSINESS_PLATFORM_ROLE_MAPPING={
    "admin": "admin",
    "manager": "location_manager",
    "staff": "personnel"
}
```

### Session Timeout

Match session timeout with Business Platform:

```python
SESSION_COOKIE_AGE = 1209600  # 2 weeks (must match Business Platform)
SESSION_SAVE_EVERY_REQUEST = False
```

---

## Support

For integration issues:

1. Check logs: `logs/django.log`
2. Enable DEBUG mode for detailed errors
3. Verify Business Platform configuration
4. Test database/API connectivity
5. Review this documentation

---

## Next Steps

1. Gather Business Platform configuration details
2. Choose integration mode (Shared Database or Remote API)
3. Update `.env` file with configuration
4. Run database migrations (if needed)
5. Test authentication flow
6. Deploy to production

---

**Ready to Configure?**

Please provide:
1. Business Platform database connection details (if using Shared Database mode)
2. Business Platform SECRET_KEY
3. API key (if using Remote API mode)
4. SESSION_COOKIE_DOMAIN for your setup

Then I can help you complete the configuration!
