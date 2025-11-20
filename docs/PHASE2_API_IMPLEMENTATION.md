# Phase 2: REST API Enhancement Implementation Guide

**Project:** Asset Movement Tracking System
**Phase:** 2 - REST API Enhancement
**Duration:** 3-4 weeks
**Status:** In Progress
**Started:** November 20, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Goals and Objectives](#goals-and-objectives)
3. [API Design](#api-design)
4. [Implementation Steps](#implementation-steps)
5. [API Documentation](#api-documentation)
6. [Testing Strategy](#testing-strategy)
7. [Performance Considerations](#performance-considerations)

---

## Overview

### Phase 2 Objectives

Build a comprehensive REST API that provides full programmatic access to all system resources, enabling seamless integration with the Integrated Business Platform and external systems.

### What Will Be Built

- **Complete CRUD APIs** for all models (Assets, Movements, Locations, Users)
- **Interactive API Documentation** (Swagger/OpenAPI)
- **API Versioning** for backward compatibility
- **Advanced Filtering** and search capabilities
- **Rate Limiting** to prevent abuse
- **Comprehensive Permissions** system
- **Pagination** and optimization
- **API Testing Suite**

---

## Goals and Objectives

### Primary Goals

1. ✅ **Complete API Coverage** - CRUD for all resources
2. ✅ **Developer-Friendly** - Clear documentation and consistent design
3. ✅ **Secure** - Proper authentication and authorization
4. ✅ **Performant** - Optimized queries and pagination
5. ✅ **Maintainable** - Well-structured and tested code

### Success Criteria

- All models have REST endpoints
- API documentation auto-generated and interactive
- All endpoints require proper authentication
- Role-based permissions enforced
- Response times < 500ms for most queries
- 90%+ test coverage for API code

---

## API Design

### API Structure

```
/api/v1/
├── auth/
│   ├── token/              POST   - Obtain JWT token
│   ├── token/refresh/      POST   - Refresh JWT token
│   └── token/verify/       POST   - Verify JWT token
│
├── users/
│   ├── /                   GET    - List users
│   ├── /                   POST   - Create user
│   ├── /{id}/              GET    - Retrieve user
│   ├── /{id}/              PUT    - Update user
│   ├── /{id}/              PATCH  - Partial update user
│   ├── /{id}/              DELETE - Delete user
│   └── /me/                GET    - Get current user
│
├── assets/
│   ├── /                   GET    - List assets
│   ├── /                   POST   - Create asset
│   ├── /{id}/              GET    - Retrieve asset
│   ├── /{id}/              PUT    - Update asset
│   ├── /{id}/              PATCH  - Partial update
│   ├── /{id}/              DELETE - Delete asset
│   ├── /{id}/history/      GET    - Asset history
│   ├── /{id}/remarks/      GET    - List remarks
│   ├── /{id}/remarks/      POST   - Add remark
│   └── /categories/        GET    - List categories
│
├── locations/
│   ├── /                   GET    - List locations
│   ├── /                   POST   - Create location
│   ├── /{id}/              GET    - Retrieve location
│   ├── /{id}/              PUT    - Update location
│   ├── /{id}/              PATCH  - Partial update
│   ├── /{id}/              DELETE - Delete location
│   └── /{id}/assets/       GET    - Location assets
│
├── movements/
│   ├── /                   GET    - List movements
│   ├── /                   POST   - Create movement
│   ├── /{id}/              GET    - Retrieve movement
│   ├── /{id}/              PUT    - Update movement
│   ├── /{id}/              PATCH  - Partial update
│   ├── /{id}/              DELETE - Cancel movement
│   ├── /{id}/acknowledge/  POST   - Acknowledge movement
│   └── /track/{number}/    GET    - Track by tracking number
│
├── stock-takes/
│   ├── /                   GET    - List stock takes
│   ├── /                   POST   - Create stock take
│   ├── /{id}/              GET    - Retrieve stock take
│   ├── /{id}/              PUT    - Update stock take
│   ├── /{id}/              PATCH  - Partial update
│   ├── /{id}/start/        POST   - Start stock take
│   ├── /{id}/complete/     POST   - Complete stock take
│   └── /{id}/items/        GET    - List items
│
└── dashboard/
    ├── /stats/             GET    - Dashboard statistics
    └── /notifications/     GET    - User notifications
```

### API Versioning Strategy

**URL-based versioning:**
```
/api/v1/assets/         - Version 1
/api/v2/assets/         - Version 2 (future)
```

**Benefits:**
- Clear and explicit
- Easy to cache
- Client can choose version

### Response Format

**Success Response:**
```json
{
  "id": 1,
  "asset_id": "AST-001",
  "name": "Laptop",
  "status": "available",
  "created_at": "2025-11-20T10:30:00Z"
}
```

**List Response (Paginated):**
```json
{
  "count": 100,
  "next": "http://api.example.com/api/v1/assets/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "asset_id": "AST-001",
      "name": "Laptop"
    }
  ]
}
```

**Error Response:**
```json
{
  "error": "ValidationError",
  "message": "Invalid input data",
  "details": {
    "name": ["This field is required."]
  }
}
```

### Filtering and Search

**Query Parameters:**

```bash
# Filtering
GET /api/v1/assets/?status=available&category=1

# Search
GET /api/v1/assets/?search=laptop

# Ordering
GET /api/v1/assets/?ordering=-created_at

# Pagination
GET /api/v1/assets/?page=2&page_size=50

# Multiple filters
GET /api/v1/assets/?status=available&location=1&search=dell
```

**Supported Filters per Model:**

**Assets:**
- `status` - Filter by status
- `category` - Filter by category ID
- `location` - Filter by current location ID
- `condition` - Filter by condition
- `responsible_person` - Filter by responsible person ID
- `search` - Search in asset_id, name, description

**Movements:**
- `status` - Filter by status
- `asset` - Filter by asset ID
- `from_location` - Filter by source location
- `to_location` - Filter by destination location
- `priority` - Filter by priority
- `is_overdue` - Filter overdue movements
- `search` - Search in tracking_number, reason

**Locations:**
- `is_active` - Filter active locations
- `country` - Filter by country
- `search` - Search in name, code, city

---

## Implementation Steps

### Week 1: Core API Structure

#### Step 1: Update Dependencies ✅

**Add to requirements.txt:**
```python
# API Enhancement (Phase 2)
drf-spectacular==0.27.0          # API documentation
django-filter==23.5              # Advanced filtering
djangorestframework-simplejwt[crypto]==5.3.1
django-rest-framework-simplejwt-blacklist==0.2.0
```

#### Step 2: Create API App Structure ✅

```bash
# Create api app
python manage.py startapp api

# Create directory structure
mkdir -p api/v1
mkdir -p api/v1/serializers
mkdir -p api/v1/viewsets
mkdir -p api/v1/permissions
mkdir -p api/v1/filters
touch api/v1/__init__.py
touch api/v1/urls.py
```

#### Step 3: Configure Settings ✅

**Update settings.py:**

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'drf_spectacular',
    # ...
    'api',  # Add API app
]

REST_FRAMEWORK = {
    # ... existing settings ...

    # Add schema and filtering
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# Spectacular Settings (API Documentation)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Asset Movement Tracking System API',
    'DESCRIPTION': 'Complete REST API for asset management and tracking',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
}
```

### Week 2: Model Serializers

#### Step 4: Create Serializers ✅

**File: api/v1/serializers/__init__.py**

```python
from .user_serializers import UserSerializer, UserDetailSerializer
from .asset_serializers import (
    AssetSerializer,
    AssetDetailSerializer,
    AssetCategorySerializer,
    AssetRemarkSerializer
)
from .location_serializers import LocationSerializer, LocationDetailSerializer
from .movement_serializers import (
    MovementSerializer,
    MovementDetailSerializer,
    MovementAcknowledgementSerializer,
    StockTakeSerializer,
    StockTakeItemSerializer
)

__all__ = [
    'UserSerializer',
    'UserDetailSerializer',
    'AssetSerializer',
    'AssetDetailSerializer',
    'AssetCategorySerializer',
    'AssetRemarkSerializer',
    'LocationSerializer',
    'LocationDetailSerializer',
    'MovementSerializer',
    'MovementDetailSerializer',
    'MovementAcknowledgementSerializer',
    'StockTakeSerializer',
    'StockTakeItemSerializer',
]
```

**File: api/v1/serializers/asset_serializers.py**

```python
from rest_framework import serializers
from assets.models import Asset, AssetCategory, AssetRemark
from .user_serializers import UserSerializer
from .location_serializers import LocationSerializer


class AssetCategorySerializer(serializers.ModelSerializer):
    asset_count = serializers.SerializerMethodField()

    class Meta:
        model = AssetCategory
        fields = ['id', 'name', 'description', 'is_active', 'asset_count']
        read_only_fields = ['id']

    def get_asset_count(self, obj):
        return obj.assets.count()


class AssetSerializer(serializers.ModelSerializer):
    """Asset list serializer - lightweight for lists"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    location_name = serializers.CharField(source='current_location.name', read_only=True)
    responsible_person_name = serializers.CharField(
        source='responsible_person.get_full_name',
        read_only=True
    )

    class Meta:
        model = Asset
        fields = [
            'id', 'asset_id', 'name', 'description',
            'category', 'category_name',
            'status', 'condition',
            'current_location', 'location_name',
            'responsible_person', 'responsible_person_name',
            'purchase_value', 'current_value',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AssetDetailSerializer(serializers.ModelSerializer):
    """Asset detail serializer - full information"""
    category = AssetCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=AssetCategory.objects.all(),
        source='category',
        write_only=True
    )
    current_location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source='current_location',
        write_only=True
    )
    responsible_person = UserSerializer(read_only=True)
    responsible_person_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='responsible_person',
        write_only=True,
        required=False,
        allow_null=True
    )
    created_by = UserSerializer(read_only=True)

    # Additional computed fields
    is_available = serializers.ReadOnlyField()
    is_in_transit = serializers.ReadOnlyField()

    class Meta:
        model = Asset
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class AssetRemarkSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = AssetRemark
        fields = ['id', 'asset', 'category', 'remark', 'is_important',
                  'created_by', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
```

### Week 3: ViewSets and URLs

#### Step 5: Create ViewSets ✅

**File: api/v1/viewsets/asset_viewsets.py**

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from assets.models import Asset, AssetCategory, AssetRemark
from ..serializers import (
    AssetSerializer,
    AssetDetailSerializer,
    AssetCategorySerializer,
    AssetRemarkSerializer
)
from ..permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from ..filters import AssetFilter


@extend_schema_view(
    list=extend_schema(
        summary="List all assets",
        description="Get a paginated list of all assets with filtering options",
        parameters=[
            OpenApiParameter('status', OpenApiTypes.STR, description='Filter by status'),
            OpenApiParameter('category', OpenApiTypes.INT, description='Filter by category ID'),
            OpenApiParameter('location', OpenApiTypes.INT, description='Filter by location ID'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Search in asset_id, name, description'),
        ]
    ),
    retrieve=extend_schema(
        summary="Get asset details",
        description="Retrieve detailed information about a specific asset"
    ),
    create=extend_schema(
        summary="Create new asset",
        description="Create a new asset in the system"
    ),
    update=extend_schema(
        summary="Update asset",
        description="Update all fields of an asset"
    ),
    partial_update=extend_schema(
        summary="Partial update asset",
        description="Update specific fields of an asset"
    ),
    destroy=extend_schema(
        summary="Delete asset",
        description="Delete an asset from the system"
    )
)
class AssetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Asset CRUD operations.

    Supports filtering by status, category, location, and search.
    """
    queryset = Asset.objects.select_related(
        'category', 'current_location', 'responsible_person', 'created_by'
    ).all()
    permission_classes = [IsAuthenticated]
    filterset_class = AssetFilter
    search_fields = ['asset_id', 'name', 'description', 'serial_number']
    ordering_fields = ['asset_id', 'name', 'created_at', 'purchase_value']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AssetDetailSerializer
        return AssetSerializer

    @extend_schema(
        summary="Get asset movement history",
        description="Retrieve all movements associated with this asset"
    )
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get asset movement history"""
        asset = self.get_object()
        movements = asset.movements.select_related(
            'from_location', 'to_location', 'initiated_by'
        ).order_by('-created_at')

        from ..serializers import MovementSerializer
        serializer = MovementSerializer(movements, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get asset remarks",
        description="Retrieve all remarks/notes for this asset"
    )
    @action(detail=True, methods=['get', 'post'])
    def remarks(self, request, pk=None):
        """Get or add asset remarks"""
        asset = self.get_object()

        if request.method == 'GET':
            remarks = asset.remarks.select_related('created_by').order_by('-created_at')
            serializer = AssetRemarkSerializer(remarks, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = AssetRemarkSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(asset=asset)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssetCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Asset Categories (read-only).

    Categories are managed through Django admin.
    """
    queryset = AssetCategory.objects.filter(is_active=True)
    serializer_class = AssetCategorySerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name']
    ordering = ['name']
```

#### Step 6: Create Filters ✅

**File: api/v1/filters/asset_filters.py**

```python
from django_filters import rest_framework as filters
from assets.models import Asset


class AssetFilter(filters.FilterSet):
    """Advanced filtering for Assets"""

    status = filters.MultipleChoiceFilter(choices=Asset.STATUS_CHOICES)
    condition = filters.MultipleChoiceFilter(choices=Asset.CONDITION_CHOICES)
    category = filters.NumberFilter(field_name='category__id')
    location = filters.NumberFilter(field_name='current_location__id')
    responsible_person = filters.NumberFilter(field_name='responsible_person__id')

    # Date range filters
    purchase_date_after = filters.DateFilter(field_name='purchase_date', lookup_expr='gte')
    purchase_date_before = filters.DateFilter(field_name='purchase_date', lookup_expr='lte')

    # Value range filters
    purchase_value_min = filters.NumberFilter(field_name='purchase_value', lookup_expr='gte')
    purchase_value_max = filters.NumberFilter(field_name='purchase_value', lookup_expr='lte')

    class Meta:
        model = Asset
        fields = ['status', 'condition', 'category', 'location', 'responsible_person']
```

#### Step 7: Create Permissions ✅

**File: api/v1/permissions.py**

```python
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission check for admin users only.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsLocationManager(permissions.BasePermission):
    """
    Permission check for location managers and admins.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_location_manager


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin can do anything, others can only read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object owner or admin can modify, others can read.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if user is admin
        if request.user.is_admin:
            return True

        # Check if user is owner (for objects with created_by field)
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user

        return False
```

### Week 4: Documentation and Testing

#### Step 8: Configure API Documentation ✅

**Update urls.py:**

```python
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

urlpatterns = [
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API v1
    path('api/v1/', include('api.v1.urls')),
]
```

#### Step 9: Create API Tests ✅

**File: api/tests/test_assets_api.py**

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from assets.models import Asset, AssetCategory
from locations.models import Location

User = get_user_model()


class AssetAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )

        # Create test data
        self.category = AssetCategory.objects.create(name='Test Category')
        self.location = Location.objects.create(
            name='Test Location',
            code='TEST',
            address='123 Test St',
            city='Test City',
            country='Test Country'
        )

        self.asset = Asset.objects.create(
            asset_id='TEST-001',
            name='Test Asset',
            description='Test Description',
            category=self.category,
            current_location=self.location,
            created_by=self.user
        )

    def test_list_assets_requires_auth(self):
        """Test that listing assets requires authentication"""
        response = self.client.get('/api/v1/assets/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_assets_with_auth(self):
        """Test listing assets with authentication"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/assets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_create_asset(self):
        """Test creating a new asset"""
        self.client.force_authenticate(user=self.user)
        data = {
            'asset_id': 'TEST-002',
            'name': 'New Asset',
            'description': 'New Description',
            'category_id': self.category.id,
            'location_id': self.location.id,
            'status': 'available'
        }
        response = self.client.post('/api/v1/assets/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['asset_id'], 'TEST-002')

    def test_filter_assets_by_status(self):
        """Test filtering assets by status"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/assets/?status=available')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_assets(self):
        """Test searching assets"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/assets/?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

---

## API Documentation

### Interactive Documentation

**Swagger UI:**
```
http://localhost:8000/api/docs/
```

**ReDoc:**
```
http://localhost:8000/api/redoc/
```

**OpenAPI Schema:**
```
http://localhost:8000/api/schema/
```

### Example API Calls

**Get JWT Token:**
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

**List Assets:**
```bash
curl http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Bearer {your-token}"
```

**Create Asset:**
```bash
curl -X POST http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Bearer {your-token}" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": "LAP-001",
    "name": "Dell Laptop",
    "description": "Business laptop",
    "category_id": 1,
    "location_id": 1,
    "status": "available"
  }'
```

**Filter Assets:**
```bash
curl "http://localhost:8000/api/v1/assets/?status=available&category=1" \
  -H "Authorization: Bearer {your-token}"
```

---

## Testing Strategy

### Unit Tests
- Serializer validation
- Permission checks
- Filter functionality

### Integration Tests
- API endpoints
- Authentication/authorization
- CRUD operations

### Performance Tests
- Response time benchmarks
- Query optimization
- Load testing

---

## Performance Considerations

### Query Optimization
- Use `select_related()` for foreign keys
- Use `prefetch_related()` for many-to-many
- Add database indexes for filtered fields

### Pagination
- Default: 20 items per page
- Maximum: 100 items per page
- Use `page_size` parameter

### Caching
- Cache frequently accessed data
- Use Redis for production
- Set appropriate cache timeouts

### Rate Limiting
- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour
- Can be customized per endpoint

---

**Document Version:** 1.0
**Last Updated:** November 20, 2025
**Status:** In Implementation
