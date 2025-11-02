from rest_framework import serializers
from .models import Empresa

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ("id_empresa", "nit", "nombre_empresa", "telefono_empresa")
        read_only_fields = ("id_empresa",)