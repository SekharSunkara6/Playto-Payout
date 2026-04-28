from django.urls import path
from . import views

urlpatterns = [
    path('merchants/', views.MerchantListView.as_view()),
]