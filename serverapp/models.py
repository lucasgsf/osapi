from django.db import models
from datetime import date

class CalculoAcao(models.Model):
    # campos do modelo
    vlRisco = models.FloatField()
    dtInicio = models.DateField(default=date.today)
    dtFim = models.DateField(default=date.today)

    def __str__(self):
        return self.vlRisco

class Acao(models.Model):
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome