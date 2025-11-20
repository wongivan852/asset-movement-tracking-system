# SSO Testing Guide - Phase 1

**Comprehensive testing checklist for SSO integration**

---

## Test Environment Setup

### Prerequisites Checklist

- [ ] Development server running (`python manage.py runserver`)
- [ ] .env file configured with SSO credentials
- [ ] Database migrations applied (`python manage.py migrate`)
- [ ] Django Sites configured (SITE_ID=1)
- [ ] SSO provider configured with correct callback URLs
- [ ] Test SSO accounts available

---

## Test Suite

### 1. Authentication Tests

#### 1.1 Local Django Authentication
- [ ] Can access Django admin at `/admin/`
- [ ] Can login with superuser credentials
- [ ] Can logout successfully
- [ ] Password change works
- [ ] Password reset works (if email configured)

#### 1.2 SSO Authentication
- [ ] SSO login button appears on `/accounts/login/`
- [ ] Clicking SSO button redirects to SSO provider
- [ ] Can login with SSO credentials
- [ ] Redirected back to application after SSO login
- [ ] Redirected to dashboard after successful login
- [ ] Can logout from SSO session

#### 1.3 SSO Callback
- [ ] Callback URL accessible: `/accounts/openid_connect/integrated_platform/login/callback/`
- [ ] No errors in logs during callback
- [ ] User session created after callback
- [ ] CSRF token handling works correctly

---

### 2. User Auto-Provisioning Tests

#### 2.1 New User Creation
- [ ] New SSO user creates Django user automatically
- [ ] Username set correctly (from `sub` or `user_id` claim)
- [ ] Email set correctly
- [ ] First name populated (if available)
- [ ] Last name populated (if available)
- [ ] Employee ID set (if available)
- [ ] Department set (if available)
- [ ] Phone set (if available)
- [ ] User marked as active (`is_active=True`)

#### 2.2 Existing User Linking
- [ ] Existing user with matching email gets linked to SSO account
- [ ] No duplicate users created
- [ ] Existing user data not overwritten
- [ ] Social account record created

#### 2.3 User Data Sync
- [ ] User data updates on subsequent logins (if sync enabled)
- [ ] Role updates when SSO role changes
- [ ] Profile updates when SSO data changes

---

### 3. Role Mapping Tests

#### 3.1 Admin Role
**SSO Claim:** `role: "admin"` or `roles: ["admin"]`
- [ ] User assigned `admin` role
- [ ] User has `is_admin` property = True
- [ ] User can access admin functions
- [ ] User can manage other users
- [ ] User can access all locations

**Test with these SSO role values:**
- [ ] `admin`
- [ ] `administrator`
- [ ] `system_admin`
- [ ] `super_admin`

#### 3.2 Location Manager Role
**SSO Claim:** `role: "manager"` or `roles: ["manager"]`
- [ ] User assigned `location_manager` role
- [ ] User has `is_location_manager` property = True
- [ ] User can manage locations
- [ ] User can manage staff
- [ ] User can create stock takes

**Test with these SSO role values:**
- [ ] `manager`
- [ ] `location_manager`
- [ ] `site_manager`
- [ ] `facility_manager`

#### 3.3 Personnel Role (Default)
**SSO Claim:** `role: "user"` or `roles: ["user"]`
- [ ] User assigned `personnel` role
- [ ] User has `is_personnel` property = True
- [ ] User can view assets
- [ ] User can create movements
- [ ] User cannot manage users

**Test with these SSO role values:**
- [ ] `user`
- [ ] `employee`
- [ ] `staff`
- [ ] `personnel`
- [ ] No role claim (should default to personnel)
- [ ] Unknown role value (should default to personnel)

#### 3.4 Multiple Roles
**SSO Claim:** `roles: ["user", "admin"]`
- [ ] Highest priority role assigned (admin)
- [ ] User has appropriate permissions

---

### 4. Security Tests

#### 4.1 HTTPS Redirect (Production Only)
- [ ] HTTP requests redirect to HTTPS (when `SECURE_SSL_REDIRECT=True`)
- [ ] HSTS headers present
- [ ] Secure cookies enabled

#### 4.2 CSRF Protection
- [ ] CSRF token present in forms
- [ ] POST requests without CSRF token rejected
- [ ] CSRF token validated correctly

