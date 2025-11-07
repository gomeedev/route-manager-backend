from rest_framework import serializers
from .models import Novedad


class NovedadSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Novedad
        fields = "__all__"
        read_only_fields = ("id_novedad", "conductor", "fecha_novedad",)