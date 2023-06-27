import time
from django.conf import Settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages

# Other imports
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

# for email verification
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage, send_mail

from dashboard.models import *
from dashboard.functions import get_device_mac, get_device_info


def anonymous_required(function=None, redirect_url=None):

    if not redirect_url:
        redirect_url = 'dashboard'

    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous,
        login_url=redirect_url
    )

    if function:
        return actual_decorator(function)
    return actual_decorator


@anonymous_required
def login(request):
    if request.method == 'POST':
        email = request.POST['email'].replace(' ', '').lower()
        password = request.POST['password']

        user = auth.authenticate(username=email, password=password)

        if user:
            # login user and redirect
            auth.login(request, user)
            return redirect('dashboard')

        else:
            # post error message
            messages.error(request, "User email and password does not match any profile!")
            return redirect('login')

    return render(request, 'authorisation/login.html', {})


@anonymous_required
def register(request):

    if request.method == 'POST':

        email = request.POST['email'].replace(' ', '').lower()
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        spam_filter = request.POST['spam_filter']

        if not spam_filter == '9' or spam_filter.upper() == 'NINE':
            messages.error(request, "Our robot is not friendly to other robots, You failed the spam filter!")
            return redirect('register')

        if not password1 == password2:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "User email address {} already exists, please use a different email address!".format(email))
            return redirect('register')

        user = User.objects.create_user(email=email, username=email, password=password1)
        user.save()

        time.sleep(2)
        
        lang = Settings.LANGUAGE_CODE
        profile = Profile.objects.get(user=user)

        # add user team
        new_user_team = Team.objects.create(
            business_name='Default',
            is_active=True,
            business_status=True,
            team_principal=profile.uniqueId,
        )
        new_user_team.save()
        time.sleep(2)

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
            contact_person='first_name',
            industry='General',
            client_email=email,
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

        # begin email verification
        # to get the domain of the current site
        # current_site = get_current_site(request)
        # mail_subject = 'Email verification for writesome.ai'
        # message = render_to_string('authorisation/email-verification.html', {
        #     'user': user,
        #     'domain': current_site.domain,
        #     'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        #     'token':account_activation_token.make_token(user),
        # })
        # to_email = email
        # email = EmailMessage(mail_subject, message, to=[to_email])
        # email.send()

        # # send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=False)

        # messages.info(request, "Email verification link has been sent to email address {}, please verify your email to start creating!".format(email))
        # return redirect('register')

        # DIRECT LOGIN IF EMAIL IS VERIFIED
        auth.login(request, user)
        return redirect('dashboard')

    return render(request, 'authorisation/register.html', {})


@login_required
def logout(request):

    auth.logout(request)
    return redirect('login')


def activate(request, token, uniqueId):  

    # decode_token = force_str(urlsafe_base64_decode(token))
    print('decode_emai: '.format(token))
    return None

    # try:  
    #     decode_email = force_str(urlsafe_base64_decode(encodedmail))
    #     profile = Profile.objects.get(uniqueId=uniqueId)
    #     p_settings = UserSetting.objects.get(profile=profile)
    #     user = User.objects.get(profile=profile)
    # except(TypeError, ValueError, OverflowError, User.DoesNotExist, Profile.DoesNotExist):
    #     user = None
    #     profile = None
    # if user is not None and profile is not None and p_settings.email_verification == token:

    #     user.is_active = True
    #     user.save()
    #     profile = Profile.objects.get(user=user)
    #     profile.is_active = True
    #     profile.is_verified = True
    #     profile.save()
        
    #     redirect('login')
    #     return HttpResponse('Thank you for verifying you email. Now you can login your account.')

    # else:
    #     return HttpResponse('Verification link is invalid!')


def forgot_password(request):

    return render(request, 'authorisation/forgot-password.html', {})
