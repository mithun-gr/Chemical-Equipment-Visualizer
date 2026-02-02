from django.db import models
from django.contrib.auth.models import User

# Model for storing equipment data
class Equipment(models.Model):
    equipment_name = models.CharField(max_length=200)
    type = models.CharField(max_length=100)  # Pump, Valve, etc
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()
    upload_session = models.ForeignKey('UploadSession', on_delete=models.CASCADE, related_name='equipments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.equipment_name} ({self.type})"
    
    class Meta:
        ordering = ['-created_at']


# Model to track upload history
class UploadSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255)
    total_equipment = models.IntegerField(default=0)
    
    # storing summary stats directly for quick access
    avg_flowrate = models.FloatField(null=True, blank=True)
    avg_pressure = models.FloatField(null=True, blank=True)
    avg_temperature = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"Upload by {self.user.username} on {self.upload_date}"
    
    class Meta:
        ordering = ['-upload_date']  # most recent first
