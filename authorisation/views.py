from base64 import urlsafe_b64encode
import datetime
import time
import smtplib, ssl
import requests
import json
from email.message import EmailMessage
from email.utils import make_msgid, formataddr
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
from django.core.mail import EmailMessage as DjangoEmailMessage, send_mail

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
    context = {}

    if request.method == 'POST':
        email = request.POST['email'].replace(' ', '').lower()
        password = request.POST['password']

        try:
            user_c_actv = User.objects.get(email=email)
            if user_c_actv.is_active:

                user = auth.authenticate(username=email, password=password)
                # print('user_auth: {}'.format(user))
                if user:
                    # user_profile = user.is_active

                    # DIRECT TO PROFILE IF EMAIL IS VERIFIED AND USER DETAILS ARE NOT FILLED OUT
                    if not user.profile.is_verified:
                        messages.error(request, "Your email is not verified, please check your inbox for verification link!")
                        return redirect('login')
                    elif not user.is_active:
                        messages.error(request, "Your account is not active, please contact support if yo!")
                        return redirect('login')
                    else:
                        # login user and redirect
                        auth.login(request, user)
                        return redirect('dashboard')
                else:
                    # post error message
                    messages.error(request, "User email and password does not match any profile!")
                    return redirect('login')
            else:
                # post error message
                messages.error(request, "Email not verified please check your inbox and verify email!")
                return redirect('login')
        except:
            # post error message
            messages.error(request, "User email and password does not match any profile!")
            return redirect('login')

    return render(request, 'authorisation/login.html', context)


def zohoEmailVerification(request, user, password1, user_team):
    resp_msg = ''
    mail_subject = "Verify your email address"
    html_message = render_to_string("authorisation/email-verification.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
        'password': password1,
        'user_team': user_team.business_name,
        'email': user.email,
        'reply_to': settings.EMAIL_REPLY_TO,
        'type_of_action': 'email verification',
    })
    
    # headers = {"Message-ID": str(uuid4())}

    url = "https://api.writesome.ai/mailer-api/welcome-email.php"

    payload = {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
        'password': password1,
        'user_team': user_team.business_name,
        'email': user.email,
        'reply_to': settings.EMAIL_REPLY_TO,
        'type_of_action': 'email verification',
    }
    headers = {
    'accept': "application/json",
    'content-type': "application/json",
    'authorization': "Zoho-enczapikey wSsVR60nqxHzC6Yozj2udLo8nglQU1vwFRl+2geguiP5T/zK9sc/k0HIVw/zGqAcGDQ6RjJGpO4oyx4F1jpb3Ikqy1lVASiF9mqRe1U4J3x17qnvhDzIXGlckxSKLIwLww1tmGVpE89u",
    }
    
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    return json.load(response.text)
    # print(response.text)
    # message_cid = make_msgid()
    
    # email = EmailMessage(mail_subject, message, to=[user.email], reply_to=[settings.EMAIL_REPLY_TO], headers=headers)
    # email.content_subtype = 'html'
