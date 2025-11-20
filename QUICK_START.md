# Asset Management System - Quick Start Guide
## Installation with SSO Integration for Business Platform

---

## 🎉 Setup Complete!

Your Asset Management Tracking System has been configured with comprehensive SSO integration support. All code changes have been committed and pushed to the repository.

---

## 📋 What Was Installed

### ✅ Core Features Added

1. **SSO Authentication Support**
   - SAML 2.0 for enterprise SSO (Azure AD, Okta, Google Workspace)
   - OAuth 2.0 / OpenID Connect for modern authentication
   - LDAP / Active Directory for corporate directory integration

2. **Automated Installation**
   - One-command installation script (`install.sh`)
   - Automatic system dependency installation
   - PostgreSQL database setup
   - Production server configuration (Gunicorn + Nginx)

3. **Enhanced Security**
   - HTTPS support
   - CORS configuration for SSO
   - Secure credential management
   - Enhanced session security

4. **Comprehensive Documentation**
   - Installation Guide (`INSTALLATION_GUIDE.md`)
   - SSO Integration Guide (`SSO_INTEGRATION.md`)
   - Configuration templates (`.env.example`)
   - Changelog (`CHANGELOG.md`)

---

## 🚀 How to Install

### Option 1: Automated Installation (Recommended)

Run the automated installation script:

```bash
cd /home/user/asset-movement-tracking-system
sudo ./install.sh
```

This will:
- Install all system dependencies
- Set up PostgreSQL database
- Create Python virtual environment
- Install all Python packages (including SSO libraries)
- Create configuration files
- Set up systemd service
- Configure Nginx
- Start the application

**Time required**: 10-15 minutes

### Option 2: Manual Installation

Follow the detailed steps in `INSTALLATION_GUIDE.md` for manual installation with full control over each step.

---

## 🔐 Configure SSO

After installation, configure SSO integration with your Business Platform:

### Step 1: Choose Your SSO Method

**SAML 2.0** (Recommended for Enterprise)
- Best for: Azure AD, Okta, Google Workspace
- Protocol: Industry standard SAML
- See: `SSO_INTEGRATION.md` section "SAML 2.0 Configuration"

**OAuth 2.0 / OIDC**
- Best for: Modern web applications
- Protocol: OAuth 2.0 / OpenID Connect
- See: `SSO_INTEGRATION.md` section "OAuth 2.0 Configuration"

**LDAP / Active Directory**
- Best for: Corporate directory integration
- Protocol: LDAP
- See: `SSO_INTEGRATION.md` section "LDAP Configuration"

### Step 2: Edit Configuration File

```bash
cd /home/user/asset-movement-tracking-system
nano .env
```

**For SAML 2.0**, update these settings:
```bash
SSO_ENABLED=True
SSO_TYPE=SAML
SITE_URL=https://your-domain.com

SAML_ENTITY_ID=https://your-domain.com/accounts/sso/saml/metadata/
SAML_SSO_URL=https://your-idp.com/sso
SAML_X509_CERT=YOUR_CERTIFICATE_HERE
```

**For OAuth 2.0**, update these settings:
```bash
SSO_ENABLED=True
SSO_TYPE=OAUTH

OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_AUTHORIZATION_URL=https://your-idp.com/authorize
OAUTH_TOKEN_URL=https://your-idp.com/token
OAUTH_USERINFO_URL=https://your-idp.com/userinfo
```

**For LDAP**, update these settings:
```bash
SSO_ENABLED=True
SSO_TYPE=LDAP

LDAP_SERVER_URI=ldap://your-ad-server:389
LDAP_BIND_DN=CN=Service Account,DC=company,DC=com
LDAP_BIND_PASSWORD=your-password
LDAP_USER_SEARCH_BASE=OU=Users,DC=company,DC=com
```

### Step 3: Configure Your Identity Provider

Add this application to your SSO provider with:

**Service Provider URLs:**
- Entity ID: `https://your-domain.com/accounts/sso/saml/metadata/`
- ACS URL: `https://your-domain.com/accounts/sso/saml/acs/`
- Login URL: `https://your-domain.com/accounts/sso/login/`

### Step 4: Restart Application

```bash
sudo systemctl restart asset-tracker
```

---

## 🧪 Test Your Installation

### 1. Check Application Status

```bash
sudo systemctl status asset-tracker
```

Should show: **active (running)** ✅

### 2. Access the Application

Open your browser and navigate to:
- **Main URL**: http://your-server-ip or https://your-domain.com
- **Admin Interface**: http://your-server-ip/admin/
- **SSO Login**: http://your-server-ip/accounts/sso/login/

### 3. Test SSO Login

1. Go to login page
2. Click **"Login with SSO"** button
3. Authenticate with your corporate credentials
4. You should be logged in automatically ✅

### 4. Verify User Creation

SSO users are automatically created on first login with:
- Username from SSO
- Email from SSO
- Name from SSO
- Default role: Personnel (configurable)

---

## 📚 Documentation Index

| Document | Description |
|----------|-------------|
| **INSTALLATION_GUIDE.md** | Complete installation instructions |
| **SSO_INTEGRATION.md** | Detailed SSO configuration for all providers |
| **DEPLOYMENT.md** | Production deployment guide |
| **README.md** | Feature overview and usage |
| **CHANGELOG.md** | Version history and changes |
| **.env.example** | Configuration template |

---

## 🔑 Default Access

### Local Admin Account

If you created a superuser during installation:
- Username: admin (or what you specified)
- Password: (what you specified)

### SSO Users

SSO users are created automatically on first login.

---

## 💡 Common Configurations

