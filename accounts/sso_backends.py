"""
SSO Authentication Backends for Asset Management System
Supports SAML 2.0, OAuth/OIDC, and LDAP authentication
"""

import logging
from datetime import datetime
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

User = get_user_model()
logger = logging.getLogger(__name__)


class SSOBackend(ModelBackend):
    """
    Base SSO Authentication Backend
    Handles common SSO user creation and update logic
    """

    def create_or_update_sso_user(self, sso_id, email, provider, attributes=None):
        """
        Create or update user from SSO authentication

        Args:
            sso_id: Unique identifier from SSO provider
            email: User's email address
            provider: SSO provider name (SAML, OAuth, LDAP)
            attributes: Dictionary of user attributes from SSO provider

        Returns:
            User object
        """
        if attributes is None:
            attributes = {}

        # Try to find existing user by SSO ID
        try:
            user = User.objects.get(sso_id=sso_id)
            logger.info(f"Found existing SSO user: {user.username}")
        except User.DoesNotExist:
            # Try to find by email
            try:
                user = User.objects.get(email=email)
                logger.info(f"Linking existing user to SSO: {user.username}")
            except User.DoesNotExist:
                # Create new user
                username = email.split('@')[0]
                # Ensure unique username
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=attributes.get('first_name', ''),
                    last_name=attributes.get('last_name', ''),
                )
                logger.info(f"Created new SSO user: {username}")

        # Update SSO fields
        user.sso_user = True
        user.sso_provider = provider
        user.sso_id = sso_id
        user.last_sso_login = timezone.now()

        # Update user attributes if provided
        if getattr(settings, 'SSO_UPDATE_USER_DATA', True):
            if 'first_name' in attributes:
                user.first_name = attributes['first_name']
            if 'last_name' in attributes:
                user.last_name = attributes['last_name']
            if 'department' in attributes:
                user.department = attributes['department']
            if 'employee_id' in attributes:
                user.employee_id = attributes['employee_id']
            if 'phone' in attributes:
                user.phone = attributes['phone']

        # Assign role based on groups if configured
        if getattr(settings, 'SSO_ROLE_MAPPING_ENABLED', False):
            groups = attributes.get('groups', [])
            user.role = self.map_role_from_groups(groups)

        user.save()
        return user

    def map_role_from_groups(self, groups):
        """
        Map SSO groups to application roles

        Args:
            groups: List of group names from SSO provider

        Returns:
            Role string (admin, location_manager, personnel)
        """
        admin_groups = getattr(settings, 'SSO_ADMIN_GROUPS', '').split(',')
        manager_groups = getattr(settings, 'SSO_MANAGER_GROUPS', '').split(',')

        # Check for admin role
        if any(group.strip() in groups for group in admin_groups if group.strip()):
            return 'admin'

        # Check for manager role
        if any(group.strip() in groups for group in manager_groups if group.strip()):
            return 'location_manager'

        # Default to personnel
        return getattr(settings, 'SSO_DEFAULT_ROLE', 'personnel')


class SAMLBackend(SSOBackend):
    """
    SAML 2.0 Authentication Backend
    """

    def authenticate(self, request, saml_data=None):
        """
        Authenticate user via SAML

        Args:
            request: Django request object
            saml_data: Dictionary containing SAML assertion data

        Returns:
            User object or None
        """
        if not saml_data:
            return None

        try:
            # Extract user information from SAML attributes
            attributes = saml_data.get('attributes', {})

            # Get email and unique identifier
            email_attr = getattr(settings, 'SAML_ATTRIBUTE_MAPPING_EMAIL', 'email')
            username_attr = getattr(settings, 'SAML_ATTRIBUTE_MAPPING_USERNAME', 'username')

            email = attributes.get(email_attr, [None])[0]
            sso_id = attributes.get(username_attr, [email])[0]

            if not email or not sso_id:
                logger.error("Missing required SAML attributes: email or username")
                return None

            # Extract additional attributes
            first_name_attr = getattr(settings, 'SAML_ATTRIBUTE_MAPPING_FIRST_NAME', 'firstName')
            last_name_attr = getattr(settings, 'SAML_ATTRIBUTE_MAPPING_LAST_NAME', 'lastName')

            user_attributes = {
                'first_name': attributes.get(first_name_attr, [''])[0],
                'last_name': attributes.get(last_name_attr, [''])[0],
                'groups': attributes.get('groups', []),
            }

            # Create or update user
            user = self.create_or_update_sso_user(sso_id, email, 'SAML', user_attributes)

            logger.info(f"SAML authentication successful for user: {user.username}")
            return user

        except Exception as e:
            logger.error(f"SAML authentication failed: {str(e)}")
            return None


