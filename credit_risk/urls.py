from django.urls import path
from . import views

urlpatterns = [
    path('', views.predict_view, name='home'),
    path('batch/', views.batch_predict_view, name='batch_predict'),
    path('historial/', views.historial_view, name='historial'),
    path('evaluacion/<int:pk>/', views.evaluation_detail_view, name='evaluacion_detalle'),
    path('evaluacion/<int:pk>/editar/', views.evaluation_update_view, name='evaluacion_editar'),

]
