# Django Asset Management System - Deployment Guide

## Cross-Platform Deployment Instructions

### Development Setup (Any Platform)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd company_asset_management
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Linux/macOS
   source venv/bin/activate
   
   # Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   - Copy `.env.example` to `.env` (if provided)
   - Or create `.env` with development settings:
   ```
   DEBUG=True
   SECRET_KEY=your-development-secret-key
   ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
   TIME_ZONE=Asia/Hong_Kong
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Production Deployment (Linux - Dell OptiPlex)

#### 1. System Prerequisites
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx

# CentOS/RHEL
sudo yum install python3 python3-pip postgresql postgresql-server nginx
```

#### 2. Database Setup (PostgreSQL)
```bash
sudo -u postgres createuser --interactive
sudo -u postgres createdb asset_tracker
```

#### 3. Environment Configuration
Create production `.env` file:
```
DEBUG=False
SECRET_KEY=your-production-secret-key-here
ALLOWED_HOSTS=your-domain.com,your-server-ip

# Database
DB_NAME=asset_tracker
DB_USER=your_db_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_app_password
```

#### 4. Application Setup
```bash
# Clone and setup
git clone <repository-url>
cd company_asset_management
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database migration
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
```

#### 5. Web Server Configuration (Nginx + Gunicorn)
Install Gunicorn:
```bash
pip install gunicorn
```

Create systemd service file `/etc/systemd/system/asset-tracker.service`:
```ini
[Unit]
Description=Django Asset Tracker
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
RuntimeDirectory=asset-tracker
WorkingDirectory=/path/to/company_asset_management
ExecStart=/path/to/company_asset_management/venv/bin/gunicorn --workers 3 --bind unix:/run/asset-tracker/asset-tracker.sock asset_tracker.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Configure Nginx `/etc/nginx/sites-available/asset-tracker`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/company_asset_management;
    }
    
    location /media/ {
        root /path/to/company_asset_management;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/asset-tracker/asset-tracker.sock;
    }
}
```

Enable and start services:
```bash
sudo systemctl enable asset-tracker
sudo systemctl start asset-tracker
sudo ln -s /etc/nginx/sites-available/asset-tracker /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

### Security Considerations

1. **Firewall Configuration**
   ```bash
   sudo ufw allow 'Nginx Full'
   sudo ufw allow ssh
   sudo ufw enable
   ```

2. **SSL Certificate (Recommended)**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

3. **Regular Updates**
   - Keep the OS updated
   - Update Python dependencies regularly
   - Monitor logs for security issues

### Troubleshooting

#### Common Issues:
1. **Permission errors**: Ensure www-data has proper permissions
2. **Database connection**: Check PostgreSQL service and credentials
3. **Static files**: Run `collectstatic` and check Nginx configuration
4. **Logs location**: Check `/var/log/nginx/` and systemd logs

#### Dell OptiPlex Specific:
- The application has been tested to work well on Dell OptiPlex hardware
- Ensure adequate disk space for database growth
- Monitor system resources during peak usage

### Performance Optimization
- Consider Redis for caching in high-traffic environments
- Implement database connection pooling
- Use CDN for static files in production
- Enable Nginx compression for better performance

### Backup Strategy
1. **Database backups**:
   ```bash
   pg_dump asset_tracker > backup_$(date +%Y%m%d).sql
   ```

2. **Media files**: Regular rsync or similar backup solution

3. **Application code**: Maintain in version control (Git)