class OAuthBackend(SSOBackend):
    """
    OAuth 2.0 / OpenID Connect Authentication Backend
    """

    def authenticate(self, request, oauth_data=None):
        """
        Authenticate user via OAuth/OIDC

        Args:
            request: Django request object
            oauth_data: Dictionary containing OAuth user data

        Returns:
            User object or None
        """
        if not oauth_data:
            return None

        try:
            # Extract user information from OAuth response
            email = oauth_data.get('email')
            sso_id = oauth_data.get('sub') or oauth_data.get('id') or email

            if not email or not sso_id:
                logger.error("Missing required OAuth attributes: email or id")
                return None

            # Extract additional attributes
            user_attributes = {
                'first_name': oauth_data.get('given_name', oauth_data.get('first_name', '')),
                'last_name': oauth_data.get('family_name', oauth_data.get('last_name', '')),
                'groups': oauth_data.get('groups', []),
            }

            # Create or update user
            user = self.create_or_update_sso_user(sso_id, email, 'OAuth', user_attributes)

            logger.info(f"OAuth authentication successful for user: {user.username}")
            return user

        except Exception as e:
            logger.error(f"OAuth authentication failed: {str(e)}")
            return None


class LDAPMixin:
    """
    LDAP Authentication helper methods
    """

    def get_ldap_user_attributes(self, ldap_user):
        """
        Extract user attributes from LDAP

        Args:
            ldap_user: LDAP user object

        Returns:
            Dictionary of user attributes
        """
        try:
            email_attr = getattr(settings, 'LDAP_ATTR_EMAIL', 'mail')
            first_name_attr = getattr(settings, 'LDAP_ATTR_FIRST_NAME', 'givenName')
            last_name_attr = getattr(settings, 'LDAP_ATTR_LAST_NAME', 'sn')
            username_attr = getattr(settings, 'LDAP_ATTR_USERNAME', 'sAMAccountName')
            department_attr = getattr(settings, 'LDAP_ATTR_DEPARTMENT', 'department')
            employee_id_attr = getattr(settings, 'LDAP_ATTR_EMPLOYEE_ID', 'employeeNumber')

            return {
                'email': ldap_user.attrs.get(email_attr, [''])[0],
                'first_name': ldap_user.attrs.get(first_name_attr, [''])[0],
                'last_name': ldap_user.attrs.get(last_name_attr, [''])[0],
                'username': ldap_user.attrs.get(username_attr, [''])[0],
                'department': ldap_user.attrs.get(department_attr, [''])[0],
                'employee_id': ldap_user.attrs.get(employee_id_attr, [''])[0],
                'groups': ldap_user.attrs.get('memberOf', []),
            }
        except Exception as e:
            logger.error(f"Error extracting LDAP attributes: {str(e)}")
            return {}


# Configure django-auth-ldap backend if LDAP is enabled
try:
    from django_auth_ldap.backend import LDAPBackend as BaseLDAPBackend

    class LDAPBackend(BaseLDAPBackend, SSOBackend, LDAPMixin):
        """
        LDAP/Active Directory Authentication Backend
        Extends django-auth-ldap with SSO user tracking
        """

        def authenticate_ldap_user(self, ldap_user, password):
            """
            Override to add SSO tracking
            """
            user = super().authenticate_ldap_user(ldap_user, password)

            if user:
                # Extract attributes
                attrs = self.get_ldap_user_attributes(ldap_user)

                # Update SSO fields
                user.sso_user = True
                user.sso_provider = 'LDAP'
                user.sso_id = attrs.get('username', user.username)
                user.last_sso_login = timezone.now()

                # Update attributes if enabled
                if getattr(settings, 'SSO_UPDATE_USER_DATA', True):
                    if attrs.get('department'):
                        user.department = attrs['department']
                    if attrs.get('employee_id'):
                        user.employee_id = attrs['employee_id']

                user.save()
                logger.info(f"LDAP authentication successful for user: {user.username}")

            return user

except ImportError:
    # django-auth-ldap not installed
    logger.warning("django-auth-ldap not installed. LDAP authentication will not be available.")
    LDAPBackend = None
