from django.urls import path
from . import views

urlpatterns = [
    path('', views.predict_view, name='home'),
    path('batch/', views.batch_predict_view, name='batch_predict'),
]   