#!/bin/bash
# Asset Management Tracking System - Installation Script with SSO Support
# This script installs and configures the system for Business Platform integration

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Asset Management Tracking System${NC}"
echo -e "${GREEN}Installation with SSO Integration${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Please do not run as root. Run as regular user with sudo privileges.${NC}"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    OS_VERSION=$VERSION_ID
else
    echo -e "${RED}Cannot detect OS. This script supports Ubuntu, Debian, CentOS, and RHEL.${NC}"
    exit 1
fi

echo -e "${GREEN}Detected OS: $OS $OS_VERSION${NC}"

# Function to install system dependencies
install_dependencies() {
    echo -e "${YELLOW}Installing system dependencies...${NC}"

    if [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv python3-dev \
            postgresql postgresql-contrib libpq-dev \
            nginx git curl build-essential libssl-dev libffi-dev \
            libxml2-dev libxslt1-dev libsasl2-dev xmlsec1
    elif [[ "$OS" == "centos" || "$OS" == "rhel" ]]; then
        sudo yum install -y python3 python3-pip python3-devel \
            postgresql postgresql-server postgresql-devel \
            nginx git curl gcc openssl-devel libffi-devel \
            libxml2-devel libxslt-devel openldap-devel xmlsec1
    else
        echo -e "${RED}Unsupported OS: $OS${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ System dependencies installed${NC}"
}

# Function to setup PostgreSQL
setup_database() {
    echo -e "${YELLOW}Setting up PostgreSQL database...${NC}"

    # Initialize PostgreSQL if needed
    if [[ "$OS" == "centos" || "$OS" == "rhel" ]]; then
        sudo postgresql-setup initdb || true
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
    fi

    # Create database and user
    DB_NAME="asset_tracker"
    DB_USER="asset_tracker_user"
    DB_PASSWORD=$(openssl rand -base64 32)

    # Check if database exists
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
        echo -e "${YELLOW}Database $DB_NAME already exists. Skipping creation.${NC}"
    else
        sudo -u postgres psql <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET timezone TO 'Asia/Hong_Kong';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF
        echo -e "${GREEN}✓ Database created${NC}"
        echo -e "${YELLOW}Database Credentials:${NC}"
        echo -e "  DB_NAME=$DB_NAME"
        echo -e "  DB_USER=$DB_USER"
        echo -e "  DB_PASSWORD=$DB_PASSWORD"
        echo ""
        echo -e "${YELLOW}IMPORTANT: Save these credentials! They will be added to .env file.${NC}"

        # Save credentials to temporary file
        cat > /tmp/db_credentials.txt <<EOF
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432
EOF
    fi
}

# Function to setup Python virtual environment
setup_python_env() {
    echo -e "${YELLOW}Setting up Python virtual environment...${NC}"

    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}✓ Virtual environment created${NC}"
    else
        echo -e "${YELLOW}Virtual environment already exists${NC}"
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Upgrade pip
    pip install --upgrade pip setuptools wheel

    # Install dependencies
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip install -r requirements.txt

    # Install additional SSO dependencies
    pip install python3-saml gunicorn whitenoise django-cors-headers django-allauth

    echo -e "${GREEN}✓ Python dependencies installed${NC}"
}

# Function to create .env file
create_env_file() {
    echo -e "${YELLOW}Creating environment configuration...${NC}"

    if [ -f ".env" ]; then
        echo -e "${YELLOW}.env file already exists. Creating backup...${NC}"
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    fi

    # Generate secret key
    SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

    # Load database credentials if available
    if [ -f "/tmp/db_credentials.txt" ]; then
        source /tmp/db_credentials.txt
    fi

    # Get server IP
    SERVER_IP=$(hostname -I | awk '{print $1}')

    cat > .env <<EOF
# Django Settings
DEBUG=False
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=localhost,127.0.0.1,$SERVER_IP,*.yourdomain.com

# Database Configuration
DB_NAME=${DB_NAME:-asset_tracker}
DB_USER=${DB_USER:-asset_tracker_user}
DB_PASSWORD=${DB_PASSWORD:-changeme}
DB_HOST=localhost
DB_PORT=5432

# Time Zone
TIME_ZONE=Asia/Hong_Kong

# Email Configuration (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# SSO Configuration - SAML 2.0
SSO_ENABLED=False
SSO_TYPE=SAML
SAML_ENTITY_ID=
SAML_SSO_URL=
SAML_SLO_URL=
SAML_X509_CERT=
SAML_ATTRIBUTE_MAPPING_EMAIL=email
SAML_ATTRIBUTE_MAPPING_USERNAME=username
SAML_ATTRIBUTE_MAPPING_FIRST_NAME=firstName
SAML_ATTRIBUTE_MAPPING_LAST_NAME=lastName

# SSO Configuration - OAuth/OIDC (Alternative)
OAUTH_ENABLED=False
OAUTH_PROVIDER=
OAUTH_CLIENT_ID=
OAUTH_CLIENT_SECRET=
OAUTH_AUTHORIZATION_URL=
OAUTH_TOKEN_URL=
OAUTH_USERINFO_URL=

# SSO Configuration - LDAP (Alternative)
LDAP_ENABLED=False
LDAP_SERVER_URI=ldap://your-ldap-server:389
LDAP_BIND_DN=
LDAP_BIND_PASSWORD=
LDAP_USER_SEARCH_BASE=ou=users,dc=example,dc=com

# Security Settings (Enable for production with HTTPS)
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
EOF

    echo -e "${GREEN}✓ Environment file created${NC}"
    echo -e "${YELLOW}Please edit .env file to add your SSO configuration${NC}"

    # Clean up temporary credentials file
    rm -f /tmp/db_credentials.txt
}

