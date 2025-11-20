# Phase 3: Embedding Configuration - Quick Start Guide

**Estimated Time:** 20-30 minutes
**Prerequisites:** Phase 1 and Phase 2 completed

---

## Overview

Phase 3 enables the Asset Movement Tracking System to be embedded seamlessly within the Integrated Business Platform through iframe embedding, session synchronization, and custom theming.

### What You'll Get

- ✅ Automatic embedded mode detection
- ✅ Custom theming from parent platform
- ✅ Session synchronization
- ✅ PostMessage communication
- ✅ Multiple navigation modes
- ✅ Responsive embedded layouts

---

## Quick Setup (10 Minutes)

### Step 1: Collect Static Files

The embedded mode CSS and JavaScript need to be collected:

```bash
python manage.py collectstatic --noinput
```

This copies `static/css/embedded.css` and `static/js/embedded.js` to `staticfiles/`.

### Step 2: Verify Settings

Check that Phase 3 configuration is present in `asset_tracker/settings.py`:

```python
# Should see these middleware (lines 82-83)
'asset_tracker.middleware.embedded.EmbeddedModeMiddleware',
'asset_tracker.middleware.embedded.EmbeddedSecurityMiddleware',

# Should see Phase 3 configuration block (lines 540-652)
# PHASE 3: EMBEDDING CONFIGURATION
EMBEDDED_MODE_ENABLED = True
SESSION_COOKIE_SAMESITE = 'None' if not DEBUG else 'Lax'
```

### Step 3: Update Environment Variables

Update `.env` file (or create from `.env.example`):

```bash
# Platform URL (already configured in Phase 1)
PLATFORM_URL=https://integrated-platform.company.com

# Optional: Platform token validation
EMBEDDED_VALIDATE_PLATFORM_TOKEN=False
PLATFORM_TOKEN_VALIDATION_URL=
```

### Step 4: Start Server

```bash
python manage.py runserver
```

---

## Testing Embedded Mode (10 Minutes)

### Method 1: Query Parameter

Simply add `?embedded=MODE` to any URL:

```bash
# Normal embedded mode
http://localhost:8000/?embedded=normal

# Minimal navigation
http://localhost:8000/?embedded=minimal

# No navigation
http://localhost:8000/?embedded=no-nav
```

You should see:
- Compact layout applied
- `embedded-mode` class on `<body>`
- Embedded CSS loaded

### Method 2: Test in Iframe

Create a test HTML file `test_embedded.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Embedded Mode</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #333;
        }
        .controls {
            margin: 20px 0;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 5px;
        }
        button {
            margin: 5px;
            padding: 10px 15px;
            cursor: pointer;
        }
        iframe {
            border: 2px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Asset Tracker - Embedded Mode Test</h1>

        <div class="controls">
            <h3>Controls</h3>
            <button onclick="changeMode('normal')">Normal Mode</button>
            <button onclick="changeMode('minimal')">Minimal Mode</button>
            <button onclick="changeMode('no-nav')">No Navigation</button>
            <button onclick="applyTheme('dark')">Dark Theme</button>
            <button onclick="applyTheme('light')">Light Theme</button>
            <button onclick="syncSession()">Sync Session</button>
        </div>

        <iframe
            id="asset-tracker"
            src="http://localhost:8000/?embedded=normal"
            width="100%"
            height="800px"
            allow="fullscreen">
        </iframe>
    </div>

    <script>
        const iframe = document.getElementById('asset-tracker');
        const baseUrl = 'http://localhost:8000';

        // Listen for messages from iframe
        window.addEventListener('message', function(event) {
            if (event.origin !== baseUrl) return;

            console.log('📨 Message from iframe:', event.data);

            if (event.data.type === 'iframe_ready') {
                console.log('✅ Asset Tracker is ready!');
            } else if (event.data.type === 'navigation_change') {
                console.log('🧭 Navigation:', event.data.path);
            } else if (event.data.type === 'height_update') {
                console.log('📏 Height:', event.data.height);
            }
        });

        // Change embedded mode
        function changeMode(mode) {
            iframe.src = `${baseUrl}/?embedded=${mode}`;
        }

        // Apply theme
        function applyTheme(theme) {
            const themes = {
                dark: {
                    type: 'theme_update',
                    theme: 'dark',
                    cssVariables: {
                        'primary-color': '#1e88e5',
                        'secondary-color': '#ff6f00',
                        'navbar-bg': '#1a1a1a',
                        'body-bg': '#2d2d2d'
                    }
                },
                light: {
                    type: 'theme_update',
                    theme: 'light',
                    cssVariables: {
                        'primary-color': '#0d6efd',
                        'secondary-color': '#6c757d',
                        'navbar-bg': '#212529',
                        'body-bg': '#ffffff'
                    }
                }
            };

            iframe.contentWindow.postMessage(themes[theme], baseUrl);
            console.log('🎨 Theme applied:', theme);
        }

        // Sync session
        function syncSession() {
            iframe.contentWindow.postMessage({
                type: 'session_sync',
                sessionToken: 'test-session-token-' + Date.now(),
                userData: {
                    username: 'testuser',
                    email: 'test@example.com',
                    role: 'admin'
                }
            }, baseUrl);
            console.log('🔐 Session synced');
        }

        // Auto-sync session when iframe loads
        iframe.onload = function() {
            setTimeout(() => {
                console.log('🔄 Auto-syncing session...');
                syncSession();
            }, 1000);
        };
    </script>
</body>
</html>
```

