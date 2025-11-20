# Asset Management Tracking System
## Installation Guide with SSO Integration

This guide provides step-by-step instructions to install and configure the Asset Management Tracking System on your device with SSO integration for your Business Platform.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Installation](#quick-installation)
3. [Manual Installation](#manual-installation)
4. [SSO Configuration](#sso-configuration)
5. [Post-Installation](#post-installation)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Operating System
- **Supported**: Ubuntu 20.04+, Debian 11+, CentOS 8+, RHEL 8+, or Linux Mint 20+
- **Architecture**: x86_64 (64-bit)
- **Hardware**: Dell OptiPlex or equivalent

### Software Prerequisites
- Python 3.8 or higher
- PostgreSQL 12+ (recommended for production)
- Nginx (for production deployment)
- 4GB RAM minimum (8GB recommended)
- 20GB disk space minimum

### Network Requirements
- Internet connectivity for package installation
- Access to your SSO Identity Provider
- HTTPS certificate (recommended for production)
- Ports: 80 (HTTP), 443 (HTTPS), 5432 (PostgreSQL - internal)

---

## Quick Installation

### Automated Installation Script

The easiest way to install the system is using the provided installation script:

```bash
cd /home/user/asset-movement-tracking-system
sudo ./install.sh
```

This script will:
1. Install all system dependencies
2. Set up PostgreSQL database
3. Create Python virtual environment
4. Install Python dependencies (including SSO libraries)
5. Create `.env` configuration file
6. Run database migrations
7. Set up systemd service
8. Configure Nginx reverse proxy
9. Start the application

**Note**: The script will prompt you for confirmation before proceeding. It will also display database credentials - **save these securely**!

### What the Script Does

The installation script performs the following:

- **System packages**: Python 3, PostgreSQL, Nginx, Git, build tools, SSL libraries, SAML libraries
- **Database**: Creates `asset_tracker` database and user with secure password
- **Python environment**: Creates virtual environment and installs all dependencies including:
  - Django 4.2.23
  - SAML authentication (python3-saml)
  - OAuth/OIDC support (django-allauth)
  - LDAP support (python-ldap, django-auth-ldap)
  - Production server (gunicorn)
  - And more...
- **Configuration**: Generates `.env` file with secure defaults
- **Service**: Creates systemd service for automatic startup
- **Web server**: Configures Nginx as reverse proxy

---

## Manual Installation

If you prefer manual installation or need more control:

### Step 1: Install System Dependencies

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev \
    postgresql postgresql-contrib libpq-dev \
    nginx git curl build-essential libssl-dev libffi-dev \
    libxml2-dev libxslt1-dev libsasl2-dev xmlsec1
```

#### CentOS/RHEL:
```bash
sudo yum install -y python3 python3-pip python3-devel \
    postgresql postgresql-server postgresql-devel \
    nginx git curl gcc openssl-devel libffi-devel \
    libxml2-devel libxslt-devel openldap-devel xmlsec1
```

### Step 2: Set Up PostgreSQL

```bash
# Initialize PostgreSQL (CentOS/RHEL only)
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql <<EOF
CREATE DATABASE asset_tracker;
CREATE USER asset_tracker_user WITH PASSWORD 'your_secure_password';
ALTER ROLE asset_tracker_user SET client_encoding TO 'utf8';
ALTER ROLE asset_tracker_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE asset_tracker_user SET timezone TO 'Asia/Hong_Kong';
GRANT ALL PRIVILEGES ON DATABASE asset_tracker TO asset_tracker_user;
EOF
```

### Step 3: Set Up Python Environment

```bash
cd /home/user/asset-movement-tracking-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Python dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
nano .env
```

**Required settings**:
- `SECRET_KEY`: Generate with: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- `DEBUG=False` for production
- Database credentials
- `SITE_URL`: Your domain or IP address
- SSO configuration (see next section)

### Step 5: Initialize Django Application

```bash
# Activate virtual environment
source venv/bin/activate

# Create logs directory
mkdir -p logs

# Run database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

### Step 6: Set Up Systemd Service

Create `/etc/systemd/system/asset-tracker.service`:

```ini
[Unit]
Description=Asset Management Tracking System
After=network.target postgresql.service

[Service]
Type=notify
User=YOUR_USERNAME
Group=YOUR_USERNAME
WorkingDirectory=/home/user/asset-movement-tracking-system
Environment="PATH=/home/user/asset-movement-tracking-system/venv/bin"
ExecStart=/home/user/asset-movement-tracking-system/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/home/user/asset-movement-tracking-system/asset-tracker.sock \
    asset_tracker.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable asset-tracker
sudo systemctl start asset-tracker
sudo systemctl status asset-tracker
```

### Step 7: Configure Nginx

Create `/etc/nginx/sites-available/asset-tracker`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }

    location /static/ {
        alias /home/user/asset-movement-tracking-system/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/user/asset-movement-tracking-system/media/;
    }

    location / {
        proxy_pass http://unix:/home/user/asset-movement-tracking-system/asset-tracker.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 600s;
        proxy_read_timeout 600s;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/asset-tracker /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

## SSO Configuration

### Overview

The system supports three SSO methods:

1. **SAML 2.0** - Best for enterprise SSO (Azure AD, Okta, Google Workspace)
2. **OAuth 2.0 / OIDC** - Modern web authentication
3. **LDAP / Active Directory** - Corporate directory integration

### Configuring SAML 2.0

#### Step 1: Gather IdP Information

From your Identity Provider, collect:
- Entity ID (IdP Identifier)
- SSO URL (Single Sign-On Service URL)
- SLO URL (Single Logout Service URL) - Optional
- X.509 Certificate

#### Step 2: Configure Your IdP

Add this application as a Service Provider with:
- **Entity ID**: `https://your-domain.com/accounts/sso/saml/metadata/`
- **ACS URL**: `https://your-domain.com/accounts/sso/saml/acs/`
- **SLS URL**: `https://your-domain.com/accounts/sso/saml/sls/`

#### Step 3: Update .env File

```bash
SSO_ENABLED=True
SSO_TYPE=SAML
SITE_URL=https://your-domain.com

SAML_ENTITY_ID=https://your-domain.com/accounts/sso/saml/metadata/
SAML_IDP_ENTITY_ID=https://idp.yourcompany.com/metadata
SAML_SSO_URL=https://idp.yourcompany.com/sso
SAML_SLO_URL=https://idp.yourcompany.com/slo
SAML_X509_CERT=MIIDXTCCAkWgAwIBAgIJALmVVuDWu4NYMA0GCSqGSIb...

# Adjust attribute names based on your IdP
SAML_ATTRIBUTE_MAPPING_EMAIL=email
SAML_ATTRIBUTE_MAPPING_USERNAME=username
SAML_ATTRIBUTE_MAPPING_FIRST_NAME=firstName
SAML_ATTRIBUTE_MAPPING_LAST_NAME=lastName
```

#### Step 4: Restart Application

```bash
sudo systemctl restart asset-tracker
```

#### Step 5: Test SAML Login

1. Navigate to: `https://your-domain.com/accounts/login/`
2. Click "Login with SSO"
3. You should be redirected to your IdP
4. After authentication, you'll be redirected back

### Configuring OAuth 2.0 / OIDC

#### For Microsoft Azure AD:

```bash
SSO_ENABLED=True
SSO_TYPE=OAUTH
SITE_URL=https://your-domain.com

OAUTH_ENABLED=True
OAUTH_PROVIDER=azure
OAUTH_CLIENT_ID=your-application-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_AUTHORIZATION_URL=https://login.microsoftonline.com/common/oauth2/v2.0/authorize
OAUTH_TOKEN_URL=https://login.microsoftonline.com/common/oauth2/v2.0/token
OAUTH_USERINFO_URL=https://graph.microsoft.com/v1.0/me
OAUTH_SCOPE=openid profile email User.Read
```

### Configuring LDAP / Active Directory

```bash
SSO_ENABLED=True
SSO_TYPE=LDAP

LDAP_ENABLED=True
LDAP_SERVER_URI=ldap://dc01.contoso.com:389
LDAP_BIND_DN=CN=AppService,OU=Service Accounts,DC=contoso,DC=com
LDAP_BIND_PASSWORD=SecurePassword123!
LDAP_USER_SEARCH_BASE=OU=Employees,DC=contoso,DC=com
LDAP_USER_SEARCH_FILTER=(sAMAccountName=%(user)s)
LDAP_USE_TLS=True
```

### Role Mapping

To automatically assign roles based on SSO groups:

```bash
SSO_ROLE_MAPPING_ENABLED=True
SSO_ADMIN_GROUPS=Asset-Admins,IT-Admins
SSO_MANAGER_GROUPS=Asset-Managers,Location-Managers
SSO_STAFF_GROUPS=Asset-Users
SSO_DEFAULT_ROLE=personnel
```

---

## Post-Installation

### Enable HTTPS (Required for Production SSO)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Update .env for HTTPS
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Restart application
sudo systemctl restart asset-tracker
```

### Configure Firewall

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw enable
```

### Set Up Backups

#### Database Backup:
```bash
# Create backup script
cat > /usr/local/bin/backup-asset-tracker.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/asset-tracker"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
pg_dump asset_tracker > $BACKUP_DIR/db_backup_$DATE.sql
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete
EOF

chmod +x /usr/local/bin/backup-asset-tracker.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-asset-tracker.sh") | crontab -
```

---

## Verification

### Check System Status

```bash
# Check application service
sudo systemctl status asset-tracker

# Check Nginx
sudo systemctl status nginx

# Check PostgreSQL
sudo systemctl status postgresql

# Check logs
tail -f logs/django.log
sudo journalctl -u asset-tracker -f
```

### Access the Application

1. **Web Interface**: `https://your-domain.com`
2. **Admin Interface**: `https://your-domain.com/admin/`
3. **SSO Login**: `https://your-domain.com/accounts/sso/login/`
4. **SAML Metadata**: `https://your-domain.com/accounts/sso/saml/metadata/`

### Test SSO Authentication

1. Navigate to login page
2. Click "Login with SSO"
3. Complete authentication with your corporate credentials
4. Verify you're logged in and can access the dashboard

---

## Troubleshooting

### SSO Login Issues

**Problem**: Redirected to IdP but authentication fails

**Solutions**:
- Verify Entity ID matches exactly in both SP and IdP
- Check SAML certificate is correct
- Ensure clocks are synchronized (NTP)
- Check attribute mapping configuration
- Review logs: `tail -f logs/django.log`

**Problem**: OAuth redirect URI mismatch

**Solutions**:
- Ensure redirect URI in IdP matches exactly: `https://your-domain.com/accounts/sso/oauth/callback/`
- Check for trailing slashes
- Verify HTTPS is used

**Problem**: LDAP bind failure

**Solutions**:
- Test connection: `ldapsearch -x -H ldap://server:389 -D "bind_dn" -W`
- Verify bind DN and password
- Check firewall allows LDAP port (389 or 636)

### Application Issues

**Problem**: Service won't start

**Solutions**:
```bash
# Check service logs
sudo journalctl -u asset-tracker -n 50

# Check for Python errors
cd /home/user/asset-movement-tracking-system
source venv/bin/activate
python manage.py check

# Verify database connection
python manage.py dbshell
```

**Problem**: Static files not loading

**Solutions**:
```bash
# Collect static files
source venv/bin/activate
python manage.py collectstatic --noinput

# Check Nginx configuration
sudo nginx -t

# Verify file permissions
ls -la staticfiles/
```

### Performance Issues

**Problem**: Slow response times

**Solutions**:
- Increase Gunicorn workers: Edit `/etc/systemd/system/asset-tracker.service`
- Enable database connection pooling
- Consider Redis caching
- Check server resources: `htop`

---

## Next Steps

1. **Configure SSO**: Complete SSO configuration with your Identity Provider
2. **Import Users**: Migrate or import existing users
3. **Customize**: Adjust settings, branding, and workflows
4. **Train Users**: Provide training on the system
5. **Monitor**: Set up monitoring and alerting
6. **Backup**: Verify backup procedures are working

---

## Additional Resources

- **SSO Integration Guide**: See `SSO_INTEGRATION.md` for detailed SSO configuration
- **Deployment Guide**: See `DEPLOYMENT.md` for advanced deployment options
- **README**: See `README.md` for feature overview and usage

---

## Support

For issues or questions:

1. Check logs: `logs/django.log`
2. Review documentation in this repository
3. Contact your IT administrator
4. For SSO issues, contact your Identity Provider administrator

---

## Security Checklist

Before going to production:

- [ ] HTTPS enabled with valid certificate
- [ ] `DEBUG=False` in .env
- [ ] Strong `SECRET_KEY` set
- [ ] Database password is secure
- [ ] Firewall configured
- [ ] Regular backups enabled
- [ ] SSO properly configured and tested
- [ ] User access controls reviewed
- [ ] Logs monitoring set up
- [ ] Security updates scheduled

---

**Installation Complete!** 🎉

Your Asset Management Tracking System is now installed and ready for use with SSO integration.

Access your application at: `https://your-domain.com`
