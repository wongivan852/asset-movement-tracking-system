"""
SSO Views for Asset Management System
Handles SAML, OAuth, and SSO login/logout flows
"""

import logging
import json
from urllib.parse import urlencode
import requests

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.urls import reverse

from .sso_backends import SAMLBackend, OAuthBackend

logger = logging.getLogger(__name__)


def sso_login(request):
    """
    SSO Login entry point
    Redirects to appropriate SSO provider based on configuration
    """
    if not getattr(settings, 'SSO_ENABLED', False):
        messages.error(request, "SSO is not enabled on this system")
        return redirect('accounts:login')

    sso_type = getattr(settings, 'SSO_TYPE', 'SAML')

    if sso_type == 'SAML':
        return saml_login(request)
    elif sso_type == 'OAUTH':
        return oauth_login(request)
    elif sso_type == 'LDAP':
        # LDAP uses standard login form
        return redirect('accounts:login')
    else:
        messages.error(request, f"Unsupported SSO type: {sso_type}")
        return redirect('accounts:login')


# ==================== SAML 2.0 Views ====================

def saml_login(request):
    """
    Initiate SAML login by redirecting to IdP
    """
    try:
        from onelogin.saml2.auth import OneLogin_Saml2_Auth
        from onelogin.saml2.utils import OneLogin_Saml2_Utils

        # Prepare SAML request
        req = prepare_saml_request(request)
        auth = OneLogin_Saml2_Auth(req, custom_base_path=get_saml_settings())

        # Redirect to IdP for authentication
        return redirect(auth.login())

    except ImportError:
        logger.error("python3-saml not installed")
        messages.error(request, "SAML authentication is not available")
        return redirect('accounts:login')
    except Exception as e:
        logger.error(f"SAML login failed: {str(e)}")
        messages.error(request, "SAML authentication failed. Please try again.")
        return redirect('accounts:login')


@csrf_exempt
@require_http_methods(["POST"])
def saml_acs(request):
    """
    SAML Assertion Consumer Service (ACS)
    Handles SAML response from IdP
    """
    try:
        from onelogin.saml2.auth import OneLogin_Saml2_Auth

        req = prepare_saml_request(request)
        auth = OneLogin_Saml2_Auth(req, custom_base_path=get_saml_settings())

        # Process SAML response
        auth.process_response()
        errors = auth.get_errors()

        if errors:
            logger.error(f"SAML errors: {', '.join(errors)}")
            messages.error(request, "SAML authentication failed. Invalid response.")
            return redirect('accounts:login')

        if not auth.is_authenticated():
            logger.warning("SAML authentication failed: user not authenticated")
            messages.error(request, "SAML authentication failed.")
            return redirect('accounts:login')

        # Get user attributes from SAML response
        saml_data = {
            'attributes': auth.get_attributes(),
            'nameid': auth.get_nameid(),
            'session_index': auth.get_session_index(),
        }

        # Authenticate user
        backend = SAMLBackend()
        user = backend.authenticate(request, saml_data=saml_data)

        if user:
            login(request, user, backend='accounts.sso_backends.SAMLBackend')
            messages.success(request, f"Welcome {user.get_full_name()}! You are now logged in via SSO.")

            # Store SAML session info for logout
            request.session['saml_session_index'] = saml_data['session_index']
            request.session['saml_nameid'] = saml_data['nameid']

            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            logger.error("Failed to create/update user from SAML data")
            messages.error(request, "Authentication failed. Please contact your administrator.")
            return redirect('accounts:login')

    except Exception as e:
        logger.error(f"SAML ACS failed: {str(e)}")
        messages.error(request, "SAML authentication failed. Please try again.")
        return redirect('accounts:login')


def saml_metadata(request):
    """
    SAML Service Provider Metadata endpoint
    """
    try:
        from onelogin.saml2.auth import OneLogin_Saml2_Auth

        req = prepare_saml_request(request)
        auth = OneLogin_Saml2_Auth(req, custom_base_path=get_saml_settings())
        settings_data = auth.get_settings()
        metadata = settings_data.get_sp_metadata()

        errors = settings_data.validate_metadata(metadata)
        if len(errors) == 0:
            return HttpResponse(content=metadata, content_type='text/xml')
        else:
            return HttpResponse(content=', '.join(errors), status=500)

    except Exception as e:
        logger.error(f"Failed to generate SAML metadata: {str(e)}")
        return HttpResponse(content=str(e), status=500)


@csrf_exempt
def saml_sls(request):
    """
    SAML Single Logout Service (SLS)
    """
    try:
        from onelogin.saml2.auth import OneLogin_Saml2_Auth

        req = prepare_saml_request(request)
        auth = OneLogin_Saml2_Auth(req, custom_base_path=get_saml_settings())

        url = auth.process_slo()
        errors = auth.get_errors()

        if len(errors) == 0:
            logout(request)
            if url is not None:
                return redirect(url)
            else:
                messages.success(request, "You have been logged out successfully.")
                return redirect('accounts:login')
        else:
            logger.error(f"SAML SLO errors: {', '.join(errors)}")
            logout(request)
            return redirect('accounts:login')

    except Exception as e:
        logger.error(f"SAML logout failed: {str(e)}")
        logout(request)
        return redirect('accounts:login')


