# Phase 2: REST API - Quick Implementation Guide

**Status:** Ready to Implement
**Estimated Time:** 3-4 weeks
**Prerequisites:** Phase 1 completed

---

## Overview

Phase 2 adds comprehensive REST API capabilities to enable full programmatic access to all system resources.

### What You'll Get

- ✅ Complete CRUD APIs for all models
- ✅ Interactive API documentation (Swagger UI)
- ✅ Advanced filtering and search
- ✅ Role-based API permissions
- ✅ Rate limiting
- ✅ API versioning (`/api/v1/`)

---

## Quick Start (30 Minutes)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**New packages added:**
- `drf-spectacular` - API documentation
- `django-filter` - Advanced filtering

### Step 2: Update Settings

Add to `INSTALLED_APPS` in `asset_tracker/settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'django_filters',
    'drf_spectacular',
    'api',  # New API app
]
```

Add to `REST_FRAMEWORK` settings:

```python
REST_FRAMEWORK = {
    # ... existing settings ...

    # Phase 2: API Documentation
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    # Phase 2: Advanced Filtering
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],

    # Phase 2: Rate Limiting
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# Phase 2: API Documentation Settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Asset Movement Tracking System API',
    'DESCRIPTION': 'Complete REST API for asset management and tracking between Hong Kong and Shenzhen locations.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
    'SWAGGER_UI_FAVICON_HREF': '/static/favicon.ico',
    'REDOC_DIST': 'SIDECAR',
}
```

### Step 3: Update URLs

Add to `asset_tracker/urls.py`:

```python
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

urlpatterns = [
    # ... existing patterns ...

    # Phase 2: API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Phase 2: API v1 Endpoints
    path('api/v1/', include('api.v1.urls')),
]
```

### Step 4: Run Migrations

```bash
python manage.py migrate
```

### Step 5: Start Server and Test

```bash
python manage.py runserver
```

**Access API Documentation:**
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

---

## API Structure

```
/api/v1/
├── assets/                 # Asset management
│   ├── GET, POST          # List/Create assets
│   ├── /{id}/             # Retrieve/Update/Delete asset
│   ├── /{id}/history/     # Asset movement history
│   ├── /{id}/remarks/     # Asset remarks/notes
│   └── /categories/       # Asset categories
│
├── locations/              # Location management
│   ├── GET, POST          # List/Create locations
│   ├── /{id}/             # Retrieve/Update/Delete location
│   └── /{id}/assets/      # Assets at location
│
├── movements/              # Movement tracking
│   ├── GET, POST          # List/Create movements
│   ├── /{id}/             # Retrieve/Update/Delete movement
│   ├── /{id}/acknowledge/ # Acknowledge receipt
│   └── /track/{number}/   # Track by tracking number
│
├── stock-takes/            # Stock taking
│   ├── GET, POST          # List/Create stock takes
│   ├── /{id}/             # Retrieve/Update stock take
│   ├── /{id}/start/       # Start stock take
│   ├── /{id}/complete/    # Complete stock take
│   └── /{id}/items/       # Stock take items
│
└── users/                  # User management
    ├── GET, POST          # List/Create users
    ├── /{id}/             # Retrieve/Update/Delete user
    └── /me/               # Current user profile
```

---

## Example API Calls

### 1. Get JWT Token

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password"
  }'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. List All Assets

```bash
curl http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Response:**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/v1/assets/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "asset_id": "LAP-001",
      "name": "Dell Laptop",
      "status": "available",
      "category_name": "IT Equipment",
      "location_name": "Hong Kong Office"
    }
  ]
}
```

### 3. Filter Assets by Status

```bash
curl "http://localhost:8000/api/v1/assets/?status=available" \
  -H "Authorization: Bearer {token}"
```

### 4. Search Assets

```bash
curl "http://localhost:8000/api/v1/assets/?search=laptop" \
  -H "Authorization: Bearer {token}"
```

### 5. Create New Asset

```bash
curl -X POST http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": "LAP-002",
    "name": "HP Laptop",
    "description": "Business laptop for marketing",
    "category_id": 1,
    "location_id": 1,
    "status": "available",
    "condition": "excellent"
  }'
```

### 6. Get Asset Details

```bash
curl http://localhost:8000/api/v1/assets/1/ \
  -H "Authorization: Bearer {token}"
```

### 7. Update Asset

```bash
curl -X PATCH http://localhost:8000/api/v1/assets/1/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_use",
    "responsible_person_id": 2
  }'
```

### 8. Get Asset Movement History

```bash
curl http://localhost:8000/api/v1/assets/1/history/ \
  -H "Authorization: Bearer {token}"
```

### 9. Create Movement

```bash
curl -X POST http://localhost:8000/api/v1/movements/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": 1,
    "from_location_id": 1,
    "to_location_id": 2,
    "reason": "Transfer for project",
    "expected_arrival_date": "2025-11-25T10:00:00Z",
    "priority": "normal"
  }'
```

### 10. Track Movement by Tracking Number

```bash
curl http://localhost:8000/api/v1/movements/track/MV2025-ABC123/ \
  -H "Authorization: Bearer {token}"
```

---

## Filtering Options

### Assets

```bash
# Filter by status
?status=available

# Filter by category
?category=1

# Filter by location
?location=2

# Filter by condition
?condition=excellent

# Multiple filters
?status=available&location=1&category=2

# Search in name, asset_id, description
?search=laptop

# Ordering
?ordering=-created_at
?ordering=name

# Pagination
?page=2&page_size=50
```