#### 4.3 Session Security
- [ ] Session cookies marked as httponly
- [ ] Session cookies marked as secure (HTTPS only)
- [ ] Session expires after timeout
- [ ] Logout clears session completely

#### 4.4 OAuth Security
- [ ] PKCE enabled for OAuth
- [ ] State parameter validated
- [ ] Redirect URI validated
- [ ] Token exchange over HTTPS only

---

### 5. CORS Tests

#### 5.1 Allowed Origins
**From platform domain:**
- [ ] GET requests accepted
- [ ] POST requests accepted
- [ ] Credentials (cookies) sent
- [ ] Authorization headers sent

**From other domains:**
- [ ] Requests blocked by CORS
- [ ] Error message clear

#### 5.2 Preflight Requests
- [ ] OPTIONS requests handled correctly
- [ ] Correct CORS headers returned
- [ ] Preflight cached for 1 hour

---

### 6. Iframe Embedding Tests

#### 6.1 Same-Origin Embedding
- [ ] Application loads in iframe from same origin
- [ ] No "Refused to display" errors
- [ ] Cookies work in iframe
- [ ] Session maintained in iframe

#### 6.2 Cross-Origin Embedding
- [ ] Application loads in iframe from platform domain
- [ ] CSP frame-ancestors allows platform
- [ ] Authentication works in iframe
- [ ] API calls work from iframe

#### 6.3 X-Frame-Options
- [ ] `X-Frame-Options: SAMEORIGIN` header present
- [ ] Embedding from other origins blocked
- [ ] CSP frame-ancestors properly configured

---

### 7. API & JWT Tests

#### 7.1 Token Obtain
**Request:**
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
```

- [ ] Returns access and refresh tokens
- [ ] Access token contains user_id claim
- [ ] Token format is valid JWT
- [ ] Token expires in 1 hour

#### 7.2 Token Refresh
**Request:**
```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "refresh-token-here"}'
```

- [ ] Returns new access token
- [ ] Old refresh token rotated (if enabled)
- [ ] Blacklisted tokens rejected

#### 7.3 Token Verify
**Request:**
```bash
curl -X POST http://localhost:8000/api/token/verify/ \
  -H "Content-Type: application/json" \
  -d '{"token": "access-token-here"}'
```

- [ ] Valid token returns 200
- [ ] Invalid token returns 401
- [ ] Expired token returns 401

#### 7.4 API Authentication
**Request:**
```bash
curl http://localhost:8000/dashboard/api/stats/ \
  -H "Authorization: Bearer access-token-here"
```

- [ ] With valid token: Returns data
- [ ] Without token: Returns 401
- [ ] With invalid token: Returns 401
- [ ] With expired token: Returns 401

#### 7.5 Movement Tracking API
**Request:**
```bash
curl http://localhost:8000/movements/api/track/MV2025-ABC123/ \
  -H "Authorization: Bearer access-token-here"