def prepare_saml_request(request):
    """
    Prepare request data for python3-saml
    """
    return {
        'https': 'on' if request.is_secure() else 'off',
        'http_host': request.META['HTTP_HOST'],
        'script_name': request.META['PATH_INFO'],
        'server_port': request.META['SERVER_PORT'],
        'get_data': request.GET.copy(),
        'post_data': request.POST.copy(),
    }


def get_saml_settings():
    """
    Generate SAML settings from Django configuration
    """
    return {
        "strict": True,
        "debug": getattr(settings, 'DEBUG', False),
        "sp": {
            "entityId": getattr(settings, 'SAML_ENTITY_ID', ''),
            "assertionConsumerService": {
                "url": f"{getattr(settings, 'SITE_URL', '')}/sso/saml/acs/",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            "singleLogoutService": {
                "url": f"{getattr(settings, 'SITE_URL', '')}/sso/saml/sls/",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
        },
        "idp": {
            "entityId": getattr(settings, 'SAML_IDP_ENTITY_ID', ''),
            "singleSignOnService": {
                "url": getattr(settings, 'SAML_SSO_URL', ''),
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "singleLogoutService": {
                "url": getattr(settings, 'SAML_SLO_URL', ''),
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "x509cert": getattr(settings, 'SAML_X509_CERT', ''),
        }
    }


# ==================== OAuth 2.0 / OIDC Views ====================

def oauth_login(request):
    """
    Initiate OAuth/OIDC login
    """
    try:
        authorization_url = getattr(settings, 'OAUTH_AUTHORIZATION_URL', '')
        client_id = getattr(settings, 'OAUTH_CLIENT_ID', '')
        redirect_uri = request.build_absolute_uri(reverse('accounts:sso_oauth_callback'))
        scope = getattr(settings, 'OAUTH_SCOPE', 'openid profile email')
        state = request.session.get('oauth_state', 'random_state_string')

        # Save state in session for verification
        request.session['oauth_state'] = state

        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': scope,
            'state': state,
        }

        auth_url = f"{authorization_url}?{urlencode(params)}"
        return redirect(auth_url)

    except Exception as e:
        logger.error(f"OAuth login initiation failed: {str(e)}")
        messages.error(request, "OAuth authentication failed. Please try again.")
        return redirect('accounts:login')


def oauth_callback(request):
    """
    OAuth/OIDC callback handler
    Exchanges authorization code for access token and authenticates user
    """
    try:
        # Verify state
        state = request.GET.get('state')
        if state != request.session.get('oauth_state'):
            logger.error("OAuth state mismatch")
            messages.error(request, "Authentication failed: Invalid state")
            return redirect('accounts:login')

        # Get authorization code
        code = request.GET.get('code')
        if not code:
            error = request.GET.get('error', 'Unknown error')
            logger.error(f"OAuth authorization failed: {error}")
            messages.error(request, f"Authentication failed: {error}")
            return redirect('accounts:login')

        # Exchange code for token
        token_url = getattr(settings, 'OAUTH_TOKEN_URL', '')
        client_id = getattr(settings, 'OAUTH_CLIENT_ID', '')
        client_secret = getattr(settings, 'OAUTH_CLIENT_SECRET', '')
        redirect_uri = request.build_absolute_uri(reverse('accounts:sso_oauth_callback'))

        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret,
        }

        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()

        access_token = tokens.get('access_token')
        if not access_token:
            logger.error("No access token in response")
            messages.error(request, "Authentication failed: No access token")
            return redirect('accounts:login')

        # Get user info
        userinfo_url = getattr(settings, 'OAUTH_USERINFO_URL', '')
        headers = {'Authorization': f'Bearer {access_token}'}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo_response.raise_for_status()
        user_data = userinfo_response.json()

        # Authenticate user
        backend = OAuthBackend()
        user = backend.authenticate(request, oauth_data=user_data)

        if user:
            login(request, user, backend='accounts.sso_backends.OAuthBackend')
            messages.success(request, f"Welcome {user.get_full_name()}! You are now logged in via SSO.")
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            logger.error("Failed to create/update user from OAuth data")
            messages.error(request, "Authentication failed. Please contact your administrator.")
            return redirect('accounts:login')

    except requests.exceptions.RequestException as e:
        logger.error(f"OAuth request failed: {str(e)}")
        messages.error(request, "Authentication failed. Please try again.")
        return redirect('accounts:login')
    except Exception as e:
        logger.error(f"OAuth callback failed: {str(e)}")
        messages.error(request, "Authentication failed. Please try again.")
        return redirect('accounts:login')


def sso_logout(request):
    """
    SSO Logout
    Logs out from application and optionally from SSO provider
    """
    sso_type = getattr(settings, 'SSO_TYPE', 'SAML')

    if sso_type == 'SAML' and request.session.get('saml_session_index'):
        # Initiate SAML SLO
        try:
            from onelogin.saml2.auth import OneLogin_Saml2_Auth

            req = prepare_saml_request(request)
            auth = OneLogin_Saml2_Auth(req, custom_base_path=get_saml_settings())

            name_id = request.session.get('saml_nameid')
            session_index = request.session.get('saml_session_index')

            logout(request)
            return redirect(auth.logout(name_id=name_id, session_index=session_index))

        except Exception as e:
            logger.error(f"SAML logout failed: {str(e)}")
            logout(request)
            return redirect('accounts:login')
    else:
        # Standard logout
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect('accounts:login')