**To Test:**
1. Save the file as `test_embedded.html`
2. Open in a browser
3. Try the control buttons
4. Check browser console for messages

**Expected Results:**
- Iframe loads with embedded mode active
- Buttons change navigation mode
- Theme buttons update colors
- Console shows PostMessage communication

---

## Embedded Navigation Modes

### Normal Mode (`?embedded=normal`)

**URL:** `http://localhost:8000/?embedded=normal`

**Features:**
- Full navigation bar (56px height)
- All menu items visible
- Standard spacing and fonts
- Best for: Full-featured embedding

**Use Case:** When you want the complete application interface within the platform.

### Minimal Mode (`?embedded=minimal`)

**URL:** `http://localhost:8000/?embedded=minimal`

**Features:**
- Compact navigation (40px height)
- Smaller fonts and spacing
- Reduced padding
- Best for: Space-constrained embedding

**Use Case:** When iframe space is limited or you want a more compact view.

### No Navigation (`?embedded=no-nav`)

**URL:** `http://localhost:8000/?embedded=no-nav`

**Features:**
- Navigation bar completely hidden
- Platform handles all navigation
- Maximum content space
- Best for: Deep platform integration

**Use Case:** When the parent platform provides its own navigation.

---

## Custom Theming

### Method 1: Query Parameters

Pass theme colors via URL:

```bash
http://localhost:8000/?embedded=minimal&primary_color=%231e88e5&navbar_bg=%23263238
```

**Available Parameters:**
- `primary_color` - Primary brand color
- `secondary_color` - Secondary color
- `navbar_bg` - Navigation bar background
- `body_bg` - Page background color

**URL Encoding:** Use `%23` for `#` in color codes.

### Method 2: PostMessage

Send theme updates dynamically:

```javascript
iframe.contentWindow.postMessage({
    type: 'theme_update',
    theme: 'dark',  // or 'light'
    cssVariables: {
        'primary-color': '#1e88e5',
        'secondary-color': '#ff6f00',
        'navbar-bg': '#1a1a1a',
        'body-bg': '#2d2d2d',
        'text-color': '#e0e0e0'
    }
}, 'http://localhost:8000');
```

### Method 3: HTTP Header

Send theme in HTTP header:

```javascript
fetch('http://localhost:8000/?embedded=minimal', {
    headers: {
        'X-Embedded-Theme': JSON.stringify({
            primary_color: '#1e88e5',
            navbar_bg: '#263238'
        })
    }
});
```

---

## Session Synchronization

### Basic Session Sync