#     curr_domain = get_current_site(request).domain
#     message = f'''\
# <html>
# <head></head>
# <body>
# <table cellspacing="0" cellpadding="0" style="margin:0px auto; width: 100%; background-color:#fff;">
#     <tbody>
#         <tr>
#             <td>
#                 <div
#                     style="background-color: #fff; border: 1px solid #eee; box-sizing: border-box; font-family: Lato, Helvetica, 'Helvetica Neue', Arial, 'sans-serif'; margin: auto; max-width: 600px; overflow: hidden; width: 600px;">
#                     <div
#                         style="padding: 65px 90px 20px; background-color: #1B3E71; background-image: url(https://static.zohocdn.com/zeptomail/assets/images/circles.4ee9fbd3db3cd183c76b.svg); background-repeat: no-repeat; background-position: top right; background-size: 140px;">
#                         <h4 style="color: #fff; font-weight: normal; font-size: 16px; margin: 0; margin-bottom: 10px;">
#                             Hi { user.username },<br></h4>
#                         <h2 style="color: #fff; font-size: 24px; font-weight: normal;margin: 0;">Welcome to
#                             writesome!<br></h2>
#                     </div>
#                     <div style="padding: 25px 90px 65px;">
#                         <p style="margin: 0px; line-height: 20px;">
#                             <span class="size" style="font-size: 14px; margin: 0px; line-height: 20px;">We're very glad that you have chosen <b>writesome</b> for your business.</span><br>
#                         </p>
#                         <p style="margin: 25px 0px 0px; line-height: 20px;"><span class="size" style="font-size: 14px; margin: 25px 0px 0px; line-height: 20px;">Your login
#                             information:</span><br></p>
#                         <div style="font-size: 14px; margin: 20px 0 20px 20px;"><br></div>
#                         <div
#                             style="background-color: #F5F7FA; border-radius: 8px; font-size: 14px; padding: 20px; margin-bottom: 30px;">
#                             <div style="display: flex; margin-bottom: 15px;">
#                                 <label style="color: #647282; width: 70px;">Login URL</label>
#                                 <span class="colour" style="color: rgb(100, 114, 130); margin-right: 10px;">:</span> <a
#                                     style="color: #1B3E71; text-decoration: none;"
#                                     href="{  'https' if request.is_secure() else 'http' }://{ get_current_site(request).domain }/auth/login">Login</a><br></div>
#                             <div style="display: flex;"><label style="color: #647282; width: 70px;">Username</label>
#                                 <span class="colour" style="color: rgb(100, 114, 130); margin-right: 10px;">:</span>
#                                 <div>{ user.username }<br></div>
#                             </div>
#                         </div>
#                         <p style="margin: 0px; line-height: 20px;"><span class="size" style="font-size: 14px; margin: 0px; line-height: 20px;">To get started with using your
#                             account, verify your account by clicking on the below link:</span><br></p><a
#                             href="{ 'https' if request.is_secure() else 'http' }://{ get_current_site(request).domain }/auth/activate/{ urlsafe_base64_encode(force_bytes(user.pk)) }/{ account_activation_token.make_token(user) }"
#                             style="border: none; border-radius: 4px; color: #fff; cursor: pointer; display: inline-block; font-size: 14px; font-weight: bold; text-decoration: none; padding: 12px 24px; background-color: #1B3E71; margin: 20px 0 30px;">Verify
#                             your account</a>
#                         <p style="margin: 0px 0px 30px; line-height: 20px;"><span class="size" style="font-size: 14px; margin: 0px 0px 30px; line-height: 20px;">If you'd like to
#                             know more about writesome or want to get in touch with us, get in touch with our
#                             customer support team.</span><br></p>
#                         <p style="margin: 0px 0px 30px; line-height: 20px;"><span class="size" style="font-size: 14px; margin: 0px 0px 30px; line-height: 20px;">If you're looking
#                             for immediate help, take a look at our help documentation and view our latest updates in our
#                             blog.</span><br></p>
#                         <p style="margin: 0px; line-height: 20px;">
#                             <span class="size" style="font-size: 14px; margin: 0px; line-height: 20px;">Thank you,</span><br>
#                         </p>
#                         <p style="margin: 0px; line-height: 20px;">
#                             <span class="size" style="font-size: 14px; margin: 0px; line-height: 20px;">Team.</span><br>
#                         </p>
#                         <div><br></div>
#                         <div class="align-center" style="text-align: center;"><br></div>
#                         <div class="align-center" style="text-align: center;">
#                             <span class="size" style="font-size: 14px; margin: 0px; line-height: 20px;">{ settings.APP_NAME }</span><br>
#                         </div>
#                         <div class="align-center" style="text-align: center;">
#                             <span class="size" style="font-size: 14px; margin: 0px; line-height: 20px;">A product by <a  target="_blank">Ukuyila (Pty)Ltd</a></span><br>
#                         </div>
#                     </div>
#                 </div>
#             </td>
#         </tr>
#     </tbody>
# </table>
# <div><br></div>
# </body>
# </html>
#     '''

