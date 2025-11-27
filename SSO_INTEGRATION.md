# SSO Integration Guide

## Overview
This asset tracking system is now integrated with your Business Platform for Single Sign-On (SSO) and user synchronization.

## Features

### 1. **SSO Authentication**
- Users can log in using their Business Platform credentials
- Automatic user creation on first login
- Falls back to local authentication if SSO is unavailable

### 2. **User Synchronization**
- Sync individual users or all users from Business Platform
- Automatic role mapping
- Keeps user data in sync (email, name, department, etc.)

### 3. **Role Mapping**
Business Platform roles are mapped to Asset Tracker roles:
- `admin` → `admin` (full system access)
- `manager` → `location_manager` (location and staff management)
- `user`/`staff` → `personnel` (basic asset operations)

## Configuration

### 1. Environment Variables
Add these to your `.env` file:

```bash
# Business Platform SSO Configuration
BUSINESS_PLATFORM_URL=http://your-business-platform-url.com
BUSINESS_PLATFORM_API_KEY=your-api-key-here
BUSINESS_PLATFORM_CLIENT_ID=your-client-id-here
BUSINESS_PLATFORM_CLIENT_SECRET=your-client-secret-here
```

### 2. Business Platform API Endpoints
Your Business Platform should provide these endpoints:

- **Authentication**: `POST /api/auth/login/`
  ```json
  Request: {"username": "user", "password": "pass"}
  Response: {"username": "user", "email": "user@example.com", "role": "admin", ...}
  ```

- **User Info**: `GET /api/users/info/?username=user`
  ```json
  Response: {"username": "user", "email": "user@example.com", "first_name": "John", ...}
  ```

- **User List**: `GET /api/users/list/`
  ```json
  Response: {"users": [{"username": "user1", ...}, {"username": "user2", ...}]}
  ```

## Installation

### 1. Install Required Packages
```bash
cd /home/wongivan852/projects/asset-movement-tracking-system
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Business Platform URL
Update your `.env` file with the correct Business Platform URL and credentials.

## Usage

### Manual User Sync

#### Sync All Users
```bash
python manage.py sync_users
```

#### Sync Specific User
```bash
python manage.py sync_users --username john.doe
```

#### Dry Run (Preview Changes)
```bash
python manage.py sync_users --dry-run
```

### Automatic SSO Login
1. Users navigate to the login page
2. Enter their Business Platform credentials
3. System authenticates against Business Platform
4. User is automatically created/updated in Asset Tracker
5. User is logged in

### Programmatic Usage

```python
from accounts.sso import sso_client

# Authenticate a user
user_data = sso_client.authenticate_user('username', 'password')

# Get user info
user_info = sso_client.get_user_info(username='john.doe')

# Sync all users
created, updated, errors = sso_client.sync_all_users()

# Sync single user
result = sso_client.sync_user(user_data)
```

## User Data Mapping

| Business Platform Field | Asset Tracker Field |
|------------------------|---------------------|
| username               | username            |
| email                  | email               |
| first_name             | first_name          |
| last_name              | last_name           |
| role                   | role (mapped)       |
| phone                  | phone               |
| department             | department          |
| employee_id            | employee_id         |
| is_active              | is_active           |

## Troubleshooting

### SSO Not Working
1. Check Business Platform URL is correct in `.env`
2. Verify API key/credentials are valid
3. Check logs: `tail -f logs/django.log`
4. Test Business Platform API manually:
   ```bash
   curl http://your-platform-url/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username":"test","password":"test"}'
   ```

### Users Not Syncing
1. Verify API endpoints are accessible
2. Check user data format matches expected structure
3. Run sync with error reporting:
   ```bash
   python manage.py sync_users
   ```

### Fallback to Local Auth
If SSO fails, users can still authenticate locally with:
- Existing local passwords
- SSO will be attempted first, then local auth

## Scheduled Sync (Optional)

To automatically sync users periodically, add a cron job:

```bash
# Sync users every day at 2 AM
0 2 * * * cd /home/wongivan852/projects/asset-movement-tracking-system && venv/bin/python manage.py sync_users
```

Or use Django-celery-beat for scheduled tasks.

## Security Notes

1. **API Keys**: Keep API keys secure and never commit to Git
2. **HTTPS**: Use HTTPS for production Business Platform URL
3. **Token Expiry**: JWT tokens expire after 24 hours
4. **Password Storage**: SSO users have unusable passwords (authenticate via Business Platform only)

## Support

For issues or questions:
1. Check Django logs: `logs/django.log`
2. Review Business Platform API documentation
3. Contact system administrator
