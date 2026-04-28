from django.urls import path
from . import views

urlpatterns = [
    path('payouts/', views.PayoutCreateView.as_view()),
    path('payouts/list/', views.PayoutListView.as_view()),
    path('merchants/<int:merchant_id>/balance/', views.MerchantBalanceView.as_view()),
    path('merchants/<int:merchant_id>/ledger/', views.LedgerView.as_view()),
]