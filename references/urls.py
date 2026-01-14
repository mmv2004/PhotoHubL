from django.urls import path
from . import views

app_name = 'references'

urlpatterns = [
    path('', views.ReferenceListView.as_view(), name='reference_list'),
    path('search/', views.reference_search, name='reference_search'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('add/', views.ReferenceCreateView.as_view(), name='reference_add'),
    path('<int:pk>/', views.ReferenceDetailView.as_view(), name='reference_detail'),
    path('<int:pk>/edit/', views.ReferenceUpdateView.as_view(), name='reference_edit'),
    path('<int:pk>/delete/', views.ReferenceDeleteView.as_view(), name='reference_delete'),
    path('category/<int:category_id>/', views.ReferencesByCategoryView.as_view(), name='references_by_category'),
]

