from django.urls import path
from . import views

app_name = 'studios'

urlpatterns = [
    path('', views.StudioListView.as_view(), name='studio_list'),
    path('add/', views.StudioCreateView.as_view(), name='studio_add'),
    path('search/', views.studio_search, name='studio_search'),
    path('<int:pk>/', views.StudioDetailView.as_view(), name='studio_detail'),
    path('<int:pk>/edit/', views.StudioUpdateView.as_view(), name='studio_edit'),
    path('<int:pk>/delete/', views.StudioDeleteView.as_view(), name='studio_delete'),
    path('<int:studio_id>/add-image/', views.StudioImageCreateView.as_view(), name='studio_add_image'),
    path('image/<int:pk>/delete/', views.StudioImageDeleteView.as_view(), name='studio_image_delete'),
    path('image/<int:pk>/set-main/', views.set_main_image, name='studio_set_main_image'),
]

