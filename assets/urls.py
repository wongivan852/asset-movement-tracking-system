from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    # Asset CRUD
    path('', views.AssetListView.as_view(), name='list'),
    path('create/', views.AssetCreateView.as_view(), name='create'),
    path('<int:pk>/', views.AssetDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.AssetUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.AssetDeleteView.as_view(), name='delete'),
    
    # Asset Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    
    # Asset Remarks
    path('<int:asset_id>/remarks/', views.AssetRemarksView.as_view(), name='remarks'),
    path('<int:asset_id>/remarks/add/', views.AddRemarkView.as_view(), name='add_remark'),
    
    # Search and Filter
    path('search/', views.AssetSearchView.as_view(), name='search'),
]
