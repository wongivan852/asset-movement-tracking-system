from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model, authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import jwt
import json

from .models import User
from .forms import UserCreationForm, UserUpdateForm, ProfileUpdateForm
from .sso import SSOTokenManager, sso_client

User = get_user_model()


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'accounts/edit_profile.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin


class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        return User.objects.filter(is_active=True).order_by('username')


class CreateUserView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'accounts/create_user.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'User {form.instance.username} created successfully!')
        return super().form_valid(form)


class EditUserView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/edit_user.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'User {form.instance.username} updated successfully!')
        return super().form_valid(form)


class DeleteUserView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'accounts/delete_user.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def delete(self, request, *args, **kwargs):
        # Soft delete - deactivate instead of actual deletion
        user = self.get_object()
        user.is_active = False
        user.save()
        messages.success(request, f'User {user.username} has been deactivated!')
        return redirect(self.success_url)


# SSO API Views

@csrf_exempt
@require_http_methods(["POST"])
def sso_token_obtain(request):
    """
    Generate SSO tokens for authenticated users.
    
    POST /api/sso/token/
    {
        "username": "john.doe",
        "password": "password123"
    }
    
    Returns:
    {
        "access": "jwt_access_token",
        "refresh": "jwt_refresh_token",
        "user": { ... user data ... }
    }
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse(
                {'error': 'Username and password are required'},
                status=400
            )
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            return JsonResponse(
                {'error': 'Invalid credentials'},
                status=401
            )
        
        if not user.is_active:
            return JsonResponse(
                {'error': 'User account is disabled'},
                status=403
            )
        
        # Generate tokens
        tokens = SSOTokenManager.generate_token(user, request)
        
        # Return user data with tokens
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'department': user.department,
            'employee_id': user.employee_id,
            'is_staff': user.is_staff,
            'is_active': user.is_active,
        }
        
        return JsonResponse({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': user_data,
            'expires_at': tokens['expires_at'].isoformat()
        }, status=200)
        
    except Exception as e:
        return JsonResponse(
            {'error': f'Authentication failed: {str(e)}'},
            status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
def sso_token_refresh(request):
    """
    Refresh access token using refresh token.
    
    POST /api/sso/refresh/
    {
        "refresh": "refresh_token"
    }
    
    Returns:
    {
        "access": "new_jwt_access_token",
        "refresh": "new_jwt_refresh_token"
    }
    """
    try:
        data = json.loads(request.body)
        refresh_token = data.get('refresh')
        
        if not refresh_token:
            return JsonResponse(
                {'error': 'Refresh token is required'},
                status=400
            )
        
        # Refresh token
        tokens = SSOTokenManager.refresh_token(refresh_token, request)
        
        return JsonResponse({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'expires_at': tokens['expires_at'].isoformat()
        }, status=200)
        
    except jwt.ExpiredSignatureError:
        return JsonResponse(
            {'error': 'Refresh token has expired'},
            status=401
        )
    except jwt.InvalidTokenError as e:
        return JsonResponse(
            {'error': f'Invalid refresh token: {str(e)}'},
            status=401
        )
    except User.DoesNotExist:
        return JsonResponse(
            {'error': 'User not found'},
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {'error': f'Token refresh failed: {str(e)}'},
            status=500
        )


@csrf_exempt
@require_http_methods(["POST", "GET"])
def sso_token_validate(request):
    """
    Validate an SSO token.
    
    POST /api/sso/validate/
    Authorization: Bearer <token>
    
    OR
    
    POST /api/sso/validate/
    {
        "token": "jwt_access_token"
    }
    
    Returns:
    {
        "valid": true,
        "user": { ... user data ... }
    }
    """
    try:
        # Get token from Authorization header or request body
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            if request.method == 'POST':
                data = json.loads(request.body)
                token = data.get('token')
            else:
                token = request.GET.get('token')
        
        if not token:
            return JsonResponse(
                {'error': 'Token is required'},
                status=400
            )
        
        # Validate token
        payload = SSOTokenManager.validate_token(token, request)
        
        # Get user from database
        user_id = payload.get('user_id')
        user = User.objects.get(id=user_id)
        
        if not user.is_active:
            return JsonResponse(
                {'valid': False, 'error': 'User account is disabled'},
                status=403
            )
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'department': user.department,
            'employee_id': user.employee_id,
        }
        
        return JsonResponse({
            'valid': True,
            'user': user_data,
            'payload': payload
        }, status=200)
        
    except jwt.ExpiredSignatureError:
        return JsonResponse(
            {'valid': False, 'error': 'Token has expired'},
            status=401
        )
    except jwt.InvalidTokenError as e:
        return JsonResponse(
            {'valid': False, 'error': f'Invalid token: {str(e)}'},
            status=401
        )
    except User.DoesNotExist:
        return JsonResponse(
            {'valid': False, 'error': 'User not found'},
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {'valid': False, 'error': f'Validation failed: {str(e)}'},
            status=500
        )


@csrf_exempt
@require_http_methods(["GET"])
def sso_user_info(request):
    """
    Get user information from Business Platform or local database.
    
    GET /api/sso/user/info/?username=john.doe
    Authorization: Bearer <api_key>
    
    Returns:
    {
        "username": "john.doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        ...
    }
    """
    try:
        username = request.GET.get('username')
        user_id = request.GET.get('id')
        
        if not username and not user_id:
            return JsonResponse(
                {'error': 'Username or ID is required'},
                status=400
            )
        
        # Try to get user from local database
        if user_id:
            user = User.objects.get(id=user_id)
        else:
            user = User.objects.get(username=username)
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'department': user.department,
            'employee_id': user.employee_id,
            'phone': user.phone,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
        }
        
        return JsonResponse(user_data, status=200)
        
    except User.DoesNotExist:
        return JsonResponse(
            {'error': 'User not found'},
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {'error': f'Failed to retrieve user info: {str(e)}'},
            status=500
        )


@csrf_exempt
@require_http_methods(["GET"])
def sso_user_list(request):
    """
    List all users (for synchronization).
    
    GET /api/sso/users/list/
    Authorization: Bearer <api_key>
    
    Returns:
    {
        "users": [
            {"username": "john.doe", ...},
            {"username": "jane.smith", ...}
        ]
    }
    """
    try:
        # Verify API key from request header
        api_key = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        expected_key = getattr(settings, 'BUSINESS_PLATFORM_API_KEY', '')
        
        # For development, allow access without API key or with any key
        # In production, enforce API key validation
        if not settings.DEBUG and api_key != expected_key:
            return JsonResponse(
                {'error': 'Invalid API key'},
                status=401
            )
        
        # Get all active users
        users = User.objects.filter(is_active=True)
        
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'department': user.department,
                'employee_id': user.employee_id,
                'phone': user.phone,
                'is_active': user.is_active,
            })
        
        return JsonResponse({'users': users_data}, status=200)
        
    except Exception as e:
        return JsonResponse(
            {'error': f'Failed to list users: {str(e)}'},
            status=500
        )
