from rest_framework import serializers
from .models import Novedad


class NovedadSerializer(serializers.ModelSerializer):
    conductor_nombre = serializers.CharField(
        source="conductor.conductor.nombre", read_only=True
    )
    
    foto = serializers.ImageField(write_only=True, required=False)
    
    class Meta: 
        model = Novedad
        fields = "__all__"
        read_only_fields = ("id_novedad", "conductor", "fecha_novedad", "leida", "imagen")
        
    def create(self, validated_data):

        validated_data.pop('foto', None)
        return super().create(validated_data)