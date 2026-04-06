from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('verify/', views.verify, name='verify'),
    path('payment/', views.payment, name='payment'),
    path('result/', views.result, name='result'),
    path('callback/', views.callback, name='callback')
]