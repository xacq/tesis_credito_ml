from django.db import models
from django.contrib.auth.models import User


class CreditEvaluation(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('OBSERVADO', 'Observado'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Inputs
    edad = models.IntegerField()
    estado_civil = models.CharField(max_length=20)
    ingreso_mensual = models.FloatField()
    ventas_anuales = models.FloatField(default=0)
    monto_solicitado = models.FloatField()
    plazo_meses = models.IntegerField()
    dias_mora_prom = models.IntegerField(default=0)

    garantia = models.CharField(max_length=20)
    tiene_garante = models.BooleanField(default=False)
    propiedad_completa = models.BooleanField(default=False)
    estado_legal = models.BooleanField(default=False)

    # Outputs ML
    prob_riesgo = models.FloatField()
    prediccion = models.IntegerField()  # 0/1
    recomendacion = models.CharField(max_length=10)  # BAJO/MEDIO/ALTO

    # Auditoría / Decisión humana
    estado_caso = models.CharField(max_length=12, choices=ESTADOS, default='PENDIENTE')
    decision_final = models.CharField(max_length=12, choices=ESTADOS, null=True, blank=True)
    comentario_analista = models.TextField(null=True, blank=True)

    cliente_nombres = models.CharField(max_length=120, null=True, blank=True)
    cliente_apellidos = models.CharField(max_length=120, null=True, blank=True)
    cliente_cedula = models.CharField(max_length=10, null=True, blank=True, db_index=True)


    def __str__(self):
        return f"Eval #{self.id} - {self.estado_caso} - {self.created_at:%Y-%m-%d}"