#     port = 465
#     smtp_server = settings.EMAIL_HOST
#     username="emailapikey"
#     password = settings.EMAIL_HOST_PASSWORD
#     msg = EmailMessage()
#     msg['Subject'] = mail_subject
#     msg['From'] = formataddr(("writesome", "noreply@writesome.ai"))
#     msg['Reply-To'] = settings.EMAIL_REPLY_TO
#     msg['To'] = user.email
#     msg.set_content(message, subtype='html')
#     # msg.add_alternative(html_message, subtype='html')

#     try:
#         if port == 465:
#             context = ssl.create_default_context()
#             with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
#                 server.login(username, password)
#                 server.send_message(msg)
#         elif port == 587:
#             with smtplib.SMTP(smtp_server, port) as server:
#                 server.starttls()
#                 server.login("emailapikey", password)
#                 server.send_message(msg)
#         else:
#             resp_msg = f'use 465 / 587 as port value.'
#             # exit()
#         resp_msg = f'Account successfully created, please go to your email {user.email} inbox and click on \
#             received activation link to confirm and complete the registration. Note: If not found check spam folder.'
#     except Exception as e:
#         # context['test_email'] = f'error: {e}'
#         resp_msg = f'Problem sending email to {user.email}, check if you typed it correctly. error: {e}'
#     return resp_msg


def emailVerification(request, user, password1, user_team):
    mail_subject = "Activate your user account."
    message = render_to_string("authorisation/email-verification.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http',
        'password': password1,
        'user_team': user_team.business_name,
        'email': user.email,
        'reply_to': settings.EMAIL_REPLY_TO,
        'type_of_action': 'email verification',
    })
    
    headers = {"Message-ID": str(uuid4())}
    
    email = DjangoEmailMessage(mail_subject, message, to=[user.email], reply_to=[settings.EMAIL_REPLY_TO], headers=headers)
    email.content_subtype = 'html'

    if email.send():
        msg = f'Account successfully created, please go to your email {user.email} inbox and click on \
                received activation link to confirm and complete the registration. Note: If not found check spam folder.'
    else:
        msg = f'Problem sending email to {user.email}, check if you typed it correctly.'

    return msg


@anonymous_required
def register(request):
    context = {}
    # populate_defaults()

    if request.method == 'POST':

        email = request.POST['email'].replace(' ', '').lower()
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        # spam_filter = request.POST['spam_filter']

        if not validateEmail(email):
            messages.error(request, "Email address invalid!")
            return redirect('register')

        # if not spam_filter == '9' or spam_filter.upper() == 'NINE':
        #     messages.error(request, "Our robot is not friendly to other robots, you failed the spam test!")
        #     return redirect('register')

        if not password1 == password2:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "User email address {} already in use, please use a different email address!".format(email))
            return redirect('register')

        user = User.objects.create_user(email=email, username=email, password=password1, is_active=False)
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

        profile.is_verified = False
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
        email = zohoEmailVerification(request, user, password1, new_user_team)

        messages.info(request, email)
        return redirect('login')

        # DIRECT LOGIN IF EMAIL IS VERIFIED
        # auth.login(request, user)
        # return redirect('dashboard')
    context['cf_site_key'] = settings.CF_SITE_KEY
    context['cf_private_key'] = settings.CF_PRIVATE_KEY
    return render(request, 'authorisation/register.html', context)


@login_required
def logout(request):

    auth.logout(request)
    return redirect('login')


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

        add_notice = UserNotification.objects.create(
            notice_type='registration',
            notification='Welcome to {}, let us start creating together!'.format(settings.APP_NAME),
            profile=profile
        )
        add_notice.save()

        date_activated = timezone.localtime(timezone.now())

        order_id = str(uuid4()).split('-')[4]
        free_plan_id = settings.FREE_SUBSCR_PACKAGE
        user_team = profile.user_team
        date_expiry = date_activated + datetime.timedelta(days=30)

        order_ref = '{}-{}-{}'.format(profile.uniqueId, free_plan_id, order_id)

        # insert SubscriptionTransaction
        sub_transact = SubscriptionTransaction.objects.create(
            subscription_reference=order_ref,
            user_profile_uid=profile.uniqueId,
            package_name='Free',
            package_price='0',
            has_team=False,
            user_team=user_team,
            date_activated=date_activated,
            date_expiry=date_expiry,
        )
        sub_transact.save()

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
