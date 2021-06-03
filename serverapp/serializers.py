from rest_framework import serializers
from .models import *

class AcaoSerializer(serializers.ModelSerializer):
    class Meta:
            model = Acao
            fields = "__all__"

class CalculoAcaoSerializer(serializers.ModelSerializer):
    lstAcoes = AcaoSerializer(many=True)

    class Meta:
            model = CalculoAcao
            fields = "__all__"