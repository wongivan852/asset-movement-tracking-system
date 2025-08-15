from django.urls import path
from . import views

app_name = 'movements'

urlpatterns = [
    # Movement Management
    path('', views.MovementListView.as_view(), name='list'),
    path('create/', views.MovementCreateView.as_view(), name='create'),
    path('<int:pk>/', views.MovementDetailView.as_view(), name='detail'),
    path('<int:pk>/acknowledge/', views.AcknowledgeMovementView.as_view(), name='acknowledge'),
    path('<int:pk>/cancel/', views.CancelMovementView.as_view(), name='cancel'),
    
    # Stock Taking
    path('stock-takes/', views.StockTakeListView.as_view(), name='stock_take_list'),
    path('stock-takes/create/', views.StockTakeCreateView.as_view(), name='stock_take_create'),
    path('stock-takes/<int:pk>/', views.StockTakeDetailView.as_view(), name='stock_take_detail'),
    path('stock-takes/<int:pk>/start/', views.StartStockTakeView.as_view(), name='stock_take_start'),
    path('stock-takes/<int:pk>/complete/', views.CompleteStockTakeView.as_view(), name='stock_take_complete'),
    
    # API endpoints
    path('api/track/<str:tracking_number>/', views.TrackMovementAPIView.as_view(), name='track_api'),
]
