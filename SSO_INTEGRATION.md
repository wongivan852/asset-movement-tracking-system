# SSO Integration Guide
## Asset Management Tracking System - Business Platform Integration

This guide provides detailed instructions for integrating the Asset Management Tracking System with your Business Platform using Single Sign-On (SSO).

## Table of Contents
1. [Supported SSO Protocols](#supported-sso-protocols)
2. [SAML 2.0 Configuration](#saml-20-configuration)
3. [OAuth 2.0 / OIDC Configuration](#oauth-20--oidc-configuration)
4. [LDAP/Active Directory Configuration](#ldapactive-directory-configuration)
5. [Testing SSO Integration](#testing-sso-integration)
6. [Troubleshooting](#troubleshooting)

---

## Supported SSO Protocols

The system supports the following SSO authentication methods:

- **SAML 2.0** - Industry standard for enterprise SSO (recommended)
- **OAuth 2.0 / OpenID Connect (OIDC)** - Modern web authentication
- **LDAP / Active Directory** - Corporate directory integration

---

## SAML 2.0 Configuration

### Prerequisites
- SAML Identity Provider (IdP) metadata or configuration
- X.509 certificate from your IdP
- Ability to configure Service Provider (SP) in your IdP

### Step 1: Gather IdP Information

You'll need the following from your Identity Provider:

```
1. Entity ID (IdP Identifier)
2. SSO URL (Single Sign-On Service URL)
3. SLO URL (Single Logout Service URL) - Optional
4. X.509 Certificate
```

### Step 2: Configure Service Provider (This Application)

Edit your `.env` file:

```bash
# Enable SSO
SSO_ENABLED=True
SSO_TYPE=SAML

# SAML Configuration
SAML_ENTITY_ID=https://your-domain.com/saml/metadata/
SAML_SSO_URL=https://idp.yourcompany.com/sso
SAML_SLO_URL=https://idp.yourcompany.com/slo
SAML_X509_CERT=MIIDXTCCAkWgAwIBAgIJALmVVuDWu4NYMA0GCSqGSIb3DQEBCwUA...

# Attribute Mapping (adjust based on your IdP)
SAML_ATTRIBUTE_MAPPING_EMAIL=http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress
SAML_ATTRIBUTE_MAPPING_USERNAME=http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name
SAML_ATTRIBUTE_MAPPING_FIRST_NAME=http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname
SAML_ATTRIBUTE_MAPPING_LAST_NAME=http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname
```

### Step 3: Configure Your IdP

Add this application as a Service Provider in your Identity Provider with:

```
Service Provider Information:
- Entity ID: https://your-domain.com/saml/metadata/
- ACS URL: https://your-domain.com/saml/acs/
- SLS URL: https://your-domain.com/saml/sls/
```

### Step 4: Configure Attribute Mapping

Ensure your IdP sends these attributes:

| Attribute | Description | Required |
|-----------|-------------|----------|
| email | User's email address | Yes |
| username | Unique username | Yes |
| firstName | First name | No |
| lastName | Last name | No |
| groups | User groups/roles | No |

### Common SAML Providers

#### Microsoft Azure AD / Entra ID

1. In Azure Portal, go to Enterprise Applications
2. Create new application
3. Select "Non-gallery application"
4. Configure SAML:
   - Identifier (Entity ID): `https://your-domain.com/saml/metadata/`
   - Reply URL (ACS): `https://your-domain.com/saml/acs/`
5. Add user attributes claims:
   - email: user.mail
   - username: user.userprincipalname
   - firstName: user.givenname
   - lastName: user.surname

#### Okta

1. In Okta Admin Console, go to Applications
2. Create App Integration → SAML 2.0
3. Configure SAML Settings:
   - Single sign-on URL: `https://your-domain.com/saml/acs/`
   - Audience URI: `https://your-domain.com/saml/metadata/`
4. Attribute Statements:
   - email: user.email
   - username: user.login
   - firstName: user.firstName
   - lastName: user.lastName

#### Google Workspace

1. Go to Google Admin Console → Apps → Web and mobile apps
2. Add custom SAML app
3. Download IdP metadata
4. Configure ACS URL and Entity ID as above
5. Map attributes accordingly

---

## OAuth 2.0 / OIDC Configuration

### Prerequisites
- OAuth Client ID and Secret
- Authorization and Token endpoints
- UserInfo endpoint

### Configuration

Edit your `.env` file:

```bash
# Enable OAuth
OAUTH_ENABLED=True
SSO_ENABLED=True
SSO_TYPE=OAUTH

# OAuth Configuration
OAUTH_PROVIDER=azure  # azure, okta, google, auth0, custom
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_AUTHORIZATION_URL=https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize
OAUTH_TOKEN_URL=https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
OAUTH_USERINFO_URL=https://graph.microsoft.com/v1.0/me
OAUTH_SCOPE=openid profile email
OAUTH_REDIRECT_URI=https://your-domain.com/oauth/callback
```

### Provider-Specific Examples

#### Microsoft Azure AD (OAuth 2.0)

```bash
OAUTH_PROVIDER=azure
OAUTH_CLIENT_ID=your-application-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_AUTHORIZATION_URL=https://login.microsoftonline.com/common/oauth2/v2.0/authorize
OAUTH_TOKEN_URL=https://login.microsoftonline.com/common/oauth2/v2.0/token
OAUTH_USERINFO_URL=https://graph.microsoft.com/v1.0/me
OAUTH_SCOPE=openid profile email User.Read
```

#### Google Workspace

```bash
OAUTH_PROVIDER=google
OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_AUTHORIZATION_URL=https://accounts.google.com/o/oauth2/v2/auth
OAUTH_TOKEN_URL=https://oauth2.googleapis.com/token
OAUTH_USERINFO_URL=https://www.googleapis.com/oauth2/v1/userinfo
OAUTH_SCOPE=openid profile email
```

#### Okta

```bash
OAUTH_PROVIDER=okta
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_AUTHORIZATION_URL=https://your-domain.okta.com/oauth2/default/v1/authorize
OAUTH_TOKEN_URL=https://your-domain.okta.com/oauth2/default/v1/token
OAUTH_USERINFO_URL=https://your-domain.okta.com/oauth2/default/v1/userinfo
OAUTH_SCOPE=openid profile email
```

---

## LDAP/Active Directory Configuration

### Prerequisites
- LDAP server address and port
- Bind DN and password
- User search base

### Configuration

Edit your `.env` file:

```bash
# Enable LDAP
LDAP_ENABLED=True
SSO_ENABLED=True
SSO_TYPE=LDAP

# LDAP Configuration
LDAP_SERVER_URI=ldap://your-ad-server.company.com:389
LDAP_BIND_DN=CN=Service Account,OU=Service Accounts,DC=company,DC=com
LDAP_BIND_PASSWORD=your-service-account-password
LDAP_USER_SEARCH_BASE=OU=Users,DC=company,DC=com
LDAP_USER_SEARCH_FILTER=(sAMAccountName=%(user)s)
LDAP_GROUP_SEARCH_BASE=OU=Groups,DC=company,DC=com

# LDAP Attribute Mapping
LDAP_ATTR_EMAIL=mail
LDAP_ATTR_FIRST_NAME=givenName
LDAP_ATTR_LAST_NAME=sn
LDAP_ATTR_USERNAME=sAMAccountName

# SSL/TLS Settings (recommended for production)
LDAP_USE_SSL=False
LDAP_USE_TLS=True
```

### Active Directory Example

```bash
LDAP_SERVER_URI=ldap://dc01.contoso.com:389
LDAP_BIND_DN=CN=AppService,OU=Service Accounts,DC=contoso,DC=com
LDAP_BIND_PASSWORD=SecurePassword123!
LDAP_USER_SEARCH_BASE=OU=Employees,DC=contoso,DC=com
LDAP_USER_SEARCH_FILTER=(sAMAccountName=%(user)s)
LDAP_USE_TLS=True
```

---

## Role Mapping

### Automatic Role Assignment

You can automatically assign roles based on SSO groups/attributes:

```bash
# Role Mapping Configuration
SSO_ROLE_MAPPING_ENABLED=True

# Map IdP groups to application roles
SSO_ADMIN_GROUPS=Asset-Admins,IT-Admins
SSO_MANAGER_GROUPS=Asset-Managers,Location-Managers
SSO_STAFF_GROUPS=Asset-Users,All-Employees

# Default role for new SSO users
SSO_DEFAULT_ROLE=PERSONNEL
```

---

## Testing SSO Integration

### 1. Test Configuration

```bash
# Activate virtual environment
source venv/bin/activate

# Test SSO configuration
python manage.py test_sso_config
```

### 2. Test Login Flow

1. Navigate to: `https://your-domain.com/sso/login`
2. You should be redirected to your IdP
3. Login with your corporate credentials
4. You should be redirected back and logged in

### 3. Verify User Creation

```bash
# Check if SSO users are being created
python manage.py shell

>>> from accounts.models import User
>>> User.objects.filter(sso_user=True)
```

### 4. Test Logout

1. Click logout in the application
2. Verify you're also logged out of the IdP (if SLO configured)

---

## Security Considerations

### Production Checklist

- [ ] Enable HTTPS (required for production SSO)
- [ ] Set `SECURE_SSL_REDIRECT=True` in .env
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Use strong SECRET_KEY
- [ ] Enable CSRF and session cookie security:
  ```bash
  SESSION_COOKIE_SECURE=True
  CSRF_COOKIE_SECURE=True
  ```
- [ ] Configure firewall to restrict database access
- [ ] Enable audit logging
- [ ] Regularly rotate certificates and secrets
- [ ] Implement rate limiting on SSO endpoints

### Certificate Management

For SAML, store certificates securely:

```bash
# Create certificates directory
mkdir -p /etc/asset-tracker/certs
chmod 700 /etc/asset-tracker/certs

# Store IdP certificate
echo "$SAML_X509_CERT" > /etc/asset-tracker/certs/idp_cert.pem
chmod 600 /etc/asset-tracker/certs/idp_cert.pem

# Update .env to use file path
SAML_X509_CERT_FILE=/etc/asset-tracker/certs/idp_cert.pem
```

---

## Troubleshooting

### Common Issues

#### 1. SAML Response Invalid

**Symptoms:** Error message "SAML response validation failed"

**Solutions:**
- Verify Entity ID matches exactly
- Check clock sync between SP and IdP (NTP)
- Validate X.509 certificate is correct
- Check SAML attribute names match configuration

#### 2. OAuth Redirect URI Mismatch

**Symptoms:** "redirect_uri_mismatch" error

**Solutions:**
- Ensure redirect URI in IdP matches exactly
- Check for trailing slashes
- Verify HTTPS vs HTTP

#### 3. LDAP Bind Failure

**Symptoms:** Cannot connect to LDAP server

**Solutions:**
- Verify LDAP server URI and port
- Check bind DN and password
- Test network connectivity: `ldapsearch -x -H ldap://server:389`
- Check firewall rules

#### 4. User Not Created Automatically

**Symptoms:** Users can authenticate but not access system

**Solutions:**
- Check attribute mapping configuration
- Verify email attribute is being sent
- Enable debug logging: `DEBUG=True`
- Check Django logs: `tail -f logs/django.log`

### Debug Mode

Enable SSO debugging:

```bash
# In .env
DEBUG=True
SSO_DEBUG=True
```

Check logs:

```bash
# Application logs
tail -f logs/django.log

# System logs
sudo journalctl -u asset-tracker -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Contact Support

If issues persist:

1. Collect logs from `logs/django.log`
2. Note exact error messages
3. Provide SSO configuration (without secrets)
4. Contact your IT department or SSO administrator

---

## Migration from Local Auth to SSO

### Gradual Migration

You can run both authentication methods simultaneously:

```bash
# Allow both local and SSO authentication
SSO_ENABLED=True
ALLOW_LOCAL_AUTH=True
```

### Force SSO Only

To disable local authentication:

```bash
SSO_ENABLED=True
ALLOW_LOCAL_AUTH=False
```

### Linking Existing Users

Link existing local users with SSO:

```bash
python manage.py shell

>>> from accounts.models import User
>>> user = User.objects.get(username='existing_user')
>>> user.sso_user = True
>>> user.sso_id = 'user@company.com'
>>> user.save()
```

---

## Advanced Configuration

### Custom Attribute Mapping

For complex IdP attribute structures:

```python
# In accounts/sso_backends.py
SAML_ATTRIBUTE_MAPPING = {
    'email': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',
    'username': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name',
    'first_name': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname',
    'last_name': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname',
    'department': 'http://schemas.company.com/identity/claims/department',
    'employee_id': 'http://schemas.company.com/identity/claims/employeeid',
}
```

### Just-In-Time (JIT) Provisioning

Users are automatically created on first SSO login:

```bash
SSO_JIT_PROVISIONING=True
SSO_CREATE_UNKNOWN_USER=True
SSO_UPDATE_USER_DATA=True  # Update user data on each login
```

### Multi-Factor Authentication (MFA)

MFA should be configured in your IdP. The application will honor IdP authentication decisions.

---

## API Authentication with SSO

For API access with SSO:

```bash
# Enable API token authentication for SSO users
API_AUTH_ENABLED=True
API_TOKEN_EXPIRY=3600  # 1 hour
```

Users can generate API tokens after SSO login.

---

## Compliance and Auditing

### Audit Logging

All SSO events are logged:
- Login attempts
- Successful authentications
- Failed authentications
- Logout events
- User provisioning

View audit logs:

```bash
# Filter SSO events
python manage.py sso_audit_report --days 30
```

### GDPR Compliance

For user data management:
- SSO user data is synchronized from IdP
- Local profile changes may be overwritten on next login
- User deletion requests should be handled at IdP level

---

## Support Matrix

| SSO Provider | SAML 2.0 | OAuth/OIDC | LDAP | Status |
|--------------|----------|------------|------|--------|
| Microsoft Azure AD | ✓ | ✓ | ✓ | Fully Supported |
| Okta | ✓ | ✓ | - | Fully Supported |
| Google Workspace | ✓ | ✓ | - | Fully Supported |
| Auth0 | ✓ | ✓ | - | Fully Supported |
| Active Directory | - | - | ✓ | Fully Supported |
| OneLogin | ✓ | ✓ | - | Tested |
| Ping Identity | ✓ | ✓ | - | Tested |
| Custom SAML | ✓ | - | - | Supported |

---

## References

- [SAML 2.0 Specification](https://docs.oasis-open.org/security/saml/v2.0/)
- [OAuth 2.0 RFC](https://tools.ietf.org/html/rfc6749)
- [OpenID Connect](https://openid.net/connect/)
- [Django Authentication Backends](https://docs.djangoproject.com/en/stable/topics/auth/)
