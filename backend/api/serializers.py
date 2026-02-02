from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Equipment, UploadSession

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'  # simple way - include all fields

class UploadSessionSerializer(serializers.ModelSerializer):
    equipment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UploadSession
        fields = ['id', 'filename', 'upload_date', 'total_equipment', 
                  'avg_flowrate', 'avg_pressure', 'avg_temperature', 'equipment_count']
    
    def get_equipment_count(self, obj):
        return obj.equipments.count()  # count related equipments
