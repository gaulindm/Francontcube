# users/models.py - APRÈS (correct)
import uuid
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import AbstractUser  # ← Vérifie que c'est là!


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username