```javascript
iframe.contentWindow.postMessage({
    type: 'session_sync',
    sessionToken: 'eyJ0eXAiOiJKV1QiLCJhbGc...',
    userData: {
        username: 'john.doe',
        email: 'john@company.com',
        role: 'admin',
        employee_id: 'EMP001'
    }
}, 'http://localhost:8000');
```

### Session Token via URL

Alternative: Pass token in URL parameter:

```html
<iframe src="http://localhost:8000/?embedded=minimal&platform_session_token=TOKEN"></iframe>
```

The middleware automatically:
1. Detects the token
2. Stores it in session
3. Associates it with the user
4. Enables SSO authentication

---

## PostMessage API Reference

### Messages to Iframe (Parent → Child)

#### Session Sync
```javascript
{
    type: 'session_sync',
    sessionToken: 'string',
    userData: {
        username: 'string',
        email: 'string',
        role: 'string'
    }
}
```

#### Theme Update
```javascript
{
    type: 'theme_update',
    theme: 'dark' | 'light',
    cssVariables: {
        'primary-color': 'string',
        'secondary-color': 'string',
        // ... more variables
    },
    primaryColor: 'string',  // shorthand
    secondaryColor: 'string'  // shorthand
}
```

#### Navigation Update
```javascript
{
    type: 'navigation_update',
    path: '/assets/'
}
```

#### Resize
```javascript
{
    type: 'resize',
    width: number,
    height: number
}
```

#### Logout
```javascript
{
    type: 'logout'
}
```

### Messages from Iframe (Child → Parent)

#### Ready Notification
```javascript
{
    type: 'iframe_ready',
    timestamp: 'ISO-8601',
    url: 'string'
}
```

#### Navigation Change
```javascript
{
    type: 'navigation_change',
    path: 'string',
    url: 'string',
    timestamp: 'ISO-8601'
}
```

#### Navigation Intent
```javascript
{
    type: 'navigation_intent',
    path: 'string',
    url: 'string',
    timestamp: 'ISO-8601'
}
```

#### Height Update
```javascript
{
    type: 'height_update',
    height: number,
    timestamp: 'ISO-8601'
}
```

---

## Integration Example

### Complete Parent Platform Integration

```html
<!DOCTYPE html>
<html>
<head>
    <title>Integrated Business Platform</title>
</head>
<body>
    <div class="platform-header">
        <!-- Platform navigation -->
    </div>

    <div class="platform-content">
        <iframe
            id="asset-tracker"
            src="https://asset-tracker.company.com/?embedded=minimal"
            width="100%"
            height="100%"
            allow="fullscreen">
        </iframe>
    </div>

    <script>
        class AssetTrackerIntegration {
            constructor() {
                this.iframe = document.getElementById('asset-tracker');
                this.origin = 'https://asset-tracker.company.com';
                this.init();
            }

            init() {
                this.setupMessageListener();
                this.waitForReady();
            }

            setupMessageListener() {
                window.addEventListener('message', (event) => {
                    if (event.origin !== this.origin) return;
                    this.handleMessage(event.data);
                });
            }

            handleMessage(data) {
                switch (data.type) {
                    case 'iframe_ready':
                        this.onReady();
                        break;
                    case 'navigation_change':
                        this.updateBreadcrumb(data.path);
                        break;
                    case 'height_update':
                        this.adjustHeight(data.height);
                        break;
                }
            }

            waitForReady() {
                this.iframe.onload = () => {
                    setTimeout(() => this.syncAll(), 500);
                };
            }

            onReady() {
                console.log('Asset Tracker ready');
                this.syncAll();
            }

            syncAll() {
                this.syncSession();
                this.syncTheme();
            }

            syncSession() {
                this.postMessage({
                    type: 'session_sync',
                    sessionToken: this.getPlatformToken(),
                    userData: this.getCurrentUser()
                });
            }

            syncTheme() {
                this.postMessage({
                    type: 'theme_update',
                    theme: 'light',
                    cssVariables: {
                        'primary-color': '#007bff',
                        'navbar-bg': '#343a40'
                    }
                });
            }

            postMessage(data) {
                this.iframe.contentWindow.postMessage(data, this.origin);
            }

            getPlatformToken() {
                // Get from your platform's session
                return localStorage.getItem('platform_token');
            }

            getCurrentUser() {
                // Get from your platform's user session
                return {
                    username: 'john.doe',
                    email: 'john@company.com',
                    role: 'admin'
                };
            }

            updateBreadcrumb(path) {
                // Update platform breadcrumb/navigation
                console.log('Navigate to:', path);
            }

            adjustHeight(height) {
                this.iframe.style.height = height + 'px';
            }
        }

        // Initialize
        const integration = new AssetTrackerIntegration();
    </script>
</body>
</html>
```

