import time
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from django.conf import settings

# local imports
from .models import ClientCategory, PermissionLevel, Profile, Team, TeamClient, UserRole, UserSetting


def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        
        lang = settings.LANGUAGE_CODE
        # profile = Profile.objects.get(user=instance)

        # add user team
        new_user_team = Team.objects.create(
            business_name='Default',
            is_active=True,
            business_status=True,
            team_principal=profile.uniqueId,
        )
        new_user_team.save()
        time.sleep(3)

        profile.user_team = new_user_team.uniqueId
        profile.save()

        try:
            permission = PermissionLevel.objects.get(permission_name='Manager')

            #create team manager role
            new_role = UserRole.objects.create(
                role_name='Team Manager',
                abbreviation='TM',
                permission=permission,
                user_team=profile.user_team,
                can_write=True,
                can_edit=True,
                can_delete=True,
                can_create_team=True,
                can_edit_team=True,
                can_delete_team=True,
            )
            new_role.save()

            user_settings = UserSetting.objects.create(
                lang=lang,
                user_role=new_role,
                profile=profile,
            )
            user_settings.save()
        except:
            pass

        # create default client
        new_client = TeamClient.objects.create(
            client_name='Default',
            contact_person=instance.first_name,
            industry='General',
            client_email=instance.email,
            business_address='',
            created_by=profile.uniqueId,
            team=profile.user_team,
        )
        new_client.save()

        # create default category
        new_cate = ClientCategory.objects.create(
            category_name='General',
            description='General category',
            created_by=profile.uniqueId,
            team=profile.user_team,
            client=new_client,
        )
        new_cate.save()


def save_profile(sender, instance, **kwargs):
    instance.profile.save()


post_save.connect(create_profile, sender=User)
post_save.connect(save_profile, sender=User)
