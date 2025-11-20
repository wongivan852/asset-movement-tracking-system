# Phase 3: Embedding Configuration - Complete Implementation Guide

**Version:** 1.0.0
**Date:** November 20, 2025
**Target:** Integration with Integrated Business Platform

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Implementation Details](#implementation-details)
3. [Middleware Components](#middleware-components)
4. [Frontend Components](#frontend-components)
5. [Security Implementation](#security-implementation)
6. [Session Management](#session-management)
7. [Theme System](#theme-system)
8. [PostMessage Protocol](#postmessage-protocol)
9. [Testing Guide](#testing-guide)
10. [Production Deployment](#production-deployment)
11. [API Reference](#api-reference)

---

## Architecture Overview

### Integration Pattern

```
┌─────────────────────────────────────────────────────────────┐
│           Integrated Business Platform (Parent)             │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Platform Session Management                         │  │
│  │  - User Authentication                               │  │
│  │  - Session Token Generation                          │  │
│  │  - Theme Management                                  │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                           │
│                 │ PostMessage API                           │
│                 │ - Session Sync                            │
│                 │ - Theme Sync                              │
│                 │ - Navigation Events                       │
│                 ▼                                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  <iframe> Container                                  │  │
│  │                                                      │  │
│  │   ┌──────────────────────────────────────────────┐  │  │
│  │   │  Asset Movement Tracking System (Child)      │  │  │
│  │   │                                              │  │  │
│  │   │  ┌────────────────────────────────────────┐  │  │  │
│  │   │  │ EmbeddedModeMiddleware                 │  │  │  │
│  │   │  │ - Detects embedded mode                │  │  │  │
│  │   │  │ - Extracts session token               │  │  │  │
│  │   │  │ - Applies theme config                 │  │  │  │
│  │   │  └────────────────────────────────────────┘  │  │  │
│  │   │                                              │  │  │
│  │   │  ┌────────────────────────────────────────┐  │  │  │
│  │   │  │ EmbeddedSecurityMiddleware             │  │  │  │
│  │   │  │ - Validates origin                     │  │  │  │
│  │   │  │ - Enforces HTTPS                       │  │  │  │
│  │   │  │ - Sets security headers                │  │  │  │
│  │   │  └────────────────────────────────────────┘  │  │  │
│  │   │                                              │  │  │
│  │   │  ┌────────────────────────────────────────┐  │  │  │
│  │   │  │ embedded.js                            │  │  │  │
│  │   │  │ - PostMessage handler                  │  │  │  │
│  │   │  │ - Session sync                         │  │  │  │
│  │   │  │ - Theme application                    │  │  │  │
│  │   │  │ - Navigation tracking                  │  │  │  │
│  │   │  └────────────────────────────────────────┘  │  │  │
│  │   │                                              │  │  │
│  │   └──────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
1. Parent Platform loads iframe with embedded parameter
   ↓
2. EmbeddedModeMiddleware detects embedded mode
   ↓
3. Template loads with embedded.css and embedded.js
   ↓
4. embedded.js detects iframe context
   ↓
5. embedded.js sends 'iframe_ready' to parent
   ↓
6. Parent responds with session_sync and theme_update
   ↓
7. Middleware processes session token
   ↓
8. embedded.js applies theme variables
   ↓
9. User interacts with embedded application
   ↓
10. Navigation events sent to parent for tracking
```

---

## Implementation Details

### File Structure

```
asset_tracker/
├── middleware/
│   ├── __init__.py
│   └── embedded.py                    # 360 lines
│       ├── EmbeddedModeMiddleware     # Detection & context
│       └── EmbeddedSecurityMiddleware # Security validation
│
static/
├── css/
│   └── embedded.css                   # 280 lines
│       ├── CSS variables              # Theming system
│       ├── Embedded layouts           # Compact styles
│       └── Responsive adjustments     # Mobile support
│
├── js/
│   └── embedded.js                    # 430 lines
│       ├── EmbeddedMode object        # Main controller
│       ├── PostMessage handler        # Communication
│       ├── Session sync               # Token management
│       ├── Theme sync                 # Style application
│       └── Navigation tracking        # Event broadcasting
│
templates/
└── base_embedded.html                 # Extended base template
```

---

## Middleware Components

### EmbeddedModeMiddleware

**Purpose:** Detect embedded mode and prepare context for rendering.

**Location:** `asset_tracker/middleware/embedded.py` (lines 1-135)

#### Detection Methods

```python
def _is_embedded(self, request):
    """
    Detect if request is from an embedded iframe.

    Detection priority:
    1. Query parameter 'embedded'
    2. Custom header 'X-Embedded-Mode'
    3. Platform session token in query
    4. Referer header matching PLATFORM_URL
    """
```

**Detection Method 1: Query Parameter** (Recommended)
```python
# Example: /?embedded=minimal
if 'embedded' in request.GET:
    return True
```

**Detection Method 2: HTTP Header**
```python
# Example: X-Embedded-Mode: true
if request.headers.get('X-Embedded-Mode') == 'true':
    return True
```

**Detection Method 3: Platform Token**
```python
# Example: /?platform_session_token=...
if 'platform_session_token' in request.GET:
    return True
```

**Detection Method 4: Referer Header**
```python
# Example: Referer: https://integrated-platform.company.com/...
referer = request.headers.get('Referer', '')
platform_url = settings.PLATFORM_URL
if platform_url and referer.startswith(platform_url):
    return True
```

#### Context Processing

```python
def process_template_response(self, request, response):
    """
    Add embedded mode context variables to templates.

    Context variables added:
    - is_embedded: Boolean flag
    - embedded_mode: String ('normal', 'minimal', 'no-nav')
    - platform_origin: String (for PostMessage security)
    - custom_theme: Dict (theme configuration)
    - debug_embedded: Boolean
    """
```

#### Session Synchronization

```python
def _sync_session(self, request):
    """
    Synchronize session with parent platform.

    Process:
    1. Extract platform_session_token from query
    2. Store in Django session
    3. Optionally validate with platform API
    """
```

#### Theme Extraction

```python
def _get_theme_config(self, request):
    """
    Extract theme configuration from request.

    Sources (in priority order):
    1. Query parameters (primary_color, navbar_bg, etc.)
    2. HTTP header X-Embedded-Theme (JSON)
    3. Session storage (from previous sync)

    Returns: Dict of theme variables or None
    """
```

### EmbeddedSecurityMiddleware

**Purpose:** Enforce security policies for embedded mode.

**Location:** `asset_tracker/middleware/embedded.py` (lines 136-230)

#### Security Checks

```python
def process_request(self, request):
    """
    Perform security checks for embedded mode.

    Checks:
    1. HTTPS requirement (production only)
    2. Origin validation against EMBEDDED_ALLOWED_ORIGINS
    3. Referer header validation
    """
```

**HTTPS Enforcement:**
```python
# In production, enforce HTTPS for embedded mode
if not settings.DEBUG and not request.is_secure():
    return HttpResponseForbidden(
        'Embedded mode requires HTTPS in production'
    )
```

**Origin Validation:**
```python
def _validate_origin(self, request):
    """
    Validate that request is from allowed origin.

    Process:
    1. Get allowed origins from settings
    2. Check Referer header
    3. Compare against whitelist
    """
```

#### Security Headers

```python
def process_response(self, request, response):
    """
    Add security headers for embedded mode.

    Headers added:
    - Permissions-Policy: Controls iframe features
    - Referrer-Policy: Privacy protection
    """
```

**Permissions Policy Example:**
```python
# Disable sensitive features in iframe
permissions = {
    'camera': '()',      # No camera access
    'microphone': '()',  # No microphone access
    'geolocation': '()', # No location access
    'payment': '()',     # No payment APIs
}
```

---

## Frontend Components

### CSS: embedded.css

**Purpose:** Provide themed, responsive styles for embedded mode.

**Location:** `static/css/embedded.css` (280 lines)

#### CSS Variables System

```css
:root {
    /* Primary Colors */
    --primary-color: #0d6efd;
    --secondary-color: #6c757d;

    /* Background Colors */
    --body-bg: #ffffff;
    --card-bg: #ffffff;
    --navbar-bg: #212529;

    /* Text Colors */
    --text-color: #212529;
    --text-muted: #6c757d;
    --link-color: #0d6efd;

    /* Layout */
    --nav-height: 56px;
    --spacing-md: 1rem;
    --border-radius: 0.375rem;

    /* Typography */
    --font-size-base: 1rem;
    --font-size-sm: 0.875rem;
}
```

#### Embedded Mode Styles

**Body Class:**
```css
body.embedded-mode {
    background-color: var(--body-bg);
    padding: 0;
    margin: 0;
    overflow-x: hidden;
}
```

**Compact Navigation:**
```css
body.embedded-mode .navbar {
    background-color: var(--nav-bg) !important;
    min-height: var(--nav-height);
    padding: 0.25rem 1rem;
}

body.embedded-mode .nav-link {
    color: var(--nav-link-color) !important;
    padding: 0.25rem 0.75rem;
    font-size: var(--font-size-sm);
}
```

**Navigation Modes:**

1. **Normal Mode** (default)
```css
body.embedded-mode .navbar {
    min-height: 56px;
}
```

2. **Minimal Mode**
```css
body.embedded-mode.minimal-chrome .navbar {
    min-height: 40px;
    padding: 0.125rem 0.75rem;
}

body.embedded-mode.minimal-chrome .navbar-brand {
    font-size: 0.875rem;
}
```

3. **No Navigation**
```css
body.embedded-mode.no-navigation .navbar {
    display: none !important;
}

body.embedded-mode.no-navigation main {
    padding-top: 1rem;
}
```

#### Dark Theme Support

```css
body[data-theme="dark"] {
    --body-bg: #1a1a1a;
    --card-bg: #2d2d2d;
    --text-color: #e0e0e0;
    --text-muted: #9e9e9e;
    --border-color: #404040;
    --nav-bg: #0d0d0d;
}
```

#### Responsive Design

```css
@media (max-width: 768px) {
    body.embedded-mode .navbar {
        padding: 0.25rem 0.5rem;
    }

    body.embedded-mode main {
        padding: 0.5rem;
    }

    body.embedded-mode .card-body {
        padding: 0.5rem;
    }
}
```

### JavaScript: embedded.js

**Purpose:** Handle PostMessage communication and embedded mode features.

**Location:** `static/js/embedded.js` (430 lines)

#### EmbeddedMode Object

```javascript
const EmbeddedMode = {
    // Configuration
    config: {
        platformOrigin: '*',           // Parent origin
        enablePostMessage: true,       // Enable communication
        enableSessionSync: true,       // Sync sessions
        enableThemeSync: true,         // Sync themes
        enableNavigationSync: true,    // Track navigation
        debug: false                   // Debug logging
    },

    // State
    isEmbedded: false,                 // Embedded flag
    parentWindow: null,                // Parent reference

    // Methods
    init() {...},
    detectEmbeddedMode() {...},
    setupPostMessageListener() {...},
    sendMessageToParent(message) {...}
}
```

#### Embedded Detection

```javascript
detectEmbeddedMode: function() {
    try {
        // Detect if in iframe
        this.isEmbedded = window.self !== window.top;
        this.parentWindow = window.parent;

        // Add embedded class to body
        if (this.isEmbedded) {
            document.body.classList.add('embedded-mode');

            // Check for mode parameter
            const urlParams = new URLSearchParams(window.location.search);
            const embeddedParam = urlParams.get('embedded');

            if (embeddedParam === 'minimal') {
                document.body.classList.add('minimal-chrome');
            } else if (embeddedParam === 'no-nav') {
                document.body.classList.add('no-navigation');
            }
        }
    } catch (e) {
        this.log('Error detecting embedded mode:', e);
        this.isEmbedded = false;
    }
}
```

#### PostMessage Handler

```javascript
setupPostMessageListener: function() {
    window.addEventListener('message', (event) => {
        // Validate origin
        if (this.config.platformOrigin !== '*' &&
            event.origin !== this.config.platformOrigin) {
            this.log('Rejected message from:', event.origin);
            return;
        }

        // Route message by type
        switch (event.data.type) {
            case 'session_sync':
                this.handleSessionSync(event.data);
                break;
            case 'theme_update':
                this.handleThemeUpdate(event.data);
                break;
            case 'navigation_update':
                this.handleNavigationUpdate(event.data);
                break;
            case 'resize':
                this.handleResize(event.data);
                break;
            case 'logout':
                this.handleLogout(event.data);
                break;
        }
    });
}
```

#### Session Synchronization

```javascript
handleSessionSync: function(data) {
    this.log('Syncing session from parent');

    // Store session data
    if (data.sessionToken) {
        sessionStorage.setItem('platform_session_token', data.sessionToken);
    }

    if (data.userData) {
        sessionStorage.setItem('platform_user_data', JSON.stringify(data.userData));
    }

    // Dispatch custom event
    window.dispatchEvent(new CustomEvent('session_synced', {
        detail: data
    }));
}
```

#### Theme Application

```javascript
handleThemeUpdate: function(data) {
    this.log('Updating theme:', data.theme);

    // Apply theme attribute
    if (data.theme) {
        document.body.setAttribute('data-theme', data.theme);
    }

    // Apply CSS variables
    if (data.cssVariables) {
        const root = document.documentElement;
        for (const [key, value] of Object.entries(data.cssVariables)) {
            root.style.setProperty(`--${key}`, value);
        }
    }

    // Apply shorthand colors
    if (data.primaryColor) {
        document.documentElement.style.setProperty(
            '--primary-color',
            data.primaryColor
        );
    }

    // Dispatch event
    window.dispatchEvent(new CustomEvent('theme_updated', {
        detail: data
    }));
}
```

#### Navigation Tracking

```javascript
setupNavigationSync: function() {
    // Track popstate events
    window.addEventListener('popstate', () => {
        const currentPath = window.location.pathname;
        this.sendMessageToParent({
            type: 'navigation_change',
            path: currentPath,
            url: window.location.href,
            timestamp: new Date().toISOString()
        });
    });

    // Intercept link clicks
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (link && link.href && !link.target) {
            const url = new URL(link.href);
            if (url.origin === window.location.origin) {
                this.sendMessageToParent({
                    type: 'navigation_intent',
                    path: url.pathname,
                    url: link.href,
                    timestamp: new Date().toISOString()
                });
            }
        }
    });
}
```

---

## Security Implementation

### Origin Validation

**Configuration:**
```python
# settings.py
EMBEDDED_ALLOWED_ORIGINS = [
    config('PLATFORM_URL', default='https://integrated-platform.company.com'),
]

if DEBUG:
    EMBEDDED_ALLOWED_ORIGINS += [
        'http://localhost:3000',
        'http://localhost:8080',
    ]
```

**Validation Logic:**
```python
def _validate_origin(self, request):
    allowed_origins = getattr(settings, 'EMBEDDED_ALLOWED_ORIGINS', [])

    if not allowed_origins:
        return True  # Allow all (not recommended)

    referer = request.headers.get('Referer', '')

    if not referer:
        return getattr(settings, 'EMBEDDED_ALLOW_NO_REFERER', False)

    for origin in allowed_origins:
        if referer.startswith(origin):
            return True

    return False
```

### CSRF Protection

**Cookie Configuration:**
```python
# Required for cross-domain embedding
CSRF_COOKIE_SAMESITE = 'None' if not DEBUG else 'Lax'
CSRF_COOKIE_HTTPONLY = False  # Must be False for JavaScript
CSRF_COOKIE_SECURE = True if not DEBUG else False

# Trusted origins
CSRF_TRUSTED_ORIGINS = [
    config('PLATFORM_URL', default='https://integrated-platform.company.com'),
]
```

**Best Practices:**
1. Always use HTTPS in production
2. Whitelist specific origins
3. Never use `SAMESITE = 'None'` without HTTPS
4. Validate tokens server-side

### Session Security

**Cookie Configuration:**
```python
# Session cookies for embedded mode
SESSION_COOKIE_SAMESITE = 'None' if not DEBUG else 'Lax'
SESSION_COOKIE_HTTPONLY = True  # Prevent XSS
SESSION_COOKIE_SECURE = True if not DEBUG else False
```

**Token Validation:**
```python
def _validate_platform_token(self, request, token):
    """
    Optional: Validate token with platform API
    """
    import requests
    from django.core.cache import cache

    # Check cache first
    cache_key = f'platform_token_{token[:20]}'
    cached_result = cache.get(cache_key)

    if cached_result is not None:
        return cached_result

    # Call platform API
    platform_api_url = settings.PLATFORM_TOKEN_VALIDATION_URL

    try:
        response = requests.post(
            platform_api_url,
            json={'token': token},
            timeout=5
        )

        is_valid = response.status_code == 200

        # Cache for 5 minutes
        cache.set(cache_key, is_valid, 300)

        return is_valid
    except Exception as e:
        logger.error(f'Token validation error: {e}')
        return False
```

### Permissions Policy

**Configuration:**
```python
EMBEDDED_PERMISSIONS_POLICY = {
    'camera': '()',          # Disabled
    'microphone': '()',      # Disabled
    'geolocation': '()',     # Disabled
    'payment': '()',         # Disabled
    'usb': '()',             # Disabled
    'autoplay': "'self'",    # Same origin only
    'fullscreen': "'self'",  # Same origin only
}
```

**Application:**
```python
def process_response(self, request, response):
    if getattr(request, 'is_embedded', False):
        permissions = settings.EMBEDDED_PERMISSIONS_POLICY
        policy_str = ', '.join([f'{k}={v}' for k, v in permissions.items()])
        response['Permissions-Policy'] = policy_str

    return response
```

---

## Session Management

### Session Synchronization Flow

```
1. User authenticates with parent platform
   ↓
2. Parent generates session token (JWT or custom)
   ↓
3. Parent passes token to iframe:
   a) Via URL: ?platform_session_token=TOKEN
   b) Via PostMessage: {type: 'session_sync', sessionToken: TOKEN}
   ↓
4. Middleware detects token
   ↓
5. Middleware stores in Django session
   ↓
6. Optional: Validate token with platform API
   ↓
7. User authenticated in embedded app
   ↓
8. Session maintained across page navigations
```

### Implementation Example

**Parent Platform:**
```javascript
// Generate or retrieve platform session token
const platformToken = getPlatformSessionToken();

// Method 1: Pass via URL
const iframeUrl = `https://asset-tracker.com/?embedded=minimal&platform_session_token=${platformToken}`;
document.getElementById('asset-tracker').src = iframeUrl;

// Method 2: Pass via PostMessage
iframe.contentWindow.postMessage({
    type: 'session_sync',
    sessionToken: platformToken,
    userData: {
        username: 'john.doe',
        email: 'john@company.com',
        role: 'admin'
    }
}, 'https://asset-tracker.com');
```

**Django Middleware:**
```python
def _sync_session(self, request):
    # Get token from URL
    platform_token = request.GET.get('platform_session_token')

    if platform_token:
        # Store in Django session
        request.session['platform_session_token'] = platform_token

        # Optional: Validate with platform
        if settings.EMBEDDED_VALIDATE_PLATFORM_TOKEN:
            is_valid = self._validate_platform_token(request, platform_token)
            request.session['platform_token_valid'] = is_valid
```

### Session Persistence

**Caching Strategy:**
```python
# Cache platform token validations
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemBackend',
        'LOCATION': 'unique-snowflake',
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}
```

**Session Storage:**
```python
# Store in Django session
request.session['platform_session_token'] = token
request.session['platform_user_data'] = user_data

# Also store in browser sessionStorage (JavaScript)
sessionStorage.setItem('platform_session_token', token);
sessionStorage.setItem('platform_user_data', JSON.stringify(userData));
```

---

## Theme System

### Theme Configuration Structure

```javascript
{
    theme: 'dark' | 'light',
    cssVariables: {
        'primary-color': '#1e88e5',
        'secondary-color': '#ff6f00',
        'navbar-bg': '#1a1a1a',
        'body-bg': '#2d2d2d',
        'text-color': '#e0e0e0',
        'link-color': '#1e88e5',
        // ... more variables
    },
    // Shorthand options
    primaryColor: '#1e88e5',
    secondaryColor: '#ff6f00'
}
```

### Theme Application Methods

#### Method 1: URL Parameters

```bash
http://localhost:8000/?embedded=minimal&primary_color=%231e88e5&navbar_bg=%231a1a1a
```

**Processing:**
```python
# Middleware extracts from query params
theme = {}
for param in ['primary_color', 'secondary_color', 'navbar_bg', 'body_bg']:
    value = request.GET.get(param)
    if value:
        theme[param] = value
```

#### Method 2: HTTP Header

```javascript
fetch('http://localhost:8000/?embedded=minimal', {
    headers: {
        'X-Embedded-Theme': JSON.stringify({
            primary_color: '#1e88e5',
            navbar_bg: '#1a1a1a'
        })
    }
});
```

**Processing:**
```python
# Middleware extracts from header
theme_header = request.headers.get('X-Embedded-Theme')
if theme_header:
    try:
        theme = json.loads(theme_header)
    except json.JSONDecodeError:
        pass
```

#### Method 3: PostMessage

```javascript
iframe.contentWindow.postMessage({
    type: 'theme_update',
    theme: 'dark',
    cssVariables: {
        'primary-color': '#1e88e5',
        'navbar-bg': '#1a1a1a'
    }
}, 'http://localhost:8000');
```

**Processing:**
```javascript
// embedded.js handles theme application
handleThemeUpdate: function(data) {
    const root = document.documentElement;

    // Apply theme attribute
    document.body.setAttribute('data-theme', data.theme);

    // Apply CSS variables
    for (const [key, value] of Object.entries(data.cssVariables)) {
        root.style.setProperty(`--${key}`, value);
    }
}
```

### Theme Persistence

```python
# Middleware stores theme in session
if theme:
    request.session['embedded_theme'] = theme

# On subsequent requests, theme is loaded from session
session_theme = request.session.get('embedded_theme')
```

---

## PostMessage Protocol

### Message Types Reference

#### From Parent to Child

**1. Session Sync**
```javascript
{
    type: 'session_sync',
    sessionToken: 'eyJ0eXAiOiJKV1QiLCJhbGci...',
    userData: {
        username: 'string',
        email: 'string',
        role: 'admin' | 'location_manager' | 'personnel',
        employee_id: 'string',
        first_name: 'string',
        last_name: 'string'
    }
}
```

**2. Theme Update**
```javascript
{
    type: 'theme_update',
    theme: 'dark' | 'light',
    cssVariables: {
        'primary-color': 'string',
        'secondary-color': 'string',
        'navbar-bg': 'string',
        'body-bg': 'string',
        'text-color': 'string',
        'border-color': 'string'
    },
    // Shorthand (alternative to cssVariables)
    primaryColor: 'string',
    secondaryColor: 'string'
}
```

**3. Navigation Update**
```javascript
{
    type: 'navigation_update',
    path: '/assets/',
    params: {
        // Optional query parameters
    }
}
```

**4. Resize**
```javascript
{
    type: 'resize',
    width: 1200,
    height: 800
}
```

**5. Logout**
```javascript
{
    type: 'logout'
}
```

#### From Child to Parent

**1. Ready Notification**
```javascript
{
    type: 'iframe_ready',
    timestamp: '2025-11-20T10:30:00.000Z',
    url: 'http://localhost:8000/?embedded=minimal'
}
```

**2. Navigation Change**
```javascript
{
    type: 'navigation_change',
    path: '/assets/',
    url: 'http://localhost:8000/assets/',
    timestamp: '2025-11-20T10:30:00.000Z'
}
```

**3. Navigation Intent**
```javascript
{
    type: 'navigation_intent',
    path: '/assets/123/',
    url: 'http://localhost:8000/assets/123/',
    timestamp: '2025-11-20T10:30:00.000Z'
}
```

**4. Height Update**
```javascript
{
    type: 'height_update',
    height: 1200,
    timestamp: '2025-11-20T10:30:00.000Z'
}
```

### Custom Events

**Session Synced Event:**
```javascript
// Dispatched when session is synced
window.addEventListener('session_synced', function(event) {
    console.log('Session synced:', event.detail);
    // event.detail contains sessionToken and userData
});
```

**Theme Updated Event:**
```javascript
// Dispatched when theme is updated
window.addEventListener('theme_updated', function(event) {
    console.log('Theme updated:', event.detail);
    // event.detail contains theme configuration
});
```

---

## Testing Guide

### Unit Testing

**Test Embedded Detection:**
```python
from django.test import TestCase, RequestFactory
from asset_tracker.middleware.embedded import EmbeddedModeMiddleware

class EmbeddedModeTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = EmbeddedModeMiddleware(lambda r: None)

    def test_query_parameter_detection(self):
        request = self.factory.get('/?embedded=minimal')
        self.middleware.process_request(request)
        self.assertTrue(request.is_embedded)

    def test_header_detection(self):
        request = self.factory.get('/', HTTP_X_EMBEDDED_MODE='true')
        self.middleware.process_request(request)
        self.assertTrue(request.is_embedded)

    def test_session_token_detection(self):
        request = self.factory.get('/?platform_session_token=test')
        self.middleware.process_request(request)
        self.assertTrue(request.is_embedded)
```

### Integration Testing

**Test PostMessage Communication:**
```html
<!DOCTYPE html>
<html>
<body>
    <iframe id="test-iframe" src="http://localhost:8000/?embedded=minimal"></iframe>

    <script>
        const iframe = document.getElementById('test-iframe');
        const origin = 'http://localhost:8000';

        // Test 1: Verify iframe ready message
        let readyReceived = false;
        window.addEventListener('message', function(event) {
            if (event.origin !== origin) return;

            if (event.data.type === 'iframe_ready') {
                console.log('✅ Test 1 passed: iframe_ready received');
                readyReceived = true;
                runTest2();
            }
        });

        // Test 2: Send theme update
        function runTest2() {
            iframe.contentWindow.postMessage({
                type: 'theme_update',
                theme: 'dark',
                primaryColor: '#1e88e5'
            }, origin);

            setTimeout(() => {
                const body = iframe.contentDocument.body;
                const theme = body.getAttribute('data-theme');
                if (theme === 'dark') {
                    console.log('✅ Test 2 passed: theme applied');
                } else {
                    console.log('❌ Test 2 failed: theme not applied');
                }
            }, 1000);
        }
    </script>
</body>
</html>
```

### Manual Testing Checklist

- [ ] Embedded mode detected via `?embedded=normal`
- [ ] Embedded mode detected via `?embedded=minimal`
- [ ] Embedded mode detected via `?embedded=no-nav`
- [ ] Theme applied via URL parameters
- [ ] Theme applied via PostMessage
- [ ] Session token synced via URL
- [ ] Session token synced via PostMessage
- [ ] Navigation events sent to parent
- [ ] Height updates sent to parent
- [ ] Origin validation works
- [ ] CSRF protection works
- [ ] Works in Chrome
- [ ] Works in Firefox
- [ ] Works in Safari
- [ ] Works in Edge
- [ ] Works on mobile devices

---

## Production Deployment

### Pre-deployment Checklist

**1. Security Configuration**
```python
# settings.py
DEBUG = False
EMBEDDED_VALIDATE_ORIGIN = True
EMBEDDED_ALLOW_NO_REFERER = False
EMBEDDED_VALIDATE_PLATFORM_TOKEN = True
```

**2. HTTPS Configuration**
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

**3. Platform Configuration**
```bash
# .env
PLATFORM_URL=https://integrated-platform.company.com
PLATFORM_TOKEN_VALIDATION_URL=https://integrated-platform.company.com/api/validate-token
```

**4. Static Files**
```bash
python manage.py collectstatic --noinput
```

**5. Migrations**
```bash
python manage.py migrate
```

### Monitoring

**Log Embedded Mode Events:**
```python
import logging
logger = logging.getLogger('asset_tracker.embedded')

# In middleware
logger.info(f'Embedded mode detected: {request.path}')
logger.info(f'Session synced for token: {token[:20]}...')
logger.warning(f'Origin validation failed: {referer}')
```

**Metrics to Track:**
- Embedded mode request count
- Session sync success rate
- Theme sync events
- Origin validation failures
- Token validation failures
- PostMessage errors

### Performance Optimization

**1. Cache Configuration**
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

**2. Static File Optimization**
```bash
# Minify CSS and JS
npm install -g clean-css-cli uglify-js

cleancss -o static/css/embedded.min.css static/css/embedded.css
uglifyjs static/js/embedded.js -o static/js/embedded.min.js
```

**3. CDN Configuration**
```python
# Use CDN for static files
if not DEBUG:
    STATIC_URL = 'https://cdn.company.com/static/'
```

---

## API Reference

### Settings Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `EMBEDDED_MODE_ENABLED` | bool | `True` | Enable embedded mode features |
| `PLATFORM_URL` | str | Required | Parent platform URL |
| `EMBEDDED_SESSION_SYNC_ENABLED` | bool | `True` | Enable session synchronization |
| `EMBEDDED_THEME_SYNC_ENABLED` | bool | `True` | Enable theme synchronization |
| `EMBEDDED_VALIDATE_ORIGIN` | bool | `not DEBUG` | Validate request origin |
| `EMBEDDED_VALIDATE_PLATFORM_TOKEN` | bool | `False` | Validate tokens via API |
| `PLATFORM_TOKEN_VALIDATION_URL` | str | `''` | Platform API endpoint |
| `EMBEDDED_ALLOWED_ORIGINS` | list | `[]` | Whitelist of allowed origins |
| `EMBEDDED_ALLOW_NO_REFERER` | bool | `DEBUG` | Allow requests without referer |
| `EMBEDDED_PERMISSIONS_POLICY` | dict | See docs | Iframe permissions policy |
| `EMBEDDED_DEFAULT_NAV_MODE` | str | `'normal'` | Default navigation mode |
| `EMBEDDED_AUTO_COMPACT` | bool | `True` | Use compact layout |
| `EMBEDDED_HIDE_FOOTER` | bool | `False` | Hide footer in embedded mode |

### URL Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `embedded` | `normal`, `minimal`, `no-nav` | Navigation mode |
| `platform_session_token` | string | Session token from platform |
| `primary_color` | hex color | Primary theme color |
| `secondary_color` | hex color | Secondary theme color |
| `navbar_bg` | hex color | Navigation background |
| `body_bg` | hex color | Page background |
| `debug_embedded` | `true`, `false` | Enable debug logging |

### HTTP Headers

| Header | Type | Description |
|--------|------|-------------|
| `X-Embedded-Mode` | `'true'` | Force embedded mode |
| `X-Embedded-Theme` | JSON | Theme configuration |
| `Referer` | URL | Used for origin validation |

### Context Variables

| Variable | Type | Description |
|----------|------|-------------|
| `is_embedded` | bool | Embedded mode flag |
| `embedded_mode` | str | Navigation mode |
| `platform_origin` | str | Platform URL for PostMessage |
| `custom_theme` | dict | Theme configuration |
| `debug_embedded` | bool | Debug mode flag |

---

**Phase 3: Embedding Configuration Complete**

This comprehensive guide covers all aspects of the embedded mode implementation. For quick start instructions, see `PHASE3_QUICKSTART.md`. For a summary overview, see `PHASE3_SUMMARY.md`.

**Version:** 1.0.0
**Last Updated:** November 20, 2025
