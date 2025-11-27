# 🎯 Asset App SSO Integration - Quick Reference

## ✅ Status: FULLY INTEGRATED AND OPERATIONAL

Your Asset Tracking System is fully integrated with Business Platform SSO authentication including JWT token support.

---

## 📋 What's Working

✅ **Asset App Activated** - All asset management features enabled  
✅ **SSO Authentication** - Business Platform login integrated  
✅ **JWT Token Support** - Full JWT token generation, validation, and refresh  
✅ **SSO API Endpoints** - 5 API endpoints for token management  
✅ **User Synchronization** - Automatic user sync from Business Platform  
✅ **Role Mapping** - Business Platform roles mapped to asset permissions  
✅ **Protected Views** - All asset endpoints require authentication  
✅ **User Relationships** - Assets linked to SSO-authenticated users  
✅ **Bearer Token Auth** - Automatic authentication via JWT in headers  

---

## 🚀 Quick Start

### 1. Start the Server
```bash
cd /home/wongivan852/projects/asset-movement-tracking-system
source venv/bin/activate
python manage.py runserver
```

### 2. Access the Application
- **Login**: http://localhost:8000/accounts/login/
- **Assets**: http://localhost:8000/assets/
- **Dashboard**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin/

### 3. Get JWT Token via API
```bash
curl -X POST http://localhost:8000/accounts/api/sso/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"your-username","password":"your-password"}'
```

### 4. Use Token to Access Assets
```bash
curl http://localhost:8000/assets/ \
  -H "Authorization: Bearer <your-access-token>"
```

### 5. Sync Users from Business Platform
```bash
python manage.py sync_users
```

---

## 🔑 Key URLs

| Feature | URL | Auth Required |
|---------|-----|---------------|
| Login | `/accounts/login/` | No |
| Asset List | `/assets/` | ✅ Yes |
| Create Asset | `/assets/create/` | ✅ Yes |
| Asset Detail | `/assets/<id>/` | ✅ Yes |
| Categories | `/assets/categories/` | ✅ Yes |
| Dashboard | `/` | ✅ Yes |

## 🔐 SSO API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/accounts/api/sso/token/` | POST | Obtain JWT tokens |
| `/accounts/api/sso/refresh/` | POST | Refresh access token |
| `/accounts/api/sso/validate/` | POST | Validate JWT token |
| `/accounts/api/sso/user/info/` | GET | Get user information |
| `/accounts/api/sso/users/list/` | GET | List all users |

---

## 👥 User Roles

| Business Platform | Asset Tracker | Permissions |
|------------------|---------------|-------------|
| `admin` | `admin` | Full system access |
| `manager` | `location_manager` | Manage locations & assets |
| `user`/`staff` | `personnel` | View & update assigned assets |

---

## 🔧 Configuration

### Environment Variables (`.env`)
```bash
# Business Platform SSO
BUSINESS_PLATFORM_URL=http://localhost:8001
BUSINESS_PLATFORM_API_KEY=your-api-key
BUSINESS_PLATFORM_CLIENT_ID=your-client-id
BUSINESS_PLATFORM_CLIENT_SECRET=your-client-secret

# Database (optional - defaults to SQLite)
DB_NAME=asset_tracker_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Security
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 📊 Database Schema

### Asset Model
```python
Asset
├── asset_id (unique identifier)
├── name, description, category
├── responsible_person → User (SSO)
├── created_by → User (SSO)
├── current_location → Location
└── status, condition, etc.
```

### User Model (SSO-Synced)
```python
User
├── username, email, name
├── role (mapped from Business Platform)
├── department, employee_id
└── assigned_assets → Asset[]
```

---

## 🧪 Testing

### Verify Integration
```bash
python verify_asset_integration.py
```

### Test SSO Connection
```bash
python test_sso.py
```

### Run Django Tests
```bash
python manage.py test
```

### Check System
```bash
python manage.py check
```

---

## 📝 Common Tasks

### Create a New Asset
1. Login via SSO
2. Navigate to `/assets/create/`
3. Fill in asset details
4. Assign to user (optional)
5. Submit form

### Assign Asset to User
```python
# Via Django shell
python manage.py shell

from assets.models import Asset
from accounts.models import User

asset = Asset.objects.get(asset_id='LAPTOP-001')
user = User.objects.get(username='john.doe')
asset.responsible_person = user
asset.save()
```

### Sync All Users
```bash
python manage.py sync_users
```

### Sync Specific User
```bash
python manage.py sync_users --username john.doe
```

---

## 🔍 Verification Results

```
✓ Accounts app installed
✓ Assets app installed
✓ Business Platform SSO backend configured
✓ Local authentication fallback enabled
✓ Business Platform URL: http://localhost:8001
✓ API Key: Configured
✓ User model: User
✓ Asset model: Asset
✓ Asset → User relationships configured
✓ All asset views require authentication
✓ URL routing configured correctly

Status: ✅ ACTIVE AND CONFIGURED
```

---

## 🐛 Troubleshooting

### Can't access assets
→ Ensure you're logged in via `/accounts/login/`

### User not found
→ Run `python manage.py sync_users`

### SSO not working
→ Check `.env` file has correct Business Platform URL and credentials

### Permission denied
→ Verify user role is correct (`python manage.py shell` → check user.role)

### Assets not showing
→ Check database: `python manage.py shell` → `Asset.objects.count()`

---

## 📚 Documentation

- **Full Integration Guide**: `ASSET_SSO_INTEGRATION.md`
- **SSO Setup**: `SSO_INTEGRATION.md`
- **Deployment**: `DEPLOYMENT.md`
- **Main README**: `README.md`

---

## 🎉 Success!

Your asset tracking system is fully integrated with Business Platform SSO. Users can:
- ✅ Login with Business Platform credentials
- ✅ Access and manage assets
- ✅ Be assigned as asset owners
- ✅ Track asset history with full audit trail

**System is ready for use!**

---

*Last verified: November 26, 2025*
*System check: 0 issues*