```

- [ ] Returns movement data
- [ ] JSON format correct
- [ ] Authentication required

---

### 8. Integration Tests

#### 8.1 Full User Journey
1. [ ] User clicks SSO login button
2. [ ] User redirected to SSO provider
3. [ ] User enters SSO credentials
4. [ ] User redirected back to app
5. [ ] User auto-provisioned
6. [ ] User redirected to dashboard
7. [ ] User sees correct role-based UI
8. [ ] User can access appropriate features
9. [ ] User can logout
10. [ ] Session terminated

#### 8.2 Embedded Application Flow
1. [ ] Platform loads app in iframe
2. [ ] User sees login page
3. [ ] User clicks SSO login
4. [ ] SSO happens in parent window or popup
5. [ ] User authenticated in iframe
6. [ ] User can interact with app
7. [ ] Navigation works
8. [ ] API calls work

---

### 9. Error Handling Tests

#### 9.1 SSO Provider Errors
- [ ] Provider unavailable: User sees error message
- [ ] Invalid client_id: User sees error message
- [ ] Invalid client_secret: User sees error message
- [ ] Network timeout: User sees error message

#### 9.2 Callback Errors
- [ ] Invalid state parameter: Rejected
- [ ] Invalid code: Error shown
- [ ] Missing required claims: User sees error
- [ ] Expired authorization code: Error shown

#### 9.3 User Errors
- [ ] Duplicate email: Handled correctly (link to existing user)
- [ ] Missing email claim: Error shown
- [ ] Invalid username characters: Handled gracefully

---

### 10. Performance Tests

#### 10.1 Load Time
- [ ] SSO redirect < 1 second
- [ ] Callback processing < 2 seconds
- [ ] User creation < 1 second
- [ ] Total SSO flow < 5 seconds

#### 10.2 Concurrent Users
- [ ] 10 simultaneous SSO logins work
- [ ] 50 simultaneous SSO logins work
- [ ] No race conditions in user creation
- [ ] Sessions don't interfere

---

### 11. Logging Tests

#### 11.1 Log Output
Check `logs/django.log` for:
- [ ] SSO login attempts logged
- [ ] User auto-provisioning logged
- [ ] Role assignment logged
- [ ] Social account linking logged
- [ ] Errors logged with details

#### 11.2 Log Format
- [ ] Timestamp present
- [ ] Log level present
- [ ] Module name present
- [ ] Message clear and informative

---

## Test Data

### Test SSO Users

Create these test users in your SSO provider:

#### 1. Admin User
```json
{
  "sub": "admin001",
  "email": "admin@company.com",
  "given_name": "Admin",
  "family_name": "User",
  "role": "admin",
  "employee_id": "EMP001",
  "department": "IT"
}
```

#### 2. Manager User
```json
{
  "sub": "manager001",
  "email": "manager@company.com",
  "given_name": "Manager",
  "family_name": "User",
  "role": "manager",
  "employee_id": "EMP002",
  "department": "Operations"
}
```

#### 3. Personnel User
```json
{
  "sub": "user001",
  "email": "user@company.com",
  "given_name": "Regular",
  "family_name": "User",
  "role": "user",
  "employee_id": "EMP003",
  "department": "Warehouse"
}
```

#### 4. No Role User (Test Default)
```json
{
  "sub": "user002",
  "email": "norole@company.com",
  "given_name": "No",
  "family_name": "Role"
}
```

---

## Automated Testing

### Run Unit Tests

```bash
python manage.py test accounts.tests.test_sso
```

Expected output:
```
Ran 3 tests in 0.XXXs
OK
```

### Run Integration Tests (Future)

```bash
# Coming in Phase 2
python manage.py test --pattern="test_sso_integration.py"
```

---

## Browser Compatibility Testing

Test in these browsers:

- [ ] Chrome/Chromium (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Mobile Chrome (Android)

---

## Regression Testing

After any changes to SSO code, verify:

- [ ] All authentication methods still work
- [ ] Existing users can still login
- [ ] No duplicate users created
- [ ] Roles still map correctly
- [ ] API authentication still works
- [ ] Embedding still works

---

## Production Pre-Launch Checklist

Before deploying to production:

- [ ] All tests passing
- [ ] SSO provider production endpoints configured
- [ ] HTTPS enabled
- [ ] Secure cookies enabled
- [ ] HSTS enabled
- [ ] Production callback URLs registered
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Backup/restore tested
- [ ] Rollback plan ready

---

## Troubleshooting Commands

```bash
# Check logs in real-time
tail -f logs/django.log

# Filter for SSO-related logs
grep "SSO\|allauth\|social" logs/django.log

# Check database users
python manage.py shell
from accounts.models import User
User.objects.all().values('username', 'email', 'role')

# Check social accounts
from allauth.socialaccount.models import SocialAccount
SocialAccount.objects.all()

# Clear sessions (logout all users)
python manage.py clearsessions

# Create test superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Check settings
python manage.py diffsettings | grep -i "auth\|cors\|csp"
```

---

## Test Results Template

```markdown
## Test Execution: [Date]

**Tester:** [Name]
**Environment:** [Development/Staging/Production]
**SSO Provider:** [Provider Name]

### Results Summary

- Total Tests: X
- Passed: X
- Failed: X
- Skipped: X

### Failed Tests

1. Test Name: [Name]
   - Expected: [What should happen]
   - Actual: [What happened]
   - Error: [Error message]
   - Screenshot: [Link if available]

### Notes

[Any additional observations]

### Sign-off

- [ ] All critical tests passed
- [ ] Documentation updated
- [ ] Ready for next phase
```

---

**Document Version:** 1.0
**Last Updated:** November 20, 2025
