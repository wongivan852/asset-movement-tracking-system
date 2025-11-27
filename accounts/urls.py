from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url='/accounts/password-change-done/'
    ), name='password_change'),
    path('password-change-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='password_change_done'),
    
    # Profile URLs
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    
    # User Management (Admin only)
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.CreateUserView.as_view(), name='create_user'),
    path('users/<int:pk>/edit/', views.EditUserView.as_view(), name='edit_user'),
    path('users/<int:pk>/delete/', views.DeleteUserView.as_view(), name='delete_user'),
    
    # SSO API Endpoints
    path('api/sso/token/', views.sso_token_obtain, name='sso_token_obtain'),
    path('api/sso/refresh/', views.sso_token_refresh, name='sso_token_refresh'),
    path('api/sso/validate/', views.sso_token_validate, name='sso_token_validate'),
    path('api/sso/user/info/', views.sso_user_info, name='sso_user_info'),
    path('api/sso/users/list/', views.sso_user_list, name='sso_user_list'),
]
