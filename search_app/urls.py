from django.urls import path
from . import views
urlpatterns = [
    path('', views.search_view, name='search_view'),
    path('search/', views.search_view, name='search_view'),
    path('search/ajax/', views.ajax_search_view, name='ajax_search'),
    path('search/history/', views.search_history_list, name='search_history_list'),
    path('api/search/', views.ProductSearchAPI.as_view(), name='product-search-api'),
    path('product/new/', views.product_create, name='product_create'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/edit/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('set_language/', views.set_language_view, name='set_language'),
    path('product/<int:product_id>/toggle_like/', views.toggle_like, name='toggle_like'),
]