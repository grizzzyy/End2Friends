from django.db import models
from django.db import models

# Create your models here.

class User(AbstractUser):
    # Add any extra fields here
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username
