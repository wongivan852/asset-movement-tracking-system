# Asset Management System Deployment Guide
## Remote API Mode with Business Platform Integration

Complete step-by-step deployment instructions for integrating Asset Management System with your Business Platform at `http://192.168.0.104:8000`.

---

## 📋 Overview

This deployment uses **Remote API Mode**, which:
- ✅ Has minimal impact on Business Platform (just 2 API endpoints)
- ✅ Keeps databases separate and independent
- ✅ Maintains security isolation
- ✅ Allows independent scaling and deployment

---

## 🔑 Generated Credentials

**API Key (use in both systems):**
```
qLzxsUsGic0ANefhzeXilZj9pPxyygJsr48V8SGBhiU
```

**⚠️ IMPORTANT:** Keep this secure! Don't commit to Git!

---

## Part 1: Business Platform Setup

### Step 1: Add API Code

See **`BUSINESS_PLATFORM_API_SETUP.md`** for complete code.

Quick summary:
1. Add `api_views.py` with 3 endpoints
2. Add URL patterns to `urls.py`
3. Add API key to `settings.py`
4. Test endpoints

**Time required:** 10-15 minutes

### Step 2: Deploy Business Platform Changes

```bash
# In Business Platform directory
cd /path/to/business-platform

# Add API views file
# (copy code from BUSINESS_PLATFORM_API_SETUP.md)

# Update urls.py
# (add API URL patterns)

# Update settings.py
# Add: ASSET_MANAGEMENT_API_KEY = 'qLzxsUsGic0ANefhzeXilZj9pPxyygJsr48V8SGBhiU'

# Restart Business Platform
sudo systemctl restart business-platform  # or your service name
# OR
sudo supervisorctl restart business-platform
# OR
pkill -f "python.*manage.py runserver" && python manage.py runserver
```

### Step 3: Test Business Platform API

```bash
# Test health check
curl http://192.168.0.104:8000/api/auth/health/

# Should return:
# {"status":"ok","service":"Business Platform Auth API","version":"1.0.0"}
```

---

## Part 2: Asset Management System Setup

### Step 1: Configure Environment

```bash
cd /home/user/asset-movement-tracking-system

# Copy production config
cp .env.production .env

# Generate SECRET_KEY
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Edit .env file
nano .env
```

**Update these values in `.env`:**

```bash
# Replace with generated SECRET_KEY
SECRET_KEY=your-generated-secret-key-here

# Update allowed hosts with your server IP/domain
ALLOWED_HOSTS=localhost,127.0.0.1,YOUR_SERVER_IP

# Set secure database password
DB_PASSWORD=your-secure-database-password

# Keep API key as-is
BUSINESS_PLATFORM_API_KEY=qLzxsUsGic0ANefhzeXilZj9pPxyygJsr48V8SGBhiU
```

### Step 2: Install Dependencies

```bash
# Create virtual environment if not exists
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Set Up Database

```bash
# Create PostgreSQL database
sudo -u postgres psql <<EOF
CREATE DATABASE asset_tracker;
CREATE USER asset_tracker_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE asset_tracker TO asset_tracker_user;
ALTER ROLE asset_tracker_user SET client_encoding TO 'utf8';
ALTER ROLE asset_tracker_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE asset_tracker_user SET timezone TO 'Asia/Hong_Kong';
EOF

# Run migrations
python manage.py migrate

# Create superuser (for local admin access)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Step 4: Create System Service

```bash
# Create systemd service
sudo nano /etc/systemd/system/asset-tracker.service
```

Add this content:

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
    --timeout 120 \
    asset_tracker.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Replace `YOUR_USERNAME` with your actual username:

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable asset-tracker
sudo systemctl start asset-tracker
sudo systemctl status asset-tracker
```

### Step 5: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/asset-tracker
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

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
        proxy_connect_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/asset-tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Part 3: Testing the Integration

### Test 1: Check Services

```bash
# Check Asset Management service
sudo systemctl status asset-tracker

# Check Nginx
sudo systemctl status nginx

# Check logs
tail -f /home/user/asset-movement-tracking-system/logs/django.log
```

### Test 2: Test API Connection

```bash
# Test from Asset Management server
cd /home/user/asset-movement-tracking-system
source venv/bin/activate

python3 << 'EOF'
import requests

url = "http://192.168.0.104:8000/api/auth/health/"
response = requests.get(url)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
EOF
```

Should print:
```
Status: 200
Response: {'status': 'ok', 'service': 'Business Platform Auth API', 'version': '1.0.0'}
```

### Test 3: End-to-End Integration Test

**Step-by-step test:**

1. **Login to Business Platform:**
   - Open browser
   - Go to: `http://192.168.0.104:8000/auth/login/`
   - Login with your credentials
   - Verify you see the dashboard

2. **Access Asset Management (same browser):**
   - Open new tab
   - Go to: `http://YOUR_ASSET_SERVER_IP/`
   - **You should be automatically logged in!** ✅
   - No password prompt should appear
   - You should see the Asset Management dashboard

3. **Verify user synchronization:**
   - In Asset Management, click on your profile/username
   - Verify your name and details match Business Platform

### Test 4: Test Logout

1. Logout from Asset Management System
2. Try to access Asset Management again
3. You should need to login via Business Platform

---

## 🔍 Troubleshooting

### Issue: Not Automatically Logged In

**Possible causes:**

1. **API key mismatch**
   ```bash
   # Check Asset Management .env
   grep BUSINESS_PLATFORM_API_KEY /home/user/asset-movement-tracking-system/.env

   # Should match Business Platform settings.py
   ```

