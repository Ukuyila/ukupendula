from base64 import urlsafe_b64encode
import time
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, auth
from django.contrib import messages

# Other imports
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

# for email verification
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage, send_mail

from dashboard.models import *
from dashboard.functions import get_device_mac, get_device_info, populate_defaults, validateEmail


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


def emailVerification(request, user, password1, user_team):
    mail_subject = "Activate your user account."
    message = render_to_string("dashboard/email-verification.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
        'password': password1,
        'user_team': user_team.business_name,
        'email': user.email,
        'reply_to': settings.EMAIL_REPLY_TO,
    })
    
    headers = {'Reply-To': settings.EMAIL_REPLY_TO}
    
    email = EmailMessage(mail_subject, message, to=[user.email], reply_to=[settings.EMAIL_REPLY_TO])
    email.content_subtype = 'html'
    if email.send():
        msg = f'Account successfully created, please go to your email {user.email} inbox and click on \
                received activation link to confirm and complete the registration. Note: If not found check spam folder.'
    else:
        msg = f'Problem sending email to {user.email}, check if you typed it correctly.'

    return msg


@anonymous_required
def register(request):
    # populate_defaults()

    if request.method == 'POST':

        email = request.POST['email'].replace(' ', '').lower()
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        spam_filter = request.POST['spam_filter']

        if not validateEmail(email):
            messages.error(request, "Email address invalid!")
            return redirect('register')

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
        
        lang = settings.LANGUAGE_CODE
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
        email = emailVerification(request, user, password1, new_user_team)

        # messages.info(request, email)
        return redirect('login')

        # DIRECT LOGIN IF EMAIL IS VERIFIED
        # auth.login(request, user)
        # return redirect('dashboard')

    return render(request, 'authorisation/register.html', {})


@login_required
def logout(request):

    auth.logout(request)
    return redirect('login')


# def activate(request, uuidToken, uniqueId):  

#     # decode_token = force_str(urlsafe_base64_decode(token))
#     print('token: '.format(uuidToken))
#     # return HttpResponse('Verification link is invalid!')

#     try:  
#         # decode_email = force_str(urlsafe_base64_decode(encodedmail))
#         profile = Profile.objects.get(uniqueId=uniqueId)
#         p_settings = UserSetting.objects.get(profile=profile)
#         user = User.objects.get(profile=profile)
#     except(TypeError, ValueError, OverflowError, User.DoesNotExist, Profile.DoesNotExist):
#         user = None
#         profile = None
#     if user is not None and profile is not None and p_settings.email_verification == uuidToken:

#         user.is_active = True
#         user.save()
#         profile = Profile.objects.get(user=user)
#         profile.is_active = True
#         profile.is_verified = True
#         profile.save()

#         p_settings.email_verification = 'None'
#         p_settings.save()
        
#         redirect('login')
#         return HttpResponse('Thank you for verifying you email. Now you can login your account.')

#     else:
#         return HttpResponse('Verification link is invalid!')


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        profile = Profile.objects.get(user=user)
        profile.is_active = True
        profile.is_verified = True
        profile.save()

        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid!")
        return redirect('login')


def forgot_password(request):

    if request.method == 'POST':
        user_email = request.POST['email']
        print(f'user email: {user_email}')
        
        

    return render(request, 'authorisation/forgot-password.html', {})
