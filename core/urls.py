from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from credit_risk.views import CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticación
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Sistema de crédito
    path('', include('credit_risk.urls')),
]