### Azure AD (SAML)

```bash
SSO_TYPE=SAML
SAML_SSO_URL=https://login.microsoftonline.com/YOUR_TENANT_ID/saml2
SAML_ATTRIBUTE_MAPPING_EMAIL=http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress
SAML_ATTRIBUTE_MAPPING_USERNAME=http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name
```

### Okta (SAML)

```bash
SSO_TYPE=SAML
SAML_SSO_URL=https://your-domain.okta.com/app/YOUR_APP_ID/sso/saml
```

### Google Workspace (SAML)

```bash
SSO_TYPE=SAML
SAML_SSO_URL=https://accounts.google.com/o/saml2/idp?idpid=YOUR_IDP_ID
```

### Active Directory (LDAP)

```bash
SSO_TYPE=LDAP
LDAP_SERVER_URI=ldap://dc01.company.com:389
LDAP_USER_SEARCH_FILTER=(sAMAccountName=%(user)s)
```

---

## 🛡️ Security Checklist

Before going to production:

- [ ] HTTPS enabled with valid SSL certificate
- [ ] `DEBUG=False` in .env file
- [ ] Strong `SECRET_KEY` configured
- [ ] Database password is secure and unique
- [ ] Firewall configured (ports 80, 443 only)
- [ ] SSO properly configured and tested
- [ ] Regular backups enabled
- [ ] Monitoring and logging enabled

---

## 🔧 Troubleshooting

### Application won't start

```bash
# Check logs
sudo journalctl -u asset-tracker -n 50

# Check Django errors
cd /home/user/asset-movement-tracking-system
source venv/bin/activate
python manage.py check
```

### SSO authentication fails

```bash
# Check application logs
tail -f /home/user/asset-movement-tracking-system/logs/django.log

# Verify SSO configuration
grep SSO /home/user/asset-movement-tracking-system/.env
```

### Database connection issues

```bash
# Test database connection
sudo -u postgres psql -d asset_tracker -c "SELECT 1;"

# Check database credentials in .env
cat /home/user/asset-movement-tracking-system/.env | grep DB_
```

---

## 🆘 Getting Help

### Documentation
1. Read `INSTALLATION_GUIDE.md` for detailed installation steps
2. Read `SSO_INTEGRATION.md` for SSO configuration help
3. Check `CHANGELOG.md` for version information

### Logs
- Application logs: `logs/django.log`
- System logs: `sudo journalctl -u asset-tracker`
- Nginx logs: `/var/log/nginx/error.log`

### Support
- Contact your IT administrator for infrastructure support
- Contact your Identity Provider administrator for SSO support
- Check GitHub repository for updates and issues

---

## 🎯 Next Steps

1. **Configure SSO**: Complete SSO setup with your Identity Provider
2. **Enable HTTPS**: Install SSL certificate for production use
3. **Import Data**: Import existing assets and locations
4. **Train Users**: Provide user training and documentation
5. **Set Up Backups**: Configure automated database backups
6. **Monitor**: Set up application monitoring and alerts

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Users / Browsers                    │
└─────────────────────┬───────────────────────────────┘
                      │
                      │ HTTPS
                      │
┌─────────────────────▼───────────────────────────────┐
│                     Nginx                            │
│              (Reverse Proxy)                         │
└─────────────────────┬───────────────────────────────┘
                      │
                      │ Unix Socket
                      │
┌─────────────────────▼───────────────────────────────┐
│                   Gunicorn                           │
│              (WSGI Server)                           │
└─────────────────────┬───────────────────────────────┘
                      │
                      │
┌─────────────────────▼───────────────────────────────┐
│              Django Application                      │
│  ┌──────────────────────────────────────────────┐  │
│  │         SSO Authentication                    │  │
│  │  • SAML 2.0    • OAuth    • LDAP            │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │         Asset Management                      │  │
│  │  • Assets  • Locations  • Movements          │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────┘
                      │
                      │
┌─────────────────────▼───────────────────────────────┐
│                PostgreSQL Database                   │
│              (Asset Data Storage)                    │
└──────────────────────────────────────────────────────┘
                      │
                      │
┌─────────────────────▼───────────────────────────────┐
│            Identity Provider (IdP)                   │
│  Azure AD / Okta / Google / AD / Custom             │
└──────────────────────────────────────────────────────┘
```

---

## ✨ Features

### User Management
- ✅ SSO Authentication (SAML, OAuth, LDAP)
- ✅ Local authentication (optional)
- ✅ Role-based access control
- ✅ Just-in-Time user provisioning
- ✅ Automatic role mapping

### Asset Management
- ✅ Comprehensive asset registry
- ✅ Category management
- ✅ Location tracking
- ✅ Movement tracking
- ✅ Stock taking
- ✅ Audit trail

### Security
- ✅ HTTPS support
- ✅ CSRF protection
- ✅ SQL injection protection
- ✅ XSS protection
- ✅ Session security
- ✅ Audit logging

---

## 🔄 Version Information

**Current Version**: 1.1.0

**Changes in 1.1.0**:
- Added SSO integration (SAML, OAuth, LDAP)
- Added automated installation script
- Enhanced security features
- Comprehensive documentation

See `CHANGELOG.md` for complete version history.

---

## 📞 Contact

For installation support:
- **Technical Issues**: Check logs and documentation
- **SSO Configuration**: Contact your IT department
- **Identity Provider**: Contact your IdP administrator

---

**Installation Ready!** 🚀

Run `sudo ./install.sh` to begin installation, or follow `INSTALLATION_GUIDE.md` for manual installation.

After installation, configure SSO using `SSO_INTEGRATION.md` guide.