2. **Business Platform API not accessible**
   ```bash
   curl http://192.168.0.104:8000/api/auth/health/
   ```

3. **Cookie not sent**
   - Check browser console for errors
   - Verify `CORS_ALLOW_CREDENTIALS = True` in Business Platform
   - Check `CORS_ALLOWED_ORIGINS` includes Asset Management URL

4. **Check logs**
   ```bash
   # Asset Management logs
   tail -f /home/user/asset-movement-tracking-system/logs/django.log

   # Business Platform logs (adjust path)
   tail -f /var/log/business-platform/django.log
   ```

### Issue: 401 Unauthorized

**Fix:**
- Verify API key matches in both systems
- Check Business Platform `settings.py` has `ASSET_MANAGEMENT_API_KEY`

### Issue: CORS Error

**Fix:**
Add Asset Management URL to Business Platform's `CORS_ALLOWED_ORIGINS`:

```python
# In Business Platform settings.py
CORS_ALLOWED_ORIGINS = [
    'http://YOUR_ASSET_SERVER_IP',
]
```

### Issue: 500 Internal Server Error

**Check:**
```bash
# Asset Management logs
tail -100 logs/django.log

# System logs
sudo journalctl -u asset-tracker -n 50

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

---

## 📊 Monitoring

### Log Files to Monitor

**Asset Management:**
```bash
# Application logs
tail -f /home/user/asset-movement-tracking-system/logs/django.log

# Service logs
sudo journalctl -u asset-tracker -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

**Business Platform:**
- Monitor API endpoint usage
- Watch for failed authentication attempts
- Track API key validation failures

### Health Checks

Create a monitoring script:

```bash
#!/bin/bash
# health-check.sh

echo "Checking Business Platform API..."
curl -s http://192.168.0.104:8000/api/auth/health/ | jq

echo -e "\nChecking Asset Management..."
curl -s http://localhost/ | grep -q "Asset" && echo "✓ OK" || echo "✗ FAILED"

echo -e "\nChecking services..."
systemctl is-active asset-tracker && echo "✓ asset-tracker running" || echo "✗ asset-tracker stopped"
systemctl is-active nginx && echo "✓ nginx running" || echo "✗ nginx stopped"
```

---

## 🔒 Security Checklist

Before going to production:

- [ ] API key stored in environment variable (not hardcoded)
- [ ] `.env` file added to `.gitignore`
- [ ] Strong database password set
- [ ] Firewall configured (only necessary ports open)
- [ ] HTTPS enabled (update `.env` security settings)
- [ ] `DEBUG=False` in production
- [ ] Nginx configured correctly
- [ ] Log rotation configured
- [ ] Backup strategy in place
- [ ] Monitoring alerts configured

### Enable HTTPS (Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Update .env
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Restart service
sudo systemctl restart asset-tracker
```

---

## 🔄 Maintenance

### Update Application

```bash
cd /home/user/asset-movement-tracking-system
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart asset-tracker
```

### Backup Database

```bash
# Create backup script
cat > /usr/local/bin/backup-asset-tracker.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/asset-tracker"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
pg_dump asset_tracker > $BACKUP_DIR/db_$DATE.sql
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
EOF

chmod +x /usr/local/bin/backup-asset-tracker.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-asset-tracker.sh") | crontab -
```

---

## 📈 Performance Optimization

### For High Traffic

1. **Increase Gunicorn workers:**
   ```bash
   # Edit /etc/systemd/system/asset-tracker.service
   # Change --workers 3 to --workers 5 (or more)

   sudo systemctl daemon-reload
   sudo systemctl restart asset-tracker
   ```

2. **Enable caching:**
   ```bash
   # Install Redis
   sudo apt install redis-server

   # Add to requirements.txt:
   # django-redis==5.4.0
   ```

3. **Configure database connection pooling**

---

## ✅ Deployment Complete

After successful deployment, you should have:

✅ Business Platform with 3 API endpoints
✅ Asset Management System with API integration enabled
✅ Single sign-on working (login once, access both)
✅ Independent databases
✅ Secure API key authentication
✅ Production-ready services
✅ Nginx reverse proxy
✅ Logging and monitoring

---

## 📞 Support

If you encounter issues:

1. Check logs (application, service, nginx)
2. Verify configuration (`.env`, API key)
3. Test API connectivity
4. Review troubleshooting section above
5. Check documentation:
   - `BUSINESS_PLATFORM_API_SETUP.md`
   - `BUSINESS_PLATFORM_INTEGRATION.md`
   - `INSTALLATION_GUIDE.md`

---

## 🎯 Quick Reference

**Business Platform API Endpoints:**
- Health: `http://192.168.0.104:8000/api/auth/health/`
- Validate: `http://192.168.0.104:8000/api/auth/validate/`
- Login: `http://192.168.0.104:8000/api/auth/login/`

**Asset Management:**
- URL: `http://YOUR_SERVER_IP/`
- Admin: `http://YOUR_SERVER_IP/admin/`
- Logs: `/home/user/asset-movement-tracking-system/logs/django.log`

**API Key:**
```
qLzxsUsGic0ANefhzeXilZj9pPxyygJsr48V8SGBhiU
```

**Services:**
```bash
# Restart Asset Management
sudo systemctl restart asset-tracker

# Check status
sudo systemctl status asset-tracker

# View logs
sudo journalctl -u asset-tracker -f
```

---

**Deployment Ready!** 🚀