### Movements

```bash
# Filter by status
?status=in_transit

# Filter by asset
?asset=1

# Filter by location
?from_location=1
?to_location=2

# Filter by priority
?priority=urgent

# Filter overdue
?is_overdue=true

# Search in tracking_number, reason
?search=MV2025
```

### Locations

```bash
# Filter active
?is_active=true

# Filter by country
?country=Hong Kong

# Search
?search=Hong Kong
```

---

## API Permissions

### Permission Levels

| Role | Permissions |
|------|-------------|
| **Admin** | Full CRUD access to all resources |
| **Location Manager** | Create/Read/Update movements, stock takes, assets at their locations |
| **Personnel** | Read all, Create movements and remarks only |
| **Anonymous** | No access (401 Unauthorized) |

### Permission Classes

**Used in viewsets:**

```python
from api.v1.permissions import IsAdminUser, IsLocationManager, IsAdminOrReadOnly

class AssetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]  # Read for all, write for admin
```

---

## Rate Limiting

**Default Rates:**
- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour

**Headers in Response:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1700000000
```

**When limit exceeded:**
```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

---

## Testing APIs

### Using Swagger UI

1. Go to http://localhost:8000/api/docs/
2. Click "Authorize" button
3. Enter: `Bearer {your-access-token}`
4. Click "Authorize"
5. Try any endpoint

### Using Postman

1. **Import OpenAPI Schema:**
   - File → Import → Link
   - Paste: http://localhost:8000/api/schema/

2. **Set Authorization:**
   - Authorization tab
   - Type: Bearer Token
   - Token: {your-access-token}

3. **Make Requests**

### Using Python Requests

```python
import requests

# Get token
response = requests.post('http://localhost:8000/api/token/', json={
    'username': 'admin',
    'password': 'password'
})
token = response.json()['access']

# Make API call
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:8000/api/v1/assets/', headers=headers)
print(response.json())
```

---

## Next Steps

### Week 1-2: Core Implementation
- ✅ Install dependencies
- ✅ Configure settings
- ✅ Create API structure
- 🔄 Implement serializers (see `api/v1/serializers/`)
- 🔄 Implement viewsets (see `api/v1/viewsets/`)

### Week 3: Advanced Features
- 🔄 Implement filters (see `api/v1/filters/`)
- 🔄 Add custom actions
- 🔄 Optimize queries
- 🔄 Add caching

### Week 4: Testing & Documentation
- 🔄 Write API tests
- 🔄 Performance testing
- 🔄 API documentation
- 🔄 Client examples

---

## Implementation Files to Create

### Serializers (`api/v1/serializers/`)
- `user_serializers.py` - User, profile
- `asset_serializers.py` - Asset, category, remarks
- `location_serializers.py` - Location
- `movement_serializers.py` - Movement, acknowledgement, stock take

### ViewSets (`api/v1/viewsets/`)
- `user_viewsets.py` - User CRUD
- `asset_viewsets.py` - Asset CRUD + custom actions
- `location_viewsets.py` - Location CRUD
- `movement_viewsets.py` - Movement CRUD + tracking

### Filters (`api/v1/filters/`)
- `asset_filters.py` - Asset filtering
- `movement_filters.py` - Movement filtering

### URLs (`api/v1/`)
- `urls.py` - API v1 URL routing

---

## Troubleshooting

### Issue: "AttributeError: 'Settings' object has no attribute 'SPECTACULAR_SETTINGS'"

**Solution:** Add SPECTACULAR_SETTINGS to settings.py (see Step 2 above)

### Issue: API docs showing "Authentication credentials were not provided"

**Solution:**
1. Get JWT token from `/api/token/`
2. Click "Authorize" in Swagger UI
3. Enter: `Bearer {token}`

### Issue: "ModuleNotFoundError: No module named 'drf_spectacular'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Rate limit reached

**Solution:** Wait for rate limit reset or increase limits in settings:
```python
'DEFAULT_THROTTLE_RATES': {
    'user': '10000/hour'  # Increase limit
}
```

---

## Performance Tips

1. **Use select_related() for ForeignKey:**
   ```python
   Asset.objects.select_related('category', 'current_location')
   ```

2. **Use prefetch_related() for reverse ForeignKey:**
   ```python
   Asset.objects.prefetch_related('movements', 'remarks')
   ```

3. **Add database indexes:**
   ```python
   class Meta:
       indexes = [
           models.Index(fields=['status', 'location']),
       ]
   ```

4. **Use pagination:**
   ```bash
   ?page_size=20  # Don't fetch too many at once
   ```

5. **Cache frequent queries:**
   ```python
   from django.core.cache import cache

   stats = cache.get('dashboard_stats')
   if not stats:
       stats = calculate_stats()
       cache.set('dashboard_stats', stats, 300)  # 5 minutes
   ```

---

## Resources

**Documentation:**
- Full Guide: `docs/PHASE2_API_IMPLEMENTATION.md`
- DRF Docs: https://www.django-rest-framework.org/
- drf-spectacular: https://drf-spectacular.readthedocs.io/
- django-filter: https://django-filter.readthedocs.io/

**API Documentation:**
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

---

**Status:** Implementation Ready
**Estimated Completion:** 3-4 weeks
**Next:** Begin implementing serializers and viewsets
