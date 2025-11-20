"""
Context processors for accounts app
Makes SSO settings available in templates
"""

from django.conf import settings


def sso_settings(request):
    """
    Add SSO configuration to template context
    """
    return {
        'settings': {
            'SSO_ENABLED': getattr(settings, 'SSO_ENABLED', False),
            'SSO_TYPE': getattr(settings, 'SSO_TYPE', 'SAML'),
            'ALLOW_LOCAL_AUTH': getattr(settings, 'ALLOW_LOCAL_AUTH', True),
        }
    }
