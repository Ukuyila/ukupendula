import time
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from django.conf import settings

# local imports
from .models import ClientCategory, PermissionLevel, Profile, Team, TeamClient, UserRole, UserSetting


def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_profile(sender, instance, **kwargs):
    instance.profile.save()


post_save.connect(create_profile, sender=User)
post_save.connect(save_profile, sender=User)