# Function to setup Django application
setup_django() {
    echo -e "${YELLOW}Setting up Django application...${NC}"

    # Activate virtual environment
    source venv/bin/activate

    # Create logs directory
    mkdir -p logs

    # Run migrations
    python manage.py migrate

    # Collect static files
    python manage.py collectstatic --noinput

    # Create superuser if not exists
    echo -e "${YELLOW}Creating superuser account...${NC}"
    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created: admin/admin')
else:
    print('Superuser already exists')
EOF

    echo -e "${GREEN}✓ Django application configured${NC}"
}

# Function to setup systemd service
setup_systemd() {
    echo -e "${YELLOW}Setting up systemd service...${NC}"

    CURRENT_DIR=$(pwd)
    CURRENT_USER=$(whoami)

    sudo tee /etc/systemd/system/asset-tracker.service > /dev/null <<EOF
[Unit]
Description=Asset Management Tracking System
After=network.target postgresql.service

[Service]
Type=notify
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/gunicorn --workers 3 --bind unix:$CURRENT_DIR/asset-tracker.sock asset_tracker.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable asset-tracker
    sudo systemctl start asset-tracker

    echo -e "${GREEN}✓ Systemd service configured and started${NC}"
}

# Function to setup Nginx
setup_nginx() {
    echo -e "${YELLOW}Setting up Nginx...${NC}"

    CURRENT_DIR=$(pwd)
    SERVER_NAME=$(hostname -f)

    sudo tee /etc/nginx/sites-available/asset-tracker > /dev/null <<EOF
server {
    listen 80;
    server_name $SERVER_NAME _;

    client_max_body_size 100M;

    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }

    location /static/ {
        alias $CURRENT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias $CURRENT_DIR/media/;
    }

    location / {
        proxy_pass http://unix:$CURRENT_DIR/asset-tracker.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 600s;
        proxy_read_timeout 600s;
    }
}
EOF

    # Enable site
    sudo ln -sf /etc/nginx/sites-available/asset-tracker /etc/nginx/sites-enabled/

    # Remove default site if exists
    sudo rm -f /etc/nginx/sites-enabled/default

    # Test and reload Nginx
    sudo nginx -t
    sudo systemctl restart nginx

    echo -e "${GREEN}✓ Nginx configured and restarted${NC}"
}

# Main installation flow
main() {
    echo ""
    echo -e "${YELLOW}This script will install the Asset Management Tracking System${NC}"
    echo -e "${YELLOW}with support for SSO integration on your Business Platform.${NC}"
    echo ""
    read -p "Do you want to continue? (y/n) " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Installation cancelled${NC}"
        exit 1
    fi

    install_dependencies
    setup_database
    setup_python_env
    create_env_file
    setup_django
    setup_systemd
    setup_nginx

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Installation Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo -e "1. Configure SSO settings in .env file"
    echo -e "2. Update ALLOWED_HOSTS in .env with your domain"
    echo -e "3. Configure your Business Platform SSO provider"
    echo -e "4. Restart the service: sudo systemctl restart asset-tracker"
    echo ""
    echo -e "${YELLOW}Access the application:${NC}"
    echo -e "  URL: http://$SERVER_IP or http://$(hostname -f)"
    echo -e "  Default admin: admin / admin"
    echo ""
    echo -e "${YELLOW}Important files:${NC}"
    echo -e "  Configuration: .env"
    echo -e "  Logs: logs/django.log"
    echo -e "  Service: sudo systemctl status asset-tracker"
    echo ""
    echo -e "${YELLOW}SSO Configuration Guide:${NC}"
    echo -e "  See: SSO_INTEGRATION.md for detailed setup instructions"
    echo ""
}

# Run main installation
main
