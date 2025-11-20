# Changelog

All notable changes to the Asset Management Tracking System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-20

### Added
- **SSO Integration**: Comprehensive Single Sign-On support for Business Platform integration
  - SAML 2.0 authentication backend
  - OAuth 2.0 / OpenID Connect authentication backend
  - LDAP / Active Directory authentication backend
  - Support for multiple IdP providers (Azure AD, Okta, Google Workspace, etc.)
  - Just-in-Time (JIT) user provisioning
  - Automatic role mapping from SSO groups
  - SSO user tracking and audit fields in User model

- **Installation Automation**:
  - Automated installation script (`install.sh`) for quick deployment
  - One-command setup for production environments
  - Automatic PostgreSQL database creation and configuration
  - Systemd service configuration
  - Nginx reverse proxy setup

- **Enhanced Security**:
  - WhiteNoise for static file serving
  - CORS support for SSO integration
  - Enhanced security middleware
  - Configurable HTTPS enforcement
  - SSL/TLS support for LDAP

- **Documentation**:
  - Comprehensive SSO Integration Guide (`SSO_INTEGRATION.md`)
  - Detailed Installation Guide (`INSTALLATION_GUIDE.md`)
  - Environment configuration template (`.env.example`)
  - Support for multiple SSO providers with examples

- **Dependencies**:
  - python3-saml (1.16.0) for SAML authentication
  - django-allauth (0.61.1) for OAuth/OIDC
  - python-ldap (3.4.4) and django-auth-ldap (4.6.0) for LDAP
  - gunicorn (21.2.0) for production deployment
  - whitenoise (6.6.0) for static file serving
  - django-cors-headers (4.3.1) for CORS support

### Changed
- **User Model**: Extended with SSO integration fields
  - `sso_user`: Boolean flag for SSO users
  - `sso_provider`: Track which SSO provider authenticated the user
  - `sso_id`: Unique identifier from SSO provider
  - `last_sso_login`: Timestamp of last SSO login

- **Authentication System**:
  - Multiple authentication backends support
  - Configurable authentication flow (SSO-only or hybrid)
  - Enhanced user provisioning logic

- **Settings**:
  - Added comprehensive SSO configuration options
  - Environment-based SSO provider selection
  - Configurable attribute mapping for SSO providers
  - Role mapping configuration

- **Login Interface**:
  - Added "Login with SSO" button when SSO is enabled
  - Improved login page layout
  - Better error handling and user feedback

### Fixed
- Enhanced error handling for SSO authentication failures
- Improved logging for SSO events
- Better validation of SSO configuration

### Security
- All SSO communications must use HTTPS in production
- Enhanced session security for SSO users
- CSRF protection for SSO endpoints
- Secure credential storage in environment variables

## [1.0.0] - 2025-11-20

### Added
- Initial release of Asset Movement Tracking System
- User management with role-based access control
- Asset registry and management
- Location management (Hong Kong and Shenzhen)
- Movement tracking between locations
- Asset reception and acknowledgement system
- Remarks and comments system
- Stock taking functionality
- Real-time dashboard with statistics
- Audit trail and activity logging
- Notification system for overdue items
- Responsive design with Bootstrap 5
- PostgreSQL database support
- SQLite support for development
- Complete documentation

### Features
- Multi-user system with three role types:
  - Administrator: Full system access
  - Location Manager: Location and staff management
  - Personnel: Basic asset operations
- Comprehensive asset tracking:
  - Unique asset identifiers
  - Category management
  - Financial tracking
  - Status management
  - Complete lifecycle tracking
- Movement tracking:
  - Unique tracking numbers
  - Status progression
  - Acknowledgement workflow
  - Condition reporting
- Dashboard:
  - Real-time statistics
  - Asset distribution charts
  - Recent activity feed
  - Alert notifications
- Security:
  - Django authentication
  - Role-based permissions
  - Activity audit trail
  - CSRF protection
  - SQL injection protection

### Technical
- Django 4.2.23 framework
- Bootstrap 5 responsive UI
- Chart.js for data visualization
- PostgreSQL production database
- SQLite development database
- Modular Django app architecture
- Comprehensive test coverage

---

## Version History

- **1.1.0**: SSO Integration and Enhanced Deployment
- **1.0.0**: Initial Release

---

## Upgrade Guide

### From 1.0.0 to 1.1.0

1. **Backup your database**:
   ```bash
   pg_dump asset_tracker > backup_before_upgrade.sql
   ```

2. **Pull latest code**:
   ```bash
   git pull origin main
   ```

3. **Update dependencies**:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Configure SSO** (optional):
   - Copy new settings from `.env.example`
   - Add SSO configuration to your `.env` file
   - Configure your SSO Identity Provider

6. **Collect static files**:
   ```bash
   python manage.py collectstatic --noinput
   ```

7. **Restart application**:
   ```bash
   sudo systemctl restart asset-tracker
   ```

---

## Notes

- SSO integration requires HTTPS in production
- Existing users can continue using local authentication
- SSO and local authentication can coexist
- Database migrations are backward compatible
- No breaking changes for existing installations
