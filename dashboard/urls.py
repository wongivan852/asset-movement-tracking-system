from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='index'),
    path('api/stats/', views.DashboardStatsAPIView.as_view(), name='stats_api'),
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('reports/export/', views.ExportDataView.as_view(), name='export_data'),
    path('activity-log/', views.ActivityLogView.as_view(), name='activity_log'),
]
