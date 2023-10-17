from django.db import models
from django.contrib.auth.models import User

class UploadFile(models.Model):
    file = models.FileField(null=True)  
    status = models.TextField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.file.name