---

## Troubleshooting

### Issue 1: Embedded mode not activating

**Check:**
```bash
# View page source and look for:
<body class="embedded-mode">
```

**Solutions:**
1. Verify `?embedded=normal` in URL
2. Check middleware is active: `python manage.py check`
3. Check browser console for errors

### Issue 2: PostMessage not working

**Check console for:**
```
Rejected message from unauthorized origin: https://...
```

**Solutions:**
1. Verify `PLATFORM_URL` in `.env` matches iframe parent origin
2. Check origin in PostMessage call matches exactly
3. Ensure no typos in origin URL (http vs https, trailing slash, etc.)

### Issue 3: Theme not applying

**Solutions:**
1. Run `collectstatic`:
   ```bash
   python manage.py collectstatic --noinput
   ```
2. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
3. Check `embedded.css` is loaded in Network tab
4. Verify CSS variables in browser DevTools

### Issue 4: Session not syncing

**Check:**
```python
# In Django shell
from django.core.cache import cache
cache.get('platform_token_...')  # Should exist after sync
```

**Solutions:**
1. Verify `EMBEDDED_SESSION_SYNC_ENABLED = True` in settings
2. Check token format (should be a string)
3. Verify PostMessage `sessionToken` field name
4. Check browser console for JavaScript errors

---

## Next Steps

### 1. Customize for Your Platform

**Update Colors:**
Edit `static/css/embedded.css` to match your brand:
```css
:root {
    --primary-color: #YOUR_BRAND_COLOR;
    --secondary-color: #YOUR_SECONDARY_COLOR;
}
```

**Custom Layouts:**
Create custom embedded templates by extending `base_embedded.html`.

### 2. Production Configuration

**Update `.env` for production:**
```bash
DEBUG=False
PLATFORM_URL=https://your-actual-platform.com
EMBEDDED_VALIDATE_PLATFORM_TOKEN=True
PLATFORM_TOKEN_VALIDATION_URL=https://your-platform.com/api/validate
```

**Enable HTTPS settings:**
Uncomment in `settings.py`:
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 3. Test All Features

- [ ] Test all three navigation modes
- [ ] Test theme switching
- [ ] Test session synchronization
- [ ] Test PostMessage communication
- [ ] Test in different browsers
- [ ] Test mobile responsive layout
- [ ] Test with actual platform

### 4. Monitor and Optimize

- Enable logging for embedded mode events
- Monitor PostMessage traffic
- Track session synchronization success rate
- Monitor iframe load times

---

## Resources

### Documentation
- **Full Guide:** `docs/PHASE3_EMBEDDING_IMPLEMENTATION.md`
- **Summary:** `PHASE3_SUMMARY.md`
- **Phase 1:** `PHASE1_SUMMARY.md` (SSO)
- **Phase 2:** `PHASE2_SUMMARY.md` (API)

### Code References
- **Middleware:** `asset_tracker/middleware/embedded.py`
- **CSS:** `static/css/embedded.css`
- **JavaScript:** `static/js/embedded.js`
- **Template:** `templates/base_embedded.html`

### External Resources
- [PostMessage API](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)
- [CSS Variables](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [SameSite Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite)

---

**Status:** Ready to Embed
**Estimated Setup Time:** 20-30 minutes
**Integration Complexity:** Low to Medium

✨ **Your application is now ready to be embedded in the Integrated Business Platform!**
