from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import sso_views

app_name = 'accounts'

urlpatterns = [
    # SSO Authentication URLs
    path('sso/login/', sso_views.sso_login, name='sso_login'),
    path('sso/logout/', sso_views.sso_logout, name='sso_logout'),

    # SAML URLs
    path('sso/saml/acs/', sso_views.saml_acs, name='sso_saml_acs'),
    path('sso/saml/sls/', sso_views.saml_sls, name='sso_saml_sls'),
    path('sso/saml/metadata/', sso_views.saml_metadata, name='sso_saml_metadata'),

    # OAuth URLs
    path('sso/oauth/callback/', sso_views.oauth_callback, name='sso_oauth_callback'),

    # Standard Authentication URLs
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
]
