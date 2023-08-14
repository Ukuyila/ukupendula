import datetime
import hashlib
import time
import urllib.parse

# payfast imports
import requests
import urllib.parse
import socket
import json

from werkzeug.urls import url_parse

from django_gravatar.helpers import get_gravatar_url, has_gravatar, get_gravatar_profile_url, calculate_gravatar_hash
# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings

# Other Auth imports
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

from uuid import uuid4

# local imports.
from .forms import *
from .models import *
from .functions import *
from authorisation.tokens import account_activation_token
from django.template.defaulttags import register


@register.filter(name='split')
def split(value, key):
    value.split("key")
    return value.split(key)


@login_required
def home(request):
    context = {}

    try:
        user_profile = request.user.profile
    except:
        user_profile = Profile.objects.create(user=request.user)

    user_team_id = user_profile.user_team

    empty_blogs = []
    complete_blogs = []

    today_date = datetime.datetime.now()

    remove_api_requests(user_profile)

    remote_addr = get_client_ip(request)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    q_year = today_date.year
    q_month = today_date.month

    # gravatar
    g_user_email = request.user.email

    # DIRECT TO PROFILE IF EMAIL IS VERIFIED AND USER DETAILS ARE NOT FILLED OUT
    if not user_profile.is_verified:
        messages.error(request, "Your email is not verified, please check your inbox for verification link!")
        return redirect('login')

    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request, "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    # Get total blogs
    blogs = Blog.objects.filter(profile=user_profile)

    for blog in blogs:
        if not blog.deleted and blog.profile.user_team == user_team_id:
            sections = BlogSection.objects.filter(blog=blog)
            if sections.exists():
                # calculate blog words
                blog_words = 0
                for section in sections:
                    blog_words += int(section.word_count)

                    # month_word_count += int(section.word_count)
                if blog.word_count is None or int(blog.word_count) == 0:
                    blog.word_count = str(blog_words)
                    blog.save()
                complete_blogs.append(blog)
            elif not sections.exists():
                empty_blogs.append(blog)

    try:
        lst_subscr_trans = SubscriptionTransaction.objects.filter(profile=profile, is_active=True).order_by(
            'date_created')[:1]
        lst_subscr_exp = lst_subscr_trans.date_created

        days_between = datetime_difference(today_date, lst_subscr_exp, 'second')
        if int(days_between) < 0:
            # reset monthly limits
            profile.monthly_count = '0'
            profile.monthly_memory_count = '0'
            profile.save()

    except:
        # lst_subscr_exp = timezone.localtime(timezone.now())
        pass

    blog_word_cnt = get_blog_word_cnt(str(q_year), str(q_month), user_profile)
    lm_blog_word_cnt = get_blog_word_cnt(str(q_year), str(q_month - 1), user_profile)

    para_word_cnt = get_para_word_cnt(str(q_year), str(q_month), user_profile)
    lm_para_word_cnt = get_para_word_cnt(str(q_year), str(q_month - 1), user_profile)

    sentence_word_cnt = get_sentence_word_cnt(str(q_year), str(q_month), user_profile)
    lm_sentence_word_cnt = get_sentence_word_cnt(str(q_year), str(q_month - 1), user_profile)

    meta_word_cnt = get_meta_word_cnt(str(q_year), str(q_month), user_profile)
    lm_meta_word_cnt = get_meta_word_cnt(str(q_year), str(q_month - 1), user_profile)

    summarizer_word_cnt = get_summarizer_word_cnt(str(q_year), str(q_month), user_profile)
    lm_summarizer_word_cnt = get_summarizer_word_cnt(str(q_year), str(q_month - 1), user_profile)

    landing_copy_word_cnt = get_land_copy_word_cnt(str(q_year), str(q_month), user_profile)
    lm_landing_copy_word_cnt = get_land_copy_word_cnt(str(q_year), str(q_month - 1), user_profile)

    context['month_word_count'] = user_profile.monthly_count
    context['blog_word_cnt'] = blog_word_cnt
    context['para_word_cnt'] = para_word_cnt
    context['sentence_word_cnt'] = sentence_word_cnt
    context['meta_word_cnt'] = meta_word_cnt
    context['landing_copy_word_cnt'] = landing_copy_word_cnt
    context['summarizer_word_cnt'] = summarizer_word_cnt

    # find percentage from last month
    if int(blog_word_cnt) > int(lm_blog_word_cnt):
        context['clm_blog_word_cnt'] = get_percent_of(lm_blog_word_cnt, blog_word_cnt)
        if lm_blog_word_cnt < 1:
            context['clm_blog_word_cnt'] = 100
        context['blg_carret_set'] = ' fa-caret-up text-success '
    else:
        context['clm_blog_word_cnt'] = get_percent_of(blog_word_cnt, lm_blog_word_cnt)
        if blog_word_cnt < 1:
            context['clm_blog_word_cnt'] = 100
        context['blg_carret_set'] = ' fa-caret-down text-danger '

    if int(summarizer_word_cnt) > int(lm_summarizer_word_cnt):
        context['clm_summarizer_word_cnt'] = get_percent_of(lm_summarizer_word_cnt, summarizer_word_cnt)
        if lm_summarizer_word_cnt < 1:
            context['clm_summarizer_word_cnt'] = 100
        context['sumry_carret_set'] = ' fa-caret-up text-success '
    else:
        context['clm_summarizer_word_cnt'] = get_percent_of(summarizer_word_cnt, lm_summarizer_word_cnt)
        if summarizer_word_cnt < 1:
            context['clm_summarizer_word_cnt'] = 100
        context['sumry_carret_set'] = ' fa-caret-down text-danger '

    if int(meta_word_cnt) > int(lm_meta_word_cnt):
        context['clm_meta_word_cnt'] = get_percent_of(lm_meta_word_cnt, meta_word_cnt)
        if lm_meta_word_cnt < 1:
            context['clm_meta_word_cnt'] = 100
        context['meta_carret_set'] = ' fa-caret-up text-success '
    else:
        context['clm_meta_word_cnt'] = get_percent_of(meta_word_cnt, lm_meta_word_cnt)
        if meta_word_cnt < 1:
            context['clm_meta_word_cnt'] = 100
        context['meta_carret_set'] = ' fa-caret-down text-danger '

    if int(landing_copy_word_cnt) > int(lm_landing_copy_word_cnt):
        context['clm_landing_copy_word_cnt'] = get_percent_of(lm_landing_copy_word_cnt, landing_copy_word_cnt)
        if lm_landing_copy_word_cnt < 1:
            context['clm_landing_copy_word_cnt'] = 100
        context['lpc_carret_set'] = ' fa-caret-up text-success '
    else:
        context['clm_landing_copy_word_cnt'] = get_percent_of(landing_copy_word_cnt, lm_landing_copy_word_cnt)
        if landing_copy_word_cnt < 1:
            context['clm_landing_copy_word_cnt'] = 100
        context['lpc_carret_set'] = ' fa-caret-down text-danger '


    
    context['clm_para_word_cnt'] = para_word_cnt
    context['clm_sentence_word_cnt'] = sentence_word_cnt

    context['num_blogs'] = len(complete_blogs)

    # context['count_reset'] = lst_subscr_trans.date_expiry  # update later

    context['empty_blogs'] = empty_blogs
    context['complete_blogs'] = complete_blogs

    user_notifcs = []
    cnt_notif = 0

    user_notifics = user_notices(user_profile)
    for notif in user_notifics:
        user_notifcs.append(notif)
        cnt_notif+=1

    context['cnt_notif'] = cnt_notif
    context['user_notices'] = user_notifcs

    context['allowance'] = check_count_allowance(user_profile)

    current_page = 'Home'
    context['current_page'] = current_page

    return render(request, 'dashboard/index.html', context)


@login_required
def edit_settings(request):
    user_profile = request.user.profile
    user_settings = UserSetting.objects.get(profile=user_profile)

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request, "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    if request.method == 'POST':

        user_settings.lang = request.POST['user_lang']
        user_settings.website_link = request.POST['user_website']
        user_settings.twitter_link = request.POST['user_twitter']
        user_settings.facebook_link = request.POST['user_facebook']
        user_settings.instagram_link = request.POST['user_instagram']
        user_settings.linkedin_link = request.POST['user_linkedin']

        user_email_notify = request.POST.get('email_notify', user_settings.email_notify)
        user_email_notify_multi = request.POST.get('multi_email_notify', user_settings.multiple_email_notify)

        # print('user_email_notify: '.format(user_email_notify_multi))
        # breakpoint

        user_settings.email_notify = True if user_email_notify == 'on' else False
        user_settings.multiple_email_notify = True if user_email_notify_multi == 'on' else False

        try:
            user_settings.save()
            resp = "User settings saved successfully!"
        except:
            resp = "Something is a foot"

    return HttpResponse(resp)


@login_required
def profile(request):
    context = {}

    current_page = 'My Profile'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(request.user.profile)

    remove_api_requests(request.user.profile)

    user_profile = request.user.profile
    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    user_settings = UserSetting.objects.get(profile=user_profile)

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request, "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['user_settings'] = user_settings
    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    if request.method == 'GET':
        profile_form = ProfileForm(instance=request.user.profile, user=request.user)

        context['profile_form'] = profile_form

        return render(request, 'dashboard/profile.html', context)

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=request.user.profile, user=request.user)

        if profile_form.is_valid():
            profile_form.save()
            return redirect('profile')
        else:
            messages.error(request, "Error! Failed to update user profile details!")
            return redirect('profile')

        # if image_form.is_valid():
        #     image_form.save()
        #     return redirect('profile')

    return render(request, 'dashboard/profile.html', context)


@login_required
def blog_topic(request):
    context = {}

    tone_of_voices = []
    current_page = 'Blog Topic Generator'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(request.user.profile)

    remove_api_requests(request.user.profile)

    cate_list = []
    client_list = []

    user_profile = request.user.profile

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_profile.user_team)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    tones = ToneOfVoice.objects.filter(tone_status=True)

    for tone in tones:
        tone_of_voices.append(tone)

    context['tone_of_voices'] = tone_of_voices

    if request.method == 'POST':
        cate_id = request.POST['category']
        request.session['category'] = cate_id

        blog_idea = request.POST['blog_idea']
        request.session['blog_idea'] = blog_idea

        keywords = request.POST['keywords']
        request.session['keywords'] = keywords

        audience = request.POST['audience']
        request.session['audience'] = audience

        tone_of_voice = request.POST['tone_of_voice']
        request.session['tone_of_voice'] = tone_of_voice

        if int(request.POST['max_words']) < 300:
            max_words = 300
        elif int(request.POST['max_words']) > 1500:
            max_words = 1500
        else:
            max_words = int(request.POST['max_words'])

        request.session['max_words'] = max_words

        if len(blog_idea) > 250 or len(keywords) > 250 or len(audience) > 250:
            messages.error(request, "The engine could not generate blog ideas, please try again!")
            return redirect('blog-topic')
        else:
            api_call_code = str(uuid4()).split('-')[4]

            # api_requests = check_api_requests()

            add_to_list = add_to_api_requests('generate_blog_topic_ideas', api_call_code, request.user.profile)

            n = 1
            # runs until n < 50,just to avoid the infinite loop.
            # this will execute the check_api_requests() func in every 5 seconds.
            while n < 50:
                # api_requests = check_api_requests()
                time.sleep(5)
                if api_call_process(api_call_code, add_to_list):
                    blog_topics = generate_blog_topic_ideas(user_profile, blog_idea, audience, keywords)

                    add_to_list.is_done = True
                    add_to_list.save()
                    if len(blog_topics) > 0:

                        request.session['blog_topics'] = blog_topics
                        return redirect('blog-sections')
                    else:
                        messages.error(request, "The engine could not generate blog ideas, please try again!")
                        return redirect('blog-topic')
                else:
                    # we might need to delete all abandoned calls
                    pass

                n += 1

    return render(request, 'dashboard/blog-topic.html', context)


@login_required
def blog_sections(request):
    context = {}

    current_page = 'Blog Topic Generator'

    remove_api_requests(request.user.profile)

    user_profile = request.user.profile

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    if 'blog_topics' in request.session:
        pass
    else:
        messages.error(request, "You have to create blog topic first!")
        return redirect('blog-topic')

    context = {'current_page': current_page, 'allowance': check_count_allowance(request.user.profile),
               'blog_topics': request.session['blog_topics']}

    return render(request, 'dashboard/blog-sections.html', context)


@login_required
def delete_blog_topic(request, uniqueId):
    try:
        blog = Blog.objects.get(uniqueId=uniqueId)
        if blog.profile == request.user.profile:
            blog.delete()
            messages.info(request, "Blog deleted successfully!")
            return redirect('blog-memory', 'incomplete')
        else:
            messages.error(request, "Access denied!")
            return redirect('blog-memory', 'incomplete')
    except:
        messages.error(request, "Blog not found!")
        return redirect('blog-memory', 'incomplete')


@login_required
def delete_blog(request, uniqueId):
    try:
        blog = Blog.objects.get(uniqueId=uniqueId)
        if blog.profile == request.user.profile:
            blog.deleted = True
            blog.save()
            messages.info(request, "Blog deleted successfully!")
            return redirect('blog-memory', 'complete')
        else:
            messages.error(request, "Access denied!")
            return redirect('blog-memory', 'complete')
    except:
        messages.error(request, "Blog not found!")
        return redirect('blog-memory', 'complete')


@login_required
def delete_saved_blog(request, uniqueId):
    try:
        blog = Blog.objects.get(uniqueId=uniqueId)
        if blog.profile == request.user.profile:

            saved_blogs = SavedBlogEdit.objects.all()
            for s_blog in saved_blogs:
                if s_blog.blog == blog:
                    s_blog.delete()

            messages.info(request, "Blog deleted successfully!")
            return redirect('blog-memory', 'saved')
        else:
            messages.error(request, "Access denied!")
            return redirect('blog-memory', 'saved')
    except:
        messages.error(request, "Blog not found!")
        return redirect('blog-memory', 'saved')


@login_required
def save_blog_topic(request, blog_topic):
    remove_api_requests(request.user.profile)

    if 'blog_idea' in request.session and 'keywords' in request.session and 'audience' in request.session and 'blog_topics' in request.session:
        blog = Blog.objects.create(
            title=blog_topic,
            blog_idea=request.session['blog_idea'],
            keywords=request.session['keywords'],
            audience=request.session['audience'],
            tone_of_voice=request.session['tone_of_voice'],
            max_words=str(request.session['max_words']),
            profile=request.user.profile,
        )
        blog.save()

        blog_topics = request.session['blog_topics']
        blog_topics.remove(blog_topic)
        request.session['blog_topics'] = blog_topics

        request.session['uniqueId'] = blog.uniqueId

        return redirect('blog-sections')
    else:
        return redirect('blog-topic')


# This generates blog from session topic
@login_required
def use_blog_topic(request, blog_topic):
    blog_topic = requests.utils.unquote(blog_topic)
    print('Blog topic: '.format(blog_topic))
    context = {}

    user_profile = request.user.profile

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    current_page = 'Use Blog Sections Generator'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(user_profile)

    remove_api_requests(user_profile)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    if 'blog-sections' in request.session and 'uniqueId' in request.session:

        uniqueId = request.session['uniqueId']
        context['uniqueId'] = uniqueId
        blog_section_heads = request.session['blog-sections']

        blog = Blog.objects.get(uniqueId=uniqueId)

        if 'saved-sect-head' == request.session:
            saved_sect_head = request.session['saved-sect-head']
            context['saved-sect-head'] = saved_sect_head
    else:
        if 'blog_idea' in request.session and 'keywords' in request.session and 'audience' in request.session:
            cate_id = request.session['category'] if request.session['category'] else ''
            # category = ClientCategory.objects.get(uniqueId=cate_id)
            # save blog topic idea first
            # code to save
            blog = Blog.objects.create(
                title=blog_topic,
                blog_idea=request.session['blog_idea'],
                keywords=request.session['keywords'],
                audience=request.session['audience'],
                tone_of_voice=request.session['tone_of_voice'],
                profile=request.user.profile,
                category=cate_id,
            )
            blog.save()

            context['uniqueId'] = blog.uniqueId
            request.session['uniqueId'] = blog.uniqueId

            api_call_code = str(uuid4()).split('-')[4]

            # api_requests = check_api_requests()

            add_to_list = add_to_api_requests('generate_blog_section_headings', api_call_code, request.user.profile)

            n = 1
            # runs until n < 50,just to avoid the infinite loop.
            # this will execute the check_api_requests() func in every 5 seconds.
            while n < 50:
                # api_requests = check_api_requests()
                time.sleep(5)
                if api_call_process(api_call_code, add_to_list):
                    blog_section_heads = generate_blog_section_headings(user_profile, blog_topic,
                                                                        request.session['audience'],
                                                                        request.session['keywords'])

                    add_to_list.is_done = True
                    add_to_list.save()
                    break
                else:
                    # we might need to delete all abandoned calls
                    pass
                n += 1
        else:
            return redirect('blog-topic')

    if len(blog_section_heads) > 0:
        # Adding the sections to the session
        request.session['blog-sections'] = blog_section_heads

        # adding the sections to the context
        context['blog_sections'] = blog_section_heads

    else:
        messages.error(request, "The engine could not generate blog sections, please try again!")
        return redirect('blog-topic')

    if request.method == 'POST':
        request.session['selectd_sections'] = request.POST

        return redirect('view-gen-blog', slug=blog.slug)

    return render(request, 'dashboard/select-blog-sections.html', context)


# this generates blog from saved topic
@login_required
def create_blog_from_topic(request, uniqueId):
    context = {}

    user_profile = request.user.profile

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    current_page = 'Use Blog Sections Generator'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(request.user.profile)
    request.session['uniqueId'] = uniqueId

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    try:
        blog = Blog.objects.get(uniqueId=uniqueId)
        api_call_code = str(uuid4()).split('-')[4]

        add_to_list = add_to_api_requests('generate_blog_section_headings', api_call_code, request.user.profile)

        n = 1
        # runs until n < 50,just to avoid the infinite loop.
        # this will execute the check_api_requests() func in every 5 seconds.
        while n < 50:
            # api_requests = check_api_requests()
            time.sleep(5)
            if api_call_process(api_call_code, add_to_list):
                blog_section_heads = generate_blog_section_headings(user_profile, blog.title, blog.audience,
                                                                    blog.keywords)

                add_to_list.is_done = True
                add_to_list.save()
                time.sleep(5)
                break
            else:
                # we might need to delete all abandoned calls
                pass
            n += 1

        if len(blog_section_heads) > 0:
            # Adding the sections to the session
            request.session['blog-sections'] = blog_section_heads
            # adding the sections to the context
            context['blog_sections'] = blog_section_heads

        else:
            messages.error(request, "The engine could not generate blog sections, please try again!")
            return redirect('blog-topic')

        if request.method == 'POST':
            request.session['selectd_sections'] = request.POST
            return redirect('view-gen-blog', slug=blog.slug)

    except:
        messages.error(request, "Blog not found!")
        redirect('dashboard')

    return render(request, 'dashboard/select-blog-sections.html', context)


@login_required
def save_section_head(request, uniqueId, section_head):
    context = {}

    blog = Blog.objects.get(uniqueId=uniqueId)
    section_head = requests.utils.unquote(section_head)

    if blog:
        blog_topic = urllib.parse.quote(blog.title)

        saved_sect_head = SavedBlogSectionHead.objects.create(
            section_head=section_head,
            blog=blog,
        )
        saved_sect_head.save()

        blog_section_heads = request.session['blog-sections']
        context['uniqueId'] = blog.uniqueId
        request.session['uniqueId'] = blog.uniqueId
        # adding the sections to the context
        request.session['saved-sect-head'] = section_head
        context['blog_sections'] = blog_section_heads
        print("saved: ".format(section_head))
        return redirect('use-blog-topic', blog_topic)
    else:
        return redirect('blog-sections')


@login_required
def view_gen_blog(request, slug):
    user_profile = request.user.profile
    context = {}
    current_page = 'Blog Generator'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(user_profile)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    min_words = 300

    try:
        blog = Blog.objects.get(slug=slug)
    except:
        messages.error(request, "Something went wrong with your request, please try again!")
        return redirect('blog-topic')

    if 'selectd_sections' in request.session:

        sect_cnt = 1
        total_sect_heads = len(request.session['selectd_sections'])
        section_heads = ""

        if total_sect_heads > 0:
            # section_heads = '\n'.join(map(str, request.session['selectd_sections']))

            for val in request.session['selectd_sections']:
                if not 'csrfmiddlewaretoken' in val:
                    # prev_blog = ''

                    # convert selectd_sections list to a prog string
                    if section_heads:
                        section_heads = section_heads + '\n'

                    section_heads = section_heads + val
                    api_call_code = str(uuid4()).split('-')[4]
                    add_to_list = add_to_api_requests('generate_full_blog', api_call_code, request.user.profile)

                    n = 1
                    # runs until n < 50,just to avoid the infinite loop.
                    # this will execute the check_api_requests() func in every 5 seconds.
                    while n < 50:
                        # api_requests = check_api_requests()
                        time.sleep(5)
                        if api_call_process(api_call_code, add_to_list):
                            gen_section = generate_full_blog(blog.title, section_heads, blog.audience, blog.keywords,
                                                             blog.tone_of_voice, min_words, blog.max_words,
                                                             request.user.profile)

                            # create database record
                            blog_sect = BlogSection.objects.create(
                                title=blog.title,
                                body=gen_section,
                                blog=blog,
                            )
                            blog_sect.save()

                            add_to_list.is_done = True
                            add_to_list.save()

                            # fetch created blog sections
                            blog_sects = BlogSection.objects.filter(blog=blog)

                            del request.session['uniqueId']
                            del request.session['blog-sections']
                            del request.session['selectd_sections']
                            del request.session['blog_idea']
                            del request.session['keywords']
                            del request.session['audience']

                            try:
                                del request.session['saved-sect-head']
                            except:
                                request.session.modified = True

                            request.session.modified = True

                            context['blog'] = blog
                            context['blog_sects'] = blog_sects

                            return redirect('view-generated-blog', slug=blog.slug)

                        else:
                            # we might need to delete all abandoned calls
                            pass
                        n += 1
                    sect_cnt += 1
        else:
            messages.error(request, "Something went wrong with your request, please try again!")
            return redirect('blog-topic')

    return render(request, 'dashboard/view-generated-blog.html', context)


def edit_gen_blog(request, uniqueId):
    context = {}
    current_page = 'Edit Generated Blog'
    # parent_page = 'Blog Generator'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(request.user.profile)

    cate_list = []
    client_list = []

    user_profile = request.user.profile
    team_clients = TeamClient.objects.filter(is_active=True)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_profile.user_team)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    try:
        blog = Blog.objects.get(uniqueId=uniqueId)
    except:
        messages.error(request, "Something went wrong with your request, please try again!")
        return redirect('blog-topic')

    blog_sections = []
    # got_b_body = False
    s_blog_body = ''
    s_blog_title = ''

    try:
        saved_blog_sect = SavedBlogEdit.objects.get(blog=blog)
        if saved_blog_sect is not None:
            #     for blog_sect in saved_blog_sects:
            blog_sections.append(saved_blog_sect.body)
            blog_title = saved_blog_sect.title

        else:
            saved_blog = SavedBlogEdit.objects.create(
                title=blog.title,
                body=blog_body_sect,
                blog=blog,
            )
            saved_blog.save()
            blog_sections.append(saved_blog.body)

            blog_title = saved_blog.title

    except:
        gen_sections = BlogSection.objects.filter(blog=blog)
        for blog_sect in gen_sections:
            this_blog_body = blog_sect.body
            blog_sections.append(this_blog_body)

        blog_body_sect = "\n".join(blog_sections).replace('<br>', '\n')

        saved_blog = SavedBlogEdit.objects.create(
            title=blog.title,
            body=blog_body_sect,
            blog=blog,
        )
        saved_blog.save()
        blog_title = saved_blog.title
        blog_sections.append(saved_blog.body)

    # saved_blogs = SavedBlogEdit.objects.all()
    # for s_blog in saved_blogs:
    #     if s_blog.blog == blog:
    #         got_b_body = True
    #         s_blog_title = s_blog.title
    #         s_blog_body = s_blog.body
    #         saved_blog = s_blog
    #         break

    # if got_b_body == True:
    #     blog_body = s_blog_body
    #     blog_title = s_blog_title

    # else:
    #     blog_sects = BlogSection.objects.filter(blog=blog)

    #     for blog_sect in blog_sects:
    #         blog_title = blog_sect.title
    #         blog_sections.append(blog_sect.body)

    #     blog_body = "\n".join(blog_sections).replace('<br>', '\n')

    #     saved_blog = SavedBlogEdit.objects.create(
    #         title=blog.title,
    #         body=blog_body,
    #         blog=blog,
    #     )
    #     saved_blog.save()
    #     blog_sections.append(saved_blog.body)

    s_blog_body = "\n".join(blog_sections).replace('\n', '<br>')
    # s_blog_body = "\n".join(blog_sections)

    s_blog_title = blog_title

    context['blog'] = blog
    context['blog_title'] = s_blog_title
    context['blog_audience'] = blog.audience
    context['uniqueId'] = uniqueId
    # context['saved_blog'] = saved_blog
    context['blog_body'] = s_blog_body
    context['blog_cate'] = blog.category

    if request.method == 'POST':
        blog_title = request.POST['blog-title']
        generated_blog_edit = request.POST['generated-blog']
        gen_blog_category = request.POST['category']

        saved_blog_sect.title = blog_title
        saved_blog_sect.body = generated_blog_edit
        saved_blog_sect.category = gen_blog_category
        saved_blog_sect.save()

        return redirect('edit-gen-blog', uniqueId)

        # print('new title: {}'.format(blog_title))

    return render(request, 'dashboard/edit-generated-blog.html', context)


@login_required
def view_blog_social_post(request, postType, uniqueId):
    context = {}
    user_profile = request.user.profile
    current_page = 'View Blog Social Post'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(user_profile)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    blog_posts = []
    tone_of_voices = []

    tones = ToneOfVoice.objects.filter(tone_status=True)

    for tone in tones:
        tone_of_voices.append(tone)

    context['tone_of_voices'] = tone_of_voices

    blogs = Blog.objects.filter(profile=request.user.profile)

    for blog in blogs:
        if not blog.deleted:
            sections = BlogSection.objects.filter(blog=blog)
            if sections.exists():
                blog_posts.append(blog)

    context['blog_posts'] = blog_posts

    try:
        post = BlogSocialPost.objects.get(uniqueId=uniqueId)
    except:
        messages.error(request, "Something went wrong with your request, please try again!")
        return redirect('gen-blog-social-media', postType, uniqueId)

    # post_type = postType.replace('_', ' ').title()
    soc_types_list = []

    soc_types = SocialPlatform.objects.filter(is_active=True)
    for soc_typ in soc_types:
        soc_types_list.append(soc_typ)

    context['soc_types_list'] = soc_types_list

    sel_p_typ = SocialPlatform.objects.get(post_name=postType)
    max_char = sel_p_typ.max_char

    context['post_type_title'] = sel_p_typ.post_name.title()
    context['post_type'] = sel_p_typ.post_name
    context['social_post'] = post
    context['post_blog'] = post.blog
    context['post_title'] = post.title
    context['max_char'] = max_char
    context['post_body'] = post.post
    context['post_audience'] = post.audience
    context['post_keywords'] = post.keywords
    context['post_tone'] = post.tone_of_voice

    return render(request, 'dashboard/social-media-post.html', context)


@login_required
def generate_social_media(request):
    context = {}
    user_profile = request.user.profile

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    if request.method == "POST":

        post_title = request.POST['post_title']
        post_keywords = request.POST['keywords']
        post_audience = request.POST['audience']
        post_category = request.POST['category']
        post_type = request.POST['soc_post_type']
        max_char = request.POST['max_char']

        print('post_category: {}'.format(post_category))

        tone_of_voice = request.POST['tone_of_voice']
        api_call_code = str(uuid4()).split('-')[4]

        add_to_list = add_to_api_requests('generate_social_post', api_call_code, request.user.profile)

        n = 1
        # runs until n < 50,just to avoid the infinite loop.
        # this will execute the check_api_requests() func in every 5 seconds.
        while n < 50:
            # api_requests = check_api_requests()
            time.sleep(5)
            if api_call_process(api_call_code, add_to_list):
                # generate social post options
                social_post = generate_social_post(post_type, post_keywords, post_audience, tone_of_voice, post_title,
                                                   max_char, request.user.profile, False)

                # create database record
                new_post = SocialPost.objects.create(
                    title=post_title,
                    post_type=post_type,
                    tone_of_voice=tone_of_voice,
                    keywords=post_keywords,
                    audience=post_audience,
                    post=social_post,
                    category=post_category,
                )
                new_post.save()

                add_to_list.is_done = True
                add_to_list.save()

                context['new_post'] = new_post

                return redirect('view-social-media', post_type, new_post.uniqueId)

            else:
                # we might need to delete all abandoned calls
                pass
            n += 1


@login_required
def gen_social_post(request, postType, uniqueId=''):
    context = {}
    user_profile = request.user.profile
    current_page = 'Generate Social Post'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(user_profile)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    # post_type = postType.replace('_', ' ').title()
    prompt_text = ''

    sel_p_typ = SocialPlatform.objects.get(post_name=postType)
    max_char = sel_p_typ.max_char

    # if postType == "twitter":
    #     max_char = 280
    # elif postType == "instagram":
    #     max_char = 2200
    # elif postType == "linkedin":
    #     max_char = 3000
    # elif postType == "facebook":
    #     max_char = 10000
    # else:
    #     max_char = 280

    tone_of_voices = []

    cate_list = []
    client_list = []
    soc_types_list = []

    team_clients = TeamClient.objects.filter(is_active=True)
    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_profile.user_team)
    for category in team_categories:
        cate_list.append(category)

    soc_types = SocialPlatform.objects.filter(is_active=True)
    for soc_typ in soc_types:
        soc_types_list.append(soc_typ)
        print('soc_typ: {}'.format(soc_typ))

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    tones = ToneOfVoice.objects.filter(tone_status=True)

    for tone in tones:
        tone_of_voices.append(tone)

    context['tone_of_voices'] = tone_of_voices
    context['soc_types_list'] = soc_types_list

    print('soc_types_list: {}'.format(soc_types_list))

    context['post_type_title'] = sel_p_typ.post_name.title()
    context['post_type'] = sel_p_typ.post_name
    context['prompt_text'] = prompt_text

    if len(uniqueId) > 0:

        try:
            this_soc_post = SocialPost.objects.get(uniqueId=uniqueId)

            context['this_soc_post'] = this_soc_post
            context['post_type_title'] = this_soc_post.post_type
            context['post_type'] = this_soc_post.post_type
            context['prompt_text'] = this_soc_post.post_idea

            context['content_type'] = 'social_{}'.format(this_soc_post.post_type)
        except:
            pass

    # context['post_title'] = this_blog.title
    # context['post_audience'] = this_blog.audience
    # context['post_keywords'] = this_blog.keywords
    # context['post_tone'] = this_blog.tone_of_voice
    # context['category'] = this_blog.category

    if request.method == "POST":

        post_title = request.POST['post_title']
        soc_post_type = request.POST['soc_post_type']
        prompt_text = request.POST['prompt_text']
        post_keywords = request.POST['keywords']
        post_audience = request.POST['audience']
        category_id = request.POST['category']

        tone_of_voice = request.POST['tone_of_voice']
        api_call_code = str(uuid4()).split('-')[4]

        add_to_list = add_to_api_requests('generate_social_post', api_call_code, user_profile)

        n = 1
        # runs until n < 50,just to avoid the infinite loop.
        # this will execute the check_api_requests() func in every 5 seconds.
        while n < 50:
            # api_requests = check_api_requests()
            time.sleep(5)
            if api_call_process(api_call_code, add_to_list):
                # generate social post options
                social_post = generate_social_post(soc_post_type, post_keywords, post_audience, tone_of_voice,
                                                   prompt_text, max_char, user_profile, False)

                # create database record
                new_post = SocialPost.objects.create(
                    title=post_title,
                    post_type=soc_post_type,
                    tone_of_voice=tone_of_voice,
                    keywords=post_keywords,
                    audience=post_audience,
                    post_idea=prompt_text,
                    post=social_post,
                    profile=user_profile,
                    category=category_id,
                )
                new_post.save()

                add_to_list.is_done = True
                add_to_list.save()

                context['new_post'] = new_post

                return redirect('view-social-media', soc_post_type, new_post.uniqueId)

            else:
                # we might need to delete all abandoned calls
                pass
            n += 1

    return render(request, 'dashboard/social-media-post.html', context)


# @login_required
# def view_social_post(request, postType, uniqueId):
#     context = {}
#     user_profile = request.user.profile
#     current_page = 'View Blog Social Post'
#     context['current_page'] = current_page
#     context['allowance'] = check_count_allowance(user_profile)

#     lang = settings.LANGUAGE_CODE
#     flag_avatar = 'dash/images/gb_flag.jpg'

#     lang = check_user_lang(user_profile, lang)

#     if lang == 'en-us':
#         flag_avatar = 'dash/images/us_flag.jpg'

#     context['lang'] = lang
#     context['flag_avatar'] = flag_avatar

#     blog_posts = []
#     tone_of_voices = []

#     tones = ToneOfVoice.objects.filter(tone_status=True)

#     for tone in tones:
#         tone_of_voices.append(tone)

#     context['tone_of_voices'] = tone_of_voices


#     post_type = postType.replace('_', ' ').title()

#     context['post_type_title'] = post_type
#     context['post_type'] = postType
#     context['social_post'] = post
#     context['post_blog'] = post.blog
#     context['post_title'] = post.title
#     context['post_body'] = post.post
#     context['post_audience'] = post.audience
#     context['post_keywords'] = post.keywords
#     context['post_tone'] = post.tone_of_voice

#     return render(request, 'dashboard/social-media-post.html', context)


@login_required
def gen_social_from_blog(request, postType, uniqueId):
    context = {}
    user_profile = request.user.profile
    current_page = 'Generated Social Post From Blog'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(user_profile)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    try:
        this_blog = Blog.objects.get(uniqueId=uniqueId)
        created_post = True
    except:
        messages.error(request, "Something went wrong with your request, please try again!")
        return redirect('blog-topic')

    post_type = postType.replace('_', ' ').title()

    if postType == "twitter":
        max_char = 280
    elif postType == "instagram":
        max_char = 2200
    elif postType == "linkedin":
        max_char = 3000
    elif postType == "facebook":
        max_char = 10000
    else:
        max_char = 280

    blog_posts = []
    tone_of_voices = []

    tones = ToneOfVoice.objects.filter(tone_status=True)

    for tone in tones:
        tone_of_voices.append(tone)

    context['tone_of_voices'] = tone_of_voices

    blogs = Blog.objects.filter(profile=request.user.profile)

    for blog in blogs:
        sections = BlogSection.objects.filter(blog=blog)
        if sections.exists():
            blog_posts.append(blog)

    blog_sections = []

    context['blog_posts'] = blog_posts

    saved_blog = SavedBlogEdit.objects.get(blog=this_blog)

    if saved_blog:
        blog_body = saved_blog.body

    else:
        blog_sects = BlogSection.objects.filter(blog=this_blog)

        for blog_sect in blog_sects:
            blog_sections.append(blog_sect.body)

        blog_body = "\n".join(blog_sections)

        saved_blog = SavedBlogEdit.objects.create(
            title=this_blog.title,
            body=blog_body,
            blog=this_blog,
        )
        saved_blog.save()

    context['post_type_title'] = post_type
    context['post_type'] = postType
    context['post_blog'] = this_blog
    context['post_title'] = this_blog.title
    context['post_audience'] = this_blog.audience
    context['post_keywords'] = this_blog.keywords
    context['post_tone'] = this_blog.tone_of_voice

    if request.method == "POST":

        post_title = request.POST['post_title']
        post_keywords = request.POST['keywords']
        post_audience = request.POST['audience']

        tone_of_voice = request.POST['tone_of_voice']
        api_call_code = str(uuid4()).split('-')[4]

        add_to_list = add_to_api_requests('generate_social_post', api_call_code, request.user.profile)

        n = 1
        # runs until n < 50,just to avoid the infinite loop.
        # this will execute the check_api_requests() func in every 5 seconds.
        while n < 50:
            # api_requests = check_api_requests()
            time.sleep(5)
            if api_call_process(api_call_code, add_to_list):
                # generate social post options
                social_post = generate_social_post(post_type, post_keywords, post_audience, tone_of_voice, blog_body,
                                                   max_char, request.user.profile)

                # create database record
                new_post = BlogSocialPost.objects.create(
                    title=post_title,
                    post_type=postType,
                    tone_of_voice=tone_of_voice,
                    keywords=post_keywords,
                    audience=post_audience,
                    post=social_post,
                    blog=blog,
                )
                new_post.save()

                add_to_list.is_done = True
                add_to_list.save()

                context['new_post'] = new_post

                return redirect('view-blog-social', postType, new_post.uniqueId)

            else:
                # we might need to delete all abandoned calls
                pass
            n += 1

    return render(request, 'dashboard/blog-social-post.html', context)


@login_required
def delete_social_post(request, uniqueId):
    try:
        post = BlogSocialPost.objects.get(uniqueId=uniqueId)
        if post.blog.profile == request.user.profile:
            post.deleted = True
            post.save()
            messages.info(request, "Social media post deleted successfully!")
            return redirect('social-post-memory')
        else:
            messages.error(request, "Access denied!")
            return redirect('social-post-memory')
    except:
        messages.error(request, "Social media post not found!")
        return redirect('social-post-memory')


@login_required
def view_generated_blog(request, slug):
    context = {}
    user_profile = request.user.profile
    current_page = 'Blog Generator'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(user_profile)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    try:
        blog = Blog.objects.get(slug=slug)
    except:
        messages.error(request, "Something went wrong with your request, please try again!")
        return redirect('blog-topic')

    # fetch created blog sections
    blog_sects = BlogSection.objects.filter(blog=blog)

    context['blog'] = blog
    context['blog_sects'] = blog_sects

    return render(request, 'dashboard/view-generated-blog.html', context)


@login_required
def improve_content(request):
    context = {}
    min_words = 200
    max_words = 300
    user_profile = request.user.profile
    response_data = {}

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    if request.method == 'POST':
        content_topic = request.POST['content_title']
        old_content = request.POST['content_body_old']
        content_cate = request.POST['content_category']
        content_keywords = request.POST['keywords']
        max_words = int(request.POST['max_words'])

        response_data = {
            'content_topic': content_topic,
            'old_content': old_content,
            'content_cate': content_cate,
            'content_keywords': content_keywords,
            'max_words': max_words

        }

        if len(content_topic) > 300 and max_words > 14000:
            messages.error(request, "The engine could not generate content from the given prompt, please try again!")
            return redirect('content-improver')
        else:
            tone_of_voice = request.POST['tone_of_voice']
            if len(old_content) > 3 and len(old_content) < 14001:
                # generator starts here
                api_call_code = str(uuid4()).split('-')[4]

                # api_requests = check_api_requests()

                add_to_list = add_to_api_requests('gen_improve_content', api_call_code, request.user.profile)

                n = 1
                # runs until n < 50,just to avoid the infinite loop.
                # this will execute the check_api_requests() func in every 5 seconds.
                while n < 50:
                    # api_requests = check_api_requests()
                    time.sleep(5)
                    if api_call_process(api_call_code, add_to_list):

                        gen_content = gen_improve_content(old_content, min_words, max_words, content_keywords,
                                                          tone_of_voice, request.user.profile)

                        if len(gen_content) > 0:

                            # create database record
                            s_content = ContentImprover.objects.create(
                                content_title=content_topic,
                                tone_of_voice=tone_of_voice,
                                content_body_old=old_content,
                                content_keywords=content_keywords,
                                content_body_new=gen_content,
                                profile=request.user.profile,
                                category=content_cate,
                            )
                            s_content.save()

                            add_to_list.is_done = True
                            add_to_list.save()

                            context['content_uniqueId'] = s_content.uniqueId

                            response_data = {
                                'result': 'success',
                                'message': 'Content successfully generated',
                                'contentId': s_content.uniqueId,
                                'contentBody': s_content.content_body_new,
                            }
                            break

                        else:
                            response_data = {
                                'result': 'error',
                                'message': 'API response not found, please try again'
                            }
                            break

                    else:
                        # we might need to delete all abandoned calls
                        pass
                    n += 1
            else:
                response_data = {
                    'result': 'error',
                    'message': 'Content body is supposed to be between 100 and 2000 chars long!'
                }

    else:
        response_data = {
            'result': 'error',
            'message': 'Something went terribly wrong here'
        }

    return JsonResponse(response_data, content_type="application/json", safe=False)


@login_required
def delete_impr_content(request, uniqueId):
    try:
        content = ContentImprover.objects.get(uniqueId=uniqueId)

        if content.profile == request.user.profile:
            content.deleted = True
            content.save()

            messages.info(request, "Item deleted successfully!")
            return redirect('content-improver-memory')
        else:
            messages.error(request, "Access denied!")
            return redirect('content-improver-memory')
    except:
        messages.error(request, "Item not found!")
        return redirect('content-improver-memory')


@login_required
def content_improver(request, uniqueId=''):
    context = {}
    user_profile = request.user.profile
    tone_of_voices = []
    current_page = 'Content Improver'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(user_profile)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    cate_list = []
    client_list = []

    team_clients = TeamClient.objects.filter(is_active=True)
    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_profile.user_team)
    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    tones = ToneOfVoice.objects.filter(tone_status=True)
    for tone in tones:
        tone_of_voices.append(tone)

    context['tone_of_voices'] = tone_of_voices

    if len(uniqueId) > 0:
        # search database for paragraph with this slug
        content = ContentImprover.objects.get(uniqueId=uniqueId)

        context['content'] = content
        context['content_body_new'] = content.content_body_new.replace('<br>', '\n')
    else:
        pass

    return render(request, 'dashboard/content-improver.html', context)


@login_required
def paragraph_writer(request, uniqueId=''):
    context = {}
    user_profile = request.user.profile
    tone_of_voices = []
    current_page = 'Paragraph Writer'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(user_profile)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    cate_list = []
    client_list = []
    user_profile = request.user.profile
    team_clients = TeamClient.objects.filter(is_active=True)

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_profile.user_team)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    tones = ToneOfVoice.objects.filter(tone_status=True)

    for tone in tones:
        tone_of_voices.append(tone)

    context['tone_of_voices'] = tone_of_voices

    if len(uniqueId) > 0:
        # search database for paragraph with this slug
        paragraph = Paragraph.objects.get(uniqueId=uniqueId)

        context['paragraph'] = paragraph
    else:
        pass

    if request.method == 'POST':
        paragraph_topic = request.POST['paragraph_topic']
        request.session['paragraph_topic'] = paragraph_topic

        paragraph_cate = request.POST['category']

        if len(paragraph_topic) > 300:
            messages.error(request, "The engine could not generate content from the given prompt, please try again!")
            return redirect('paragraph-writer')
        else:

            tone_of_voice = request.POST['tone_of_voice']
            request.session['tone_of_voice'] = tone_of_voice

            api_call_code = str(uuid4()).split('-')[4]

            # api_requests = check_api_requests()

            add_to_list = add_to_api_requests('generate_paragraph', api_call_code, request.user.profile)

            n = 1
            # runs until n < 50,just to avoid the infinite loop.
            # this will execute the check_api_requests() func in every 5 seconds.
            while n < 50:
                # api_requests = check_api_requests()
                time.sleep(5)
                if api_call_process(api_call_code, add_to_list):

                    gen_paragraph = generate_paragraph(paragraph_topic, tone_of_voice, request.user.profile)

                    if len(gen_paragraph) > 0:

                        # create database record
                        s_paragraph = Paragraph.objects.create(
                            paragraph_topic=paragraph_topic,
                            tone_of_voice=tone_of_voice,
                            paragraph=gen_paragraph,
                            profile=request.user.profile,
                            category=paragraph_cate
                        )
                        s_paragraph.save()

                        add_to_list.is_done = True
                        add_to_list.save()

                        context['paragraph_uniqueId'] = s_paragraph.uniqueId

                        return redirect('paragraph-writer-response', uniqueId=s_paragraph.uniqueId)

                    else:
                        messages.error(request, "The engine could not understand your command, please try again!")
                        return redirect('paragraph-writer')

                else:
                    # we might need to delete all abandoned calls
                    pass
                n += 1

    return render(request, 'dashboard/paragraph-writer.html', context)


@login_required
def delete_paragraph(request, uniqueId):
    try:
        content = Paragraph.objects.get(uniqueId=uniqueId)

        if content.profile == request.user.profile:
            content.deleted = True
            content.save()

            messages.info(request, "Item deleted successfully!")
            return redirect('paragraph-memory')
        else:
            messages.error(request, "Access denied!")
            return redirect('paragraph-memory')
    except:
        messages.error(request, "Item not found!")
        return redirect('paragraph-memory')


@login_required
def sentence_writer(request, uniqueId=''):
    context = {}
    user_profile = request.user.profile
    tone_of_voices = []
    current_page = 'Sentence Writer'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(user_profile)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    cate_list = []
    client_list = []

    user_profile = request.user.profile

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_profile.user_team)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    tones = ToneOfVoice.objects.filter(tone_status=True)

    for tone in tones:
        tone_of_voices.append(tone)

    context['tone_of_voices'] = tone_of_voices

    if len(uniqueId) > 0:
        sentence_opts = []
        # search database for sentences with this slug
        sentence_obj = Sentence.objects.get(uniqueId=uniqueId)

        new_sentences = sentence_obj.new_sentence

        a_list = new_sentences.split('<br>')
        if len(a_list) > 0:
            for sentence in a_list:
                sentence_opts.append(sentence)
        else:
            return []

        if len(sentence) > 0:
            context['sentences'] = sentence_opts
            context['old_sentence'] = sentence_obj.old_sentence
            context['tone_of_voice'] = sentence_obj.tone_of_voice
            context['sentence_uniqueId'] = sentence_obj.uniqueId
            context['sentence_cate'] = sentence_obj.category

            context['sentence_obj'] = sentence_obj
    else:
        pass

    if request.method == 'POST':
        old_sentence = request.POST['old_sentence']
        tone_of_voice = request.POST['tone_of_voice']
        sentnc_cate = request.POST['category']

        if len(old_sentence) > 160:
            messages.error(request, "The engine could not generate content from the given prompt, please try again!")
            return redirect('sentence-writer')
        else:

            api_call_code = str(uuid4()).split('-')[4]

            add_to_list = add_to_api_requests('rewrite_sentence', api_call_code, request.user.profile)

            n = 1
            # runs until n < 50,just to avoid the infinite loop.
            # this will execute the check_api_requests() func in every 5 seconds.
            while n < 50:
                # api_requests = check_api_requests()
                time.sleep(5)
                if api_call_process(api_call_code, add_to_list):

                    new_sentences = rewrite_sentence(old_sentence, tone_of_voice, request.user.profile)

                    if len(new_sentences) > 0:

                        # create database record
                        s_sentence = Sentence.objects.create(
                            old_sentence=old_sentence,
                            new_sentence=new_sentences,
                            tone_of_voice=tone_of_voice,
                            profile=request.user.profile,
                            category=sentnc_cate
                        )
                        s_sentence.save()

                        add_to_list.is_done = True
                        add_to_list.save()

                        context['sentence_slug'] = s_sentence.uniqueId

                        return redirect('sentence-writer-response', uniqueId=s_sentence.uniqueId)

                    else:
                        messages.error(request, "The engine could not understand your command, please try again!")
                        return redirect('sentence-writer')

                else:
                    # we might need to delete all abandoned calls
                    pass
                n += 1

    return render(request, 'dashboard/sentence-writer.html', context)


@login_required
def delete_sentence(request, uniqueId):
    context = {}

    try:
        sentence = Sentence.objects.get(uniqueId=uniqueId)

        if sentence.profile == request.user.profile:
            sentence.deleted = True
            sentence.save()

            messages.info(request, "Sentence deleted successfully!")
            return redirect('sentence-memory')
        else:
            messages.error(request, "Access denied!")
            return redirect('sentence-memory')
    except:
        messages.error(request, "Sentence not found!")
        return redirect('sentence-memory')


@login_required
def article_title_writer(request, uniqueId=''):
    context = {}
    user_profile = request.user.profile
    tone_of_voices = []
    current_page = 'Title Writer'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(user_profile)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    cate_list = []
    client_list = []

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_profile.user_team)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list
    tones = ToneOfVoice.objects.filter(tone_status=True)

    for tone in tones:
        tone_of_voices.append(tone)

    context['tone_of_voices'] = tone_of_voices

    if len(uniqueId) > 0:
        title_opts = []
        # search database for titles with this slug
        title_obj = ArticleTitle.objects.get(uniqueId=uniqueId)

        new_titles = title_obj.new_title_options

        a_list = new_titles.split('<br>')
        if len(a_list) > 0:
            for title in a_list:
                title_opts.append(title)
        else:
            return []

        if len(title) > 0:
            context['title_opts'] = title_opts
            context['old_title'] = title_obj.old_title
            context['tone_of_voice'] = title_obj.tone_of_voice
            context['title_uniqueId'] = title_obj.uniqueId
            context['title_cate'] = title_obj.category

        # context['paragraph'] = title
    else:
        pass

    if request.method == 'POST':
        old_title = request.POST['old_title']
        tone_of_voice = request.POST['tone_of_voice']
        title_cate = request.POST['category']
        # request.session['old_title'] = old_title

        if len(old_title) > 160:
            messages.error(request, "The engine could not generate content from the given prompt, please try again!")
            return redirect('title-writer')
        else:
            api_call_code = str(uuid4()).split('-')[4]

            add_to_list = add_to_api_requests('rewriter_article_title', api_call_code, request.user.profile)

            n = 1
            # runs until n < 50,just to avoid the infinite loop.
            # this will execute the check_api_requests() func in every 5 seconds.
            while n < 50:
                # api_requests = check_api_requests()
                time.sleep(5)
                if api_call_process(api_call_code, add_to_list):

                    new_titles = rewriter_article_title(old_title, tone_of_voice, request.user.profile)

                    if len(new_titles) > 0:

                        # create database record
                        s_title = ArticleTitle.objects.create(
                            old_title=old_title,
                            tone_of_voice=tone_of_voice,
                            new_title_options=new_titles,
                            profile=request.user.profile,
                            category=title_cate,
                        )
                        s_title.save()

                        add_to_list.is_done = True
                        add_to_list.save()

                        context['title_slug'] = s_title.uniqueId

                        return redirect('title-writer-response', uniqueId=s_title.uniqueId)

                    else:
                        messages.error(request, "The engine could not understand your command, please try again!")
                        return redirect('title-writer')

                else:
                    # we might need to delete all abandoned calls
                    pass
                n += 1

    return render(request, 'dashboard/title-rewriter.html', context)


@login_required
def delete_title(request, uniqueId):
    try:
        title = ArticleTitle.objects.get(uniqueId=uniqueId)

        if title.profile == request.user.profile:
            title.deleted = True
            title.save()

            messages.info(request, "Title deleted successfully!")
            return redirect('title-memory')
        else:
            messages.error(request, "Access denied!")
            return redirect('title-memory')
    except:
        messages.error(request, "Title not found!")
        return redirect('title-memory')


@login_required
def generate_blog_meta(request, uniqueId):
    context = {}
    user_profile = request.user.profile
    tone_of_voices = []
    current_page = 'Meta Description Generator'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(user_profile)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    blog_posts = []

    cate_list = []
    client_list = []

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_profile.user_team)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    tones = ToneOfVoice.objects.filter(tone_status=True)

    for tone in tones:
        tone_of_voices.append(tone)

    context['tone_of_voices'] = tone_of_voices

    try:
        this_blog = Blog.objects.get(uniqueId=uniqueId)

    except:
        messages.error(request, "Blog not found!")
        return redirect('blog-memory')

    blogs = Blog.objects.filter(profile=user_profile)

    for blog in blogs:
        sections = BlogSection.objects.filter(blog=blog)
        if sections.exists():
            blog_posts.append(blog)

    blog_sections = []

    context['blog_posts'] = blog_posts

    context['post_blog'] = this_blog
    context['article_title'] = this_blog.title
    context['this_blog_cate'] = this_blog.category
    context['tone_of_voice'] = this_blog.tone_of_voice

    if request.method == 'POST':
        article_title = request.POST['article_title']
        tone_of_voice = request.POST['tone_of_voice']
        meta_category = request.POST['category']
        request.session['article_title'] = article_title

        if len(article_title) > 160:
            messages.error(request, "The engine could not generate content for your prompt, please try again!")
            return redirect('meta-description-generator')
        else:

            api_call_code = str(uuid4()).split('-')[4]

            add_to_list = add_to_api_requests('generate_meta_description', api_call_code, request.user.profile)

            n = 1
            # runs until n < 50,just to avoid the infinite loop.
            # this will execute the check_api_requests() func in every 5 seconds.
            while n < 50:
                # api_requests = check_api_requests()
                time.sleep(5)
                if api_call_process(api_call_code, add_to_list):

                    gen_meta_descr = generate_meta_description(article_title, tone_of_voice, request.user.profile)

                    if len(gen_meta_descr) > 0:

                        # create database record
                        s_meta_descr = MetaDescription.objects.create(
                            article_title=article_title,
                            tone_of_voice=tone_of_voice,
                            meta_description=gen_meta_descr,
                            profile=request.user.profile,
                            category=meta_category,
                            blog_id=uniqueId,
                        )
                        s_meta_descr.save()

                        add_to_list.is_done = True
                        add_to_list.save()

                        context['meta_descr_uniqueId'] = s_meta_descr.uniqueId

                        return redirect('meta-description-generator-response', s_meta_descr.uniqueId)

                    else:
                        messages.error(request, "The engine could not understand your command, please try again!")
                        return redirect('generate-blog-meta', uniqueId)
                else:
                    # we might need to delete all abandoned calls
                    pass
                n += 1

    return render(request, 'dashboard/meta-description-generator.html', context)


@login_required
def meta_description_writer(request, uniqueId=''):
    context = {}
    user_profile = request.user.profile
    tone_of_voices = []
    current_page = 'Meta Description Generator'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(user_profile)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    cate_list = []
    client_list = []

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_profile.user_team)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    tones = ToneOfVoice.objects.filter(tone_status=True)

    for tone in tones:
        tone_of_voices.append(tone)

    context['tone_of_voices'] = tone_of_voices

    if len(uniqueId) > 0:
        # search database for meta descriptions with this slug
        meta_descr = MetaDescription.objects.get(uniqueId=uniqueId)

        context['meta_descr'] = meta_descr
        context['article_title'] = meta_descr.article_title
        context['category'] = meta_descr.category
        context['tone_of_voice'] = meta_descr.tone_of_voice
        context['meta_description'] = meta_descr.meta_description
    else:
        pass

    if request.method == 'POST':
        article_title = request.POST['article_title']
        tone_of_voice = request.POST['tone_of_voice']
        meta_category = request.POST['category']
        request.session['article_title'] = article_title

        if len(article_title) > 160:
            messages.error(request, "The engine could not generate content for your prompt, please try again!")
            return redirect('meta-description-generator')
        else:

            api_call_code = str(uuid4()).split('-')[4]

            add_to_list = add_to_api_requests('generate_meta_description', api_call_code, request.user.profile)

            n = 1
            # runs until n < 50,just to avoid the infinite loop.
            # this will execute the check_api_requests() func in every 5 seconds.
            while n < 50:
                # api_requests = check_api_requests()
                time.sleep(5)
                if api_call_process(api_call_code, add_to_list):

                    gen_meta_descr = generate_meta_description(article_title, tone_of_voice, request.user.profile)

                    if len(gen_meta_descr) > 0:

                        # create database record
                        s_meta_descr = MetaDescription.objects.create(
                            article_title=article_title,
                            tone_of_voice=tone_of_voice,
                            meta_description=gen_meta_descr,
                            profile=request.user.profile,
                            category=meta_category,
                        )
                        s_meta_descr.save()

                        add_to_list.is_done = True
                        add_to_list.save()

                        context['meta_descr_uniqueId'] = s_meta_descr.uniqueId

                        return redirect('meta-description-generator-response', uniqueId=s_meta_descr.uniqueId)

                    else:
                        messages.error(request, "The engine could not understand your command, please try again!")
                        return redirect('meta-description-generator')
                else:
                    # we might need to delete all abandoned calls
                    pass
                n += 1

    return render(request, 'dashboard/meta-description-generator.html', context)


@login_required
def delete_meta_descr(request, uniqueId):
    try:
        meta_descr = MetaDescription.objects.get(uniqueId=uniqueId)

        if meta_descr.profile == request.user.profile:
            meta_descr.deleted = True
            meta_descr.save()

            messages.info(request, "Item deleted successfully!")
            return redirect('meta-descr-memory')
        else:
            messages.error(request, "Access denied!")
            return redirect('meta-descr-memory')
    except:
        messages.error(request, "Item not found!")
        return redirect('meta-descr-memory')


@login_required
def summarize_blog(request, blogUniqueId, uniqueId=''):
    context = {}
    user_profile = request.user.profile
    tone_of_voices = []
    current_page = 'Content Summariser'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(user_profile)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
    # print(check_device_reg)
    # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    cate_list = []
    client_list = []
    blog_posts = []
    this_blog_sections = []
    blog_body = ''
    blog_sections = []

    team_clients = TeamClient.objects.filter(is_active=True)

    try:
        this_blog = Blog.objects.get(uniqueId=blogUniqueId)
        blog_title = this_blog.title

    except:
        messages.error(request, "Blog not found!")
        return redirect('blog-memory', 'incomplete')

    try:
        saved_blog_sects = SavedBlogEdit.objects.filter(blog=this_blog)
        if saved_blog_sects.exists():
            for blog_sect in saved_blog_sects:
                blog_title = blog_sect.title

                this_blog_sections.append(blog_sect.body)
        else:
            saved_blog = SavedBlogEdit.objects.create(
                title=this_blog.title,
                body=blog_body_sect,
                blog=this_blog,
            )
            saved_blog.save()
            this_blog_sections.append(saved_blog.body)

    except:
        gen_sections = BlogSection.objects.filter(blog=this_blog)
        for blog_sect in gen_sections:
            this_blog_body = blog_sect.body
            blog_sections.append(this_blog_body)

        blog_body_sect = "\n".join(blog_sections).replace('<br>', '\n')

        saved_blog = SavedBlogEdit.objects.create(
            title=this_blog.title,
            body=blog_body_sect,
            blog=this_blog,
        )
        saved_blog.save()
        this_blog_sections.append(saved_blog.body)

    blogs = Blog.objects.filter(profile=user_profile)
    for blog in blogs:
        sections = BlogSection.objects.filter(blog=blog)
        if sections.exists():
            blog_posts.append(blog)

    # blog_body = "\n".join(this_blog_sections).replace('<br>', '\n')
    blog_body = "\n".join(this_blog_sections)

    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_profile.user_team)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    tones = ToneOfVoice.objects.filter(tone_status=True)

    for tone in tones:
        tone_of_voices.append(tone)

    context['blog_posts'] = blog_posts
    context['tone_of_voices'] = tone_of_voices

    context['post_blog'] = this_blog
    context['summary_title'] = this_blog.title
    context['this_summary_cate'] = this_blog.category
    context['tone_of_voice'] = this_blog.tone_of_voice

    context['long_content'] = blog_body

    if len(uniqueId) > 0:
        # search database for meta descriptions with this slug
        content_summary = ContentSummary.objects.get(uniqueId=uniqueId)

        context['content_summary'] = content_summary
        context['summary_title'] = content_summary.summary_title
        context['this_summary_cate'] = content_summary.category
        context['tone_of_voice'] = content_summary.tone_of_voice
        context['long_content'] = content_summary.long_content
        context['summarized_content'] = content_summary.summarized
    else:
        pass

    if request.method == 'POST':
        long_content = request.POST['long_content']
        summary_title = request.POST['summary_title']
        tone_of_voice = request.POST['tone_of_voice']
        summary_cate = request.POST['category']
        request.session['long_content'] = long_content

        if len(long_content) > 14000:
            messages.error(request, "The engine could not generate content for your prompt, please try again!")
            return redirect('meta-description-generator')
        else:

            api_call_code = str(uuid4()).split('-')[4]

            add_to_list = add_to_api_requests('write_content_summary', api_call_code, request.user.profile)

            n = 1
            # runs until n < 50,just to avoid the infinite loop.
            # this will execute the check_api_requests() func in every 5 seconds.
            while n < 50:
                # api_requests = check_api_requests()
                time.sleep(5)
                if api_call_process(api_call_code, add_to_list):

                    content_summary = write_content_summary(long_content, tone_of_voice, request.user.profile)

                    if len(content_summary) > 0:

                        # create database record
                        s_content_data = ContentSummary.objects.create(
                            long_content=long_content,
                            summary_title=summary_title,
                            tone_of_voice=tone_of_voice,
                            summarized=content_summary,
                            profile=request.user.profile,
                            category=summary_cate,
                            blog_id=blogUniqueId,
                        )
                        s_content_data.save()

                        add_to_list.is_done = True
                        add_to_list.save()

                        context['content_data_uniqueId'] = s_content_data.uniqueId

                        return redirect('blog-summarizer-response', blogUniqueId, s_content_data.uniqueId)

                    else:
                        messages.error(request, "The engine could not understand your command, please try again!")
                        return redirect('generate-blog-summary', blogUniqueId)
                else:
                    # we might need to delete all abandoned calls
                    pass
                n += 1

    return render(request, 'dashboard/content-summarizer.html', context)


@login_required
def summarize_content(request, uniqueId=""):
    context = {}
    user_profile = request.user.profile
    tone_of_voices = []
    current_page = 'Content Summariser'
    context['current_page'] = current_page
    context['allowance'] = check_count_allowance(user_profile)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    cate_list = []
    client_list = []

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_profile.user_team)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    tones = ToneOfVoice.objects.filter(tone_status=True)

    for tone in tones:
        tone_of_voices.append(tone)

    context['tone_of_voices'] = tone_of_voices

    if len(uniqueId) > 0:
        # search database for meta descriptions with this slug
        content_summary = ContentSummary.objects.get(uniqueId=uniqueId)

        context['content_summary'] = content_summary
        context['summary_title'] = content_summary.summary_title
        context['this_summary_cate'] = content_summary.category
        context['tone_of_voice'] = content_summary.tone_of_voice
        context['long_content'] = content_summary.long_content
        context['summarized_content'] = content_summary.summarized

    else:
        pass

    if request.method == 'POST':
        long_content = request.POST['long_content']
        summary_title = request.POST['summary_title']
        tone_of_voice = request.POST['tone_of_voice']
        summary_cate = request.POST['category']
        request.session['long_content'] = long_content

        if len(long_content) > 14000:
            messages.error(request, "The engine could not generate content for your prompt, please try again!")
            return redirect('meta-description-generator')
        else:

            api_call_code = str(uuid4()).split('-')[4]

            add_to_list = add_to_api_requests('write_content_summary', api_call_code, request.user.profile)

            n = 1
            # runs until n < 50,just to avoid the infinite loop.
            # this will execute the check_api_requests() func in every 5 seconds.
            while n < 50:
                # api_requests = check_api_requests()
                time.sleep(5)
                if api_call_process(api_call_code, add_to_list):

                    content_summary = write_content_summary(long_content, tone_of_voice, request.user.profile)

                    if len(content_summary) > 0:

                        # create database record
                        s_content_data = ContentSummary.objects.create(
                            long_content=long_content,
                            summary_title=summary_title,
                            tone_of_voice=tone_of_voice,
                            summarized=content_summary,
                            profile=request.user.profile,
                            category=summary_cate,
                        )
                        s_content_data.save()

                        add_to_list.is_done = True
                        add_to_list.save()

                        context['content_data_uniqueId'] = s_content_data.uniqueId

                        return redirect('content-summarizer-response', uniqueId=s_content_data.uniqueId)

                    else:
                        messages.error(request, "The engine could not understand your command, please try again!")
                        return redirect('content-summarizer')
                else:
                    # we might need to delete all abandoned calls
                    pass
                n += 1

    return render(request, 'dashboard/content-summarizer.html', context)


@login_required
def delete_summary(request, uniqueId):
    try:
        content = ContentSummary.objects.get(uniqueId=uniqueId)
        if content.profile == request.user.profile:
            content.deleted = True
            content.save()

            messages.info(request, "Item deleted successfully!")
            return redirect('summarizer-memory')
        else:
            messages.error(request, "Access denied!")
            return redirect('summarizer-memory')
    except:
        messages.error(request, "Item not found!")
        return redirect('summarizer-memory')


@login_required
def landing_page_copy(request, uniqueId=""):
    context = {}

    user_profile = request.user.profile
    current_page = 'Landing Page Copy Generator'
    context['current_page'] = current_page
    page_sections = "Header, Subheader, About Us, Call to Action, FAQ, Testimonials"
    context['allowance'] = check_count_allowance(user_profile)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    remote_addr = get_client_ip(request)
    max_devices_allow = max_devices(user_profile)
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # redirect user out and give solution to remove device
        messages.error(request,
                       "You have maximum devices logged in on your profile, please delete one to be able to use current device or upgrade!")
        return redirect('device-manager')
        # print(check_device_reg)
        # pass
    else:
        profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
        profile.current_device = device_reg
        profile.current_ip = remote_addr
        profile.save()

    cate_list = []
    client_list = []

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_profile.user_team)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    context['page_sections'] = page_sections

    if len(uniqueId) > 0:
        # search database for landing copy
        copy_content = LandingPageCopy.objects.get(uniqueId=uniqueId)
        copy_content.page_copy = copy_content.page_copy.replace('\n', '<br>')
        copy_content.save()

        context['copy_content'] = copy_content
        context['page_sections'] = copy_content.page_sections
    else:
        pass

    if request.method == 'POST':
        company_name = request.POST['company_name']
        copy_title = request.POST['copy_title']
        copy_category = request.POST['category']
        # request.session['company_name'] = company_name

        company_purpose = request.POST['company_purpose']
        page_sections = request.POST['page_sections']
        # request.session['company_purpose'] = company_purpose

        if len(company_name) > 200 or len(company_purpose) > 200:
            messages.error(request, "The engine could not understand your command, please try again!")
            return redirect('landing-page-copy')
        else:

            api_call_code = str(uuid4()).split('-')[4]

            add_to_list = add_to_api_requests('generate_landing_page_copy', api_call_code, request.user.profile)

            n = 1
            # runs until n < 50,just to avoid the infinite loop.
            # this will execute the check_api_requests() func in every 5 seconds.
            while n < 50:
                # api_requests = check_api_requests()
                time.sleep(5)
                if api_call_process(api_call_code, add_to_list):

                    gen_page_copy = generate_landing_page_copy(company_name, company_purpose, page_sections,
                                                               request.user.profile)

                    if len(gen_page_copy) > 0:

                        # create database record
                        s_content_data = LandingPageCopy.objects.create(
                            company_name=company_name,
                            company_purpose=company_purpose,
                            copy_title=copy_title,
                            page_sections=page_sections,
                            page_copy=gen_page_copy,
                            profile=request.user.profile,
                            category=copy_category,
                        )
                        s_content_data.save()

                        add_to_list.is_done = True
                        add_to_list.save()

                        context['content_data_uniqueId'] = s_content_data.uniqueId

                        return redirect('landing-page-copy-response', uniqueId=s_content_data.uniqueId)

                    else:
                        messages.error(request, "The engine could not understand your command, please try again!")
                        return redirect('landing-page-copy')
                else:
                    # we might need to delete all abandoned calls
                    pass
                n += 1

    return render(request, 'dashboard/landing-page-copy.html', context)


@login_required
def delete_page_copy(request, uniqueId):
    try:
        content = LandingPageCopy.objects.get(uniqueId=uniqueId)

        if content.profile == request.user.profile:
            content.deleted = True
            content.save()

            messages.info(request, "Item deleted successfully!")
            return redirect('page-copy-memory')
        else:
            messages.error(request, "Access denied!")
            return redirect('page-copy-memory')
    except:
        messages.error(request, "Item not found!")
        return redirect('page-copy-memory')


@login_required
def transactions(request):
    context = {}
    transactions = []
    user_profile = request.user.profile

    current_page = 'Transactions'

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    # user_sub_type = user_profile.subscription_type.title()

    # # get user current tier
    # user_curr_tier = SubscriptionPackage.objects.get(package_name=user_sub_type)

    # get packages
    subscr_transactions = SubscriptionTransaction.objects.filter(is_active=True, user_profile_uid=user_profile.uniqueId).order_by('date_created')

    for subscr_transact in subscr_transactions:
        transactions.append(subscr_transact)

    context['current_page'] = current_page
    context['transactions'] = transactions
    return render(request, 'dashboard/transactions.html', context)


@login_required
def view_transaction(request, uniqueId):
    context = {}
    transactions = []
    user_profile = request.user.profile

    current_page = 'View Transaction'

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(request.user.profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    # user_sub_type = request.user.profile.subscription_type.title()

    # # get user current tier
    # user_curr_tier = SubscriptionPackage.objects.get(package_name=user_sub_type)

    # get packages
    subscr_transactions = SubscriptionTransaction.objects.filter(is_active=True, user_profile_uid=user_profile.uniqueId).order_by('date_created')

    for subscr_transact in subscr_transactions:
        transactions.append(subscr_transact)

    context['current_page'] = current_page
    context['transactions'] = transactions
    return render(request, 'dashboard/transactions.html', context)


@login_required
def billing(request):
    context = {}
    packages = []

    current_page = 'Billing'

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(request.user.profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    user_sub_type = request.user.profile.subscription_type.title()

    # get user current tier
    user_curr_tier = SubscriptionPackage.objects.get(package_name=user_sub_type)

    # get packages
    packs = SubscriptionPackage.objects.filter(is_active=True).order_by('date_created')

    for pack in packs:
        packages.append(pack)

    context['current_page'] = current_page
    context['month_word_count'] = request.user.profile.monthly_count
    context['user_curr_tier'] = user_curr_tier
    context['sub_packages'] = packages

    return render(request, 'dashboard/billing.html', context)


def get_single_plan(request, uniqueId, planId):
    response_data = {}

    # validate member
    try:
        user_profile = Profile.objects.get(uniqueId=uniqueId)
        subplan = SubscriptionPackage.objects.get(uniqueId=planId)

        response_data = {
            'result': 'success',
            'message': 'plan found successfully',
            'user_team': user_profile.user_team,
            'plan_amount': subplan.package_price,
            'package_name': subplan.package_name,
            'max_word': subplan.package_max_word
        }

    except:
        response_data = {
            'result': 'error',
            'message': 'Some error message'
        }

    # return JsonResponse(response_data)
    return JsonResponse(json.dumps(response_data), content_type="application/json", safe=False)


@login_required
def payment_plans(request):
    context = {}

    current_page = 'Payment Plans'
    context['current_page'] = current_page

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(request.user.profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    return render(request, 'dashboard/process-initiator-plan.html', context)


@login_required
def payfast_payment(request, planId):
    user_profile = request.user.profile
    context = {}

    protocol = 'https' if request.is_secure() else 'http'

    merchant_id = settings.PAYFAST_MERCHANT_ID
    merchant_key = settings.PAYFAST_MERCHANT_KEY
    return_url = '{}/success'.format(settings.PAYFAST_URL_BASE)
    notify_url = '{}/notify'.format(settings.PAYFAST_URL_BASE)
    # cancel_url = '{}/cancel'.format(settings.PAYFAST_URL_BASE)
    cancel_url = '{}://{}/dash/billing'.format(protocol, get_current_site(request).domain)

    order_id = str(uuid4()).split('-')[4]

    package = SubscriptionPackage.objects.get(uniqueId=planId)

    recurring_amount = package.package_price
    amount = "%.2f" % int(recurring_amount)
    item_name = "{} {}".format(settings.APP_NAME, package.package_name)
    item_descr = "{} Package".format(package.package_name)

    m_payment_id = '{}-{}-{}'.format(user_profile.uniqueId, planId, order_id)

    current_page = 'Billing | {}'.format(item_name)
    context['current_page'] = current_page

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    if request.user.first_name is None or request.user.last_name is None:
        messages.error(request, 'Your profile is not complete, please fill in your details to contiue!')
        redirect('profile')

    subscri_frequency = "3"
    sub_period = 'month'
    if 'Yearly' in package.package_name:
        subscri_frequency = "6"
        recurring_amount = str(int(recurring_amount) * 12)
        amount = "%.2f" % int(recurring_amount)
        sub_period = 'Year'

    ws_user_fname = request.user.first_name
    ws_user_lname = request.user.last_name

    pfData = {
        "merchant_id": merchant_id,
        "merchant_key": merchant_key,
        "return_url": return_url,
        "cancel_url": cancel_url,
        "notify_url": notify_url,
        # # Buyer details
        "name_first": ws_user_fname,
        "name_last": ws_user_lname,
        "email_address": request.user.email,
        "m_payment_id": m_payment_id,
        "amount": amount,
        "item_name": item_name,
        "item_description": item_descr,
        # # Subscription details
        "subscription_type": "1",
        # "billing_date": "",
        "recurring_amount": recurring_amount,
        "frequency": subscri_frequency,
        "cycles": "0",
        # "custom_str1": user_profile.uniqueId,
        # "custom_str2": planId
    }

    def generateSignature(dataArray, passPhrase=''):
        payload = ""
        for key in dataArray:
            # Get all the data from Payfast and prepare parameter string
            payload += key + "=" + urllib.parse.quote_plus(dataArray[key].replace("+", " ")) + "&"
        # After looping through, cut the last & or append your passphrase
        payload = payload[:-1]
        if passPhrase != '':
            payload += f"&passphrase={passPhrase}"
        return hashlib.md5(payload.encode()).hexdigest()

    passPhrase = settings.PAYFAST_PASS_PHRASE
    signature = generateSignature(pfData, passPhrase)

    # Generate signature (see step 2)
    # passphase = 'jt7NOE43FZPn';
    # signature = generateSignature(pfData, passPhrase)
    # pfData['signature'] = signature

    context['signature'] = signature

    # context['user_id'] = user_profile.uniqueId
    context['m_payment_id'] = m_payment_id
    context['merchant_id'] = merchant_id
    context['merchant_key'] = merchant_key
    context['return_url'] = return_url
    context['cancel_url'] = cancel_url
    context['notify_url'] = notify_url
    context['amount'] = amount
    context['recurring_amount'] = recurring_amount
    context['subscri_frequency'] = subscri_frequency
    context['item_name'] = item_name
    context['item_descr'] = item_descr
    context['sub_period'] = sub_period
    # context['plan_id'] = planId
    context[
        'action_url'] = 'https://sandbox.payfast.co.za/eng/process' if settings.PAYFAST_SANDBOX_MODE else 'https://www.payfast.co.za/eng/process'

    return render(request, 'dashboard/process-plan-payment.html', context)


@require_POST
@csrf_exempt
def webhook(request):
    # verify that the request is from PayPal

    # check the type of webhook event
    # 1. subscription created
    # 2. subscription got cancelled

    # process the event
    return redirect('billing')


@login_required
def payment_cancel(request):
    return redirect('billing')


def payment_success(request, uniqueId, planId, orderId):
    context = {}
    order_ref = '{}-{}-{}'.format(uniqueId, planId, orderId)
    # print(order_ref)

    try:
        package = SubscriptionPackage.objects.get(uniqueId=planId)
        package_name = package.package_name.lower().replace(' ', '-') if ' ' in package.package_name else package.package_name.lower()
        package_price = package.package_price

        try:
            profile = Profile.objects.get(uniqueId=uniqueId)
            profile.monthly_count = '0'
            profile.monthly_memory_count = '0'
            profile.subscribed = True
            profile.subscription_type = package_name
            profile.subscription_reference = order_ref
            profile.save()

            date_activated = timezone.localtime(timezone.now())

            date_expiry = date_activated + datetime.timedelta(days=30)
            if 'yearly' in package_name:
                date_expiry = date_activated + datetime.timedelta(days=365)
                package_price = int(package_price)*12
            print('date_expiry: {}'.format(date_expiry))

            has_team = False
            user_team = ''
            if 'team' in package.package_name.lower():
                has_team = True
                try:
                    this_user_team = Team.objects.get(uniqueId=profile.user_team)
                except:
                    this_user_team = Team.objects.create(
                        business_name='',
                        business_size='5',
                        industry='',
                        business_email=profile.user.email,
                        business_description='',
                        business_address=profile.address_line1,
                        business_status=True,
                        team_principal=profile.uniqueId,
                    )
                    this_user_team.save()

                    profile.user_team = this_user_team.uniqueId

                user_team = this_user_team.uniqueId

            # insert SubscriptionTransaction
            sub_transact = SubscriptionTransaction.objects.create(
                subscription_reference=order_ref,
                user_profile_uid=uniqueId,
                package_name=package.package_name.title(),
                package_price=package_price,
                has_team=has_team,
                user_team=user_team,
                date_activated=timezone.localtime(timezone.now()),
                date_expiry=date_expiry,

            )
            sub_transact.save()

            # update the team
            try:
                this_user_team = Team.objects.get(uniqueId=profile.user_team)

                find_team_members = Profile.objects.filter(user_team=this_user_team.uniqueId)

                for team_member in find_team_members:
                    if team_member.is_verified and team_member.is_active and team_member.user.is_active:
                        team_member.subscribed = profile.subscribed
                        team_member.subscription_type = profile.subscription_type
                        team_member.subscription_reference = profile.subscription_reference
                        team_member.save()

                return HttpResponse('SUCCESS')
            except:

                return HttpResponse('SUCCESS')
        except:
            return HttpResponse('FAIL: 001')
    except:
        return HttpResponse('FAIL: 002')


@login_required
def paypal_payment_success(request):
    if request.POST['subscriptionType'] == 'starter':
        try:
            profile = Profile.objects.get(uniqueId=request.POST['userId'])
            profile.subscribed = True
            profile.subscription_type = request.POST['subscriptionType']
            profile.subscription_reference = request.POST['subscriptionId']
            profile.save()
            return JsonResponse({'result': 'SUCCESS'})
        except:
            return JsonResponse({'result': 'FAIL'})

    elif request.POST['subscriptionType'] == 'professional':
        try:
            profile = Profile.objects.get(uniqueId=request.POST['userId'])
            profile.subscribed = True
            profile.subscription_type = request.POST['subscriptionType']
            profile.subscription_reference = request.POST['subscriptionId']
            profile.save()
            return JsonResponse({'result': 'SUCCESS'})
        except:
            return JsonResponse({'result': 'FAIL'})

    else:
        return JsonResponse({'result': 'FAIL'})


@login_required
def team_manager(request):
    context = {}

    current_page = "Team Manager"
    total_members = 0
    max_members = 10
    team_members = []

    total_invites = 0
    member_invites = []
    user_roles = []

    user_settings = []

    u_settings = UserSetting.objects.all()
    for u_set in u_settings:
        user_settings.append(u_set)

    user_profile = request.user.profile

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(request.user.profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar
    context['user_settings'] = user_settings

    if not 'teams' in user_profile.subscription_type:
        messages.error(request, "You subscription packages does not have access to this feature!")
        return redirect('billing')

    if user_profile.user_team is not None:

        this_user_team = Team.objects.get(uniqueId=user_profile.user_team)
        context['this_user_team'] = this_user_team
        find_team_members = Profile.objects.filter(user_team=this_user_team.uniqueId)

        for team_member in find_team_members:
            if team_member.is_verified:
                total_members += 1
                # team_member.subscribed=user_profile.subscribed
                # team_member.subscription_type=user_profile.subscription_type
                # team_member.subscription_reference=user_profile.subscription_reference
                # team_member.save()
                team_members.append(team_member)
            else:
                total_invites += 1
                member_invites.append(team_member)

    u_roles = UserRole.objects.filter(is_active=True).order_by('date_created')
    for role in u_roles:
        if role.user_team == this_user_team.uniqueId:
            user_roles.append(role)

    context['current_page'] = current_page
    context['total_members'] = str(total_members)
    context['team_members'] = team_members
    context['max_members'] = str(max_members)
    context['team_uid'] = user_profile.user_team
    context['total_invites'] = total_invites
    context['member_invites'] = member_invites
    context['user_roles'] = user_roles

    if request.method == 'POST':

        biz_name = request.POST['biz_name']
        industry = request.POST['industry']
        business_size = request.POST['business_size']
        biz_email = request.POST['biz_email']
        biz_address = request.POST['biz_address']
        biz_description = request.POST['biz_description']

        if user_profile.user_team is None:
            new_team = Team.objects.create(
                business_name=biz_name,
                business_size=business_size,
                industry=industry,
                business_email=biz_email,
                business_description=biz_description,
                business_address=biz_address,
                business_status=True,
                team_principal=request.user.profile.uniqueId,
            )
            new_team.save()
            profile = Profile.objects.get(uniqueId=user_profile.uniqueId)
            profile.user_team = new_team.uniqueId
            profile.save()
        else:
            edit_org = Team.objects.get(uniqueId=user_profile.user_team)

            if edit_org.team_principal == request.user.profile.uniqueId:
                edit_org.business_name = biz_name
                edit_org.business_size = business_size
                edit_org.industry = industry
                edit_org.business_email = biz_email
                edit_org.business_description = biz_description
                edit_org.business_address = biz_address
                edit_org.save()

    return render(request, 'dashboard/team-manager.html', context)


def activateEmail(request, user, user_team, password1=''):
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

    email = EmailMessage(mail_subject, message, to=[user.email], reply_to=[settings.EMAIL_REPLY_TO], headers=headers)
    email.content_subtype = 'html'
    if email.send():
        msg = f'Member successfully added to team, please tell them go to their email <b>{user.email}</b> inbox and click on \
                received activation link to confirm and complete the registration. <b>Note:</b> If not found check spam folder.'
    else:
        msg = f'Problem sending email to {user.email}, check if you typed it correctly.'

    return msg


@login_required
def edit_team_member(request):
    if request.method == 'POST':
        user_uid = request.POST['user_uid']

        first_name = request.POST['user_fname']
        last_name = request.POST['user_lname']
        # user_email = request.POST['user_email']

        user_language = request.POST['user_language']
        user_role = UserRole.objects.get(uniqueId=request.POST['user_role'])

        print(user_uid)
        try:
            user_profile = Profile.objects.get(uniqueId=user_uid)
            edit_user = User.objects.get(profile=user_profile)

            edit_user.first_name = first_name
            edit_user.last_name = last_name
            edit_user.save()

            user_set = UserSetting.objects.get(profile=user_profile)
            user_set.lang = user_language
            user_set.user_role = user_role
            user_set.save()

            resp = f"Member details updated successfully!"
        except:
            resp = f'User could not be found!'

    return HttpResponse(resp)


@login_required
def add_team_member(request):
    u_profile = request.user.profile

    if request.method == 'POST':

        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        user_email = request.POST['user_email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email_notify = False if request.POST.get('email_notify', False) == 'off' else True
        user_language = request.POST['user_language']
        user_role = UserRole.objects.get(uniqueId=request.POST['user_role'])

        if not validateEmail(user_email):
            messages.error(request, "Email address invalid!")
            return redirect('team-manager')

        if not password1 == password2:
            messages.error(request, "Passwords do not match!")
            return redirect('team-manager')

        if User.objects.filter(email=user_email).exists():
            messages.error(request,
                           "User email address {} already exists, please use a different email address!".format(
                               user_email))
            return redirect('team-manager')

        new_member = User.objects.create_user(email=user_email, username=user_email, first_name=first_name,
                                              last_name=last_name, password=password1, is_active=False)
        new_member.save()
        time.sleep(2)

        # get user team
        user_team = Team.objects.get(uniqueId=u_profile.user_team)

        nu_profile = Profile.objects.get(user=new_member)
        # New user inherites principal credentials
        nu_profile.user_team = user_team.uniqueId
        nu_profile.subscribed = u_profile.subscribed
        nu_profile.subscription_type = u_profile.subscription_type
        nu_profile.subscription_reference = u_profile.subscription_reference
        nu_profile.save()

        user_settings = UserSetting.objects.create(lang=user_language, email_verification='null', user_role=user_role,
                                                   profile=nu_profile)
        user_settings.save()

        success = activateEmail(request, new_member, user_team, password1)

        return HttpResponse(success)


@login_required
def resend_team_invite(request, orgUniqueId, uniqueId):
    user_profile = request.user.profile.user_team
    if orgUniqueId == user_profile:
        try:
            # get user team
            user_team = Team.objects.get(uniqueId=user_profile)

            member_p = Profile.objects.get(uniqueId=uniqueId)
            success = activateEmail(request, member_p.user, user_team)

            messages.success(request, success)
        except:
            resp_msg = "Action not allowed, this user does not belong to your team!"
            messages.error(request, resp_msg)

        # resp_msg = '{}-{}'.format(member_p.user.email, user_team)
        # print(resp_msg)
    else:
        resp_msg = "Action not allowed, you do not have permission to access this team!"
        messages.error(request, resp_msg)

    print(resp_msg)

    return redirect('team-manager')


@login_required
def delete_member(request, orgUniqueId, uniqueId):
    get_this_org = Team.objects.get(uniqueId=orgUniqueId)
    user_profile = request.user.profile

    try:
        if user_profile.user_team == orgUniqueId:

            member = Profile.objects.get(uniqueId=uniqueId)
            if member.profile.uniqueId == user_profile.uniqueId:
                # member.delete()
                messages.error(request, "Action not allowed, you cannot remove yourself from this team!")
                return redirect('team-manager')

            elif not member.profile.user_team == orgUniqueId:
                messages.error(request, "Action not allowed, this user does not belong to your team!")
                return redirect('team-manager')

            elif get_this_org.team_principal == member.profile.uniqueId:
                messages.error(request, "Action not allowed, You cannot remove team principal from this team!")
                return redirect('team-manager')

            else:
                member.is_active = False
                member.save()

                messages.success(request, "Team member removed successfully!")
                return redirect('team-manager')

        else:
            messages.error(request, "Action not allowed, looks like you do not belong to this team!")
            return redirect('dashboard')
    except:
        messages.error(request, "Member not found!")
        return redirect('team-manager')


@login_required
def delete_invite(request, userUid, uniqueId):
    try:
        if request.user.profile.uniqueId == userUid:
            invite = MemberInvite.objects.get(uniqueId=uniqueId)
            invite.delete()

            messages.success(request, "Team member invite removed successfully!")
            return redirect('team-manager')

        else:
            messages.error(request, "Action not allowed, looks like you did not invite this member")
            return redirect('dashboard')
    except:
        messages.error(request, "Member not found!")
        return redirect('team-manager')


@login_required
def device_manager(request):
    context = {}

    current_page = 'Device Manager'
    total_devices = 0
    # max_devices = 10

    user_profile = request.user.profile
    # find if user is on premium package
    if user_profile.subscription_type == 'free':
        user_sub_pack = SubscriptionPackage.objects.get(uniqueId=settings.FREE_SUBSCR_PACKAGE)
    else:
        # find user package from package ref
        user_package_ref = user_profile.subscription_reference
        user_subscrip_pakg = user_package_ref.split('-')[1]

        user_sub_pack = SubscriptionPackage.objects.get(uniqueId=user_subscrip_pakg)

    max_devices = int(user_sub_pack.package_max_device)

    context['current_page'] = current_page
    reg_devices = []
    user_reg_devices = RegisteredDevice.objects.filter(profile=user_profile)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    for user_device in user_reg_devices:
        reg_devices.append(user_device)
        total_devices += 1

    context['reg_devices'] = reg_devices
    context['total_devices'] = str(total_devices)
    context['max_devices'] = max_devices

    return render(request, 'dashboard/device-manager.html', context)


@login_required
def delete_device(request, uniqueId):
    try:
        device = RegisteredDevice.objects.get(uniqueId=uniqueId)
        if device.profile == request.user.profile:
            device.delete()
            messages.info(request, "Device deleted successfully!")
            return redirect('device-manager')
        else:
            messages.error(request, "Access denied!")
            return redirect('dashboard')
    except:
        messages.error(request, "Device not found!")
        return redirect('device-manager')


@login_required
def memory_blogs(request, status):
    context = {}

    empty_blogs = []
    complete_blogs = []
    edited_blogs = []

    today_date = datetime.datetime.now()

    q_year = today_date.year
    q_month = today_date.month

    cate_list = []
    client_list = []

    user_profile = request.user.profile
    user_team_id = user_profile.user_team

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(request.user.profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_team_id:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_team_id)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    context['blogs_status'] = status

    user_team = Team.objects.get(uniqueId=user_team_id)

    # Get total blogs
    blogs = Blog.objects.all().order_by('last_updated')

    # check memory limit
    user_momery_limit = package_memory_limit(profile=user_profile)

    cnt_memry = 1

    for blog in blogs:
        if not blog.deleted and blog.profile.user_team == user_team_id and int(user_momery_limit) > 0:
            sections = BlogSection.objects.filter(blog=blog)
            saved_sections = SavedBlogEdit.objects.filter(blog=blog)

            if saved_sections.exists():
                edited_blogs.append(blog)

            if sections.exists():
                # calculate blog words
                blog_words = 0
                for section in sections:
                    blog_words += int(section.word_count)
                    # month_word_count += int(section.word_count)
                if blog.word_count is not None and int(blog.word_count) < 1:
                    blog.word_count = str(blog_words)
                    blog.save()
                complete_blogs.append(blog)
            else:
                empty_blogs.append(blog)
            # if limit is reached break loop
            if user_momery_limit == cnt_memry:
                break

        cnt_memry += 1

    context['empty_blogs'] = empty_blogs
    context['complete_blogs'] = complete_blogs
    context['edited_blogs'] = edited_blogs

    context['allowance'] = check_count_allowance(request.user.profile)

    current_page = 'Blog Memory'
    context['current_page'] = current_page

    return render(request, 'dashboard/blog-memory.html', context)


@login_required
def memory_social_post(request, socType='blog'):
    context = {}

    s_posts = []
    my_blogs = []
    cate_list = []
    client_list = []

    user_profile = request.user.profile
    user_team_id = user_profile.user_team

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_team_id:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_team_id)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    if socType == 'blog':

        current_page = 'Blog Social Media Posts'

        # Get total blogs
        blogs = Blog.objects.filter(profile=user_profile).order_by('last_updated')
        for blog in blogs:
            if not blog.deleted:
                my_blogs.append(blog)

        # get social posts
        soc_posts = BlogSocialPost.objects.filter(deleted=False)
        for post in soc_posts:
            if not post.deleted and post.blog.profile.user_team == user_team_id:
                s_posts.append(post)

        context['my_blogs'] = my_blogs

    else:
        current_page = 'Social Media Posts'
        # get social posts
        soc_posts = SocialPost.objects.filter(deleted=False)
        for post in soc_posts:
            if not post.deleted and post.profile.user_team == user_team_id:
                s_posts.append(post)

    context['soc_type'] = socType
    context['s_posts'] = s_posts

    context['allowance'] = check_count_allowance(request.user.profile)

    context['current_page'] = current_page

    return render(request, 'dashboard/social-media-memory.html', context)


@login_required
def memory_paragraph(request):
    context = {}
    saved_paragraphs = []
    today_date = datetime.datetime.now()

    q_year = today_date.year
    q_month = today_date.month

    cate_list = []
    client_list = []

    user_profile = request.user.profile
    user_team_id = user_profile.user_team

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_profile.user_team)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    paragraphs = Paragraph.objects.filter(profile=user_profile).order_by('last_updated')

    for summary in paragraphs:
        if not summary.deleted and summary.profile.user_team == user_team_id:
            saved_paragraphs.append(summary)

    context['saved_paragraphs'] = saved_paragraphs

    context['allowance'] = check_count_allowance(request.user.profile)

    current_page = 'Paragraph Memory'
    context['current_page'] = current_page

    return render(request, 'dashboard/paragraph-memory.html', context)


@login_required
def memory_sentence(request):
    context = {}
    saved_sentence = []
    today_date = datetime.datetime.now()

    q_year = today_date.year
    q_month = today_date.month

    cate_list = []
    client_list = []

    user_profile = request.user.profile
    user_team_id = user_profile.user_team
    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_profile.user_team)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    sentences = Sentence.objects.filter(profile=request.user.profile).order_by('last_updated')

    for sentence in sentences:
        if not sentence.deleted and sentence.profile.user_team == user_team_id:
            saved_sentence.append(sentence)

    context['saved_sentence'] = saved_sentence

    context['allowance'] = check_count_allowance(request.user.profile)

    current_page = 'Sentence Memory'
    context['current_page'] = current_page

    return render(request, 'dashboard/sentence-memory.html', context)


@login_required
def memory_title(request):
    context = {}
    saved_title = []
    today_date = datetime.datetime.now()

    q_year = today_date.year
    q_month = today_date.month

    cate_list = []
    client_list = []

    user_profile = request.user.profile
    user_team_id = user_profile.user_team

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_profile.user_team)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    article_titles = ArticleTitle.objects.filter(profile=request.user.profile).order_by('last_updated')

    for title in article_titles:
        if not title.deleted and title.profile.user_team == user_team_id:
            saved_title.append(title)

    context['saved_title'] = saved_title

    context['allowance'] = check_count_allowance(request.user.profile)

    current_page = 'Title Memory'
    context['current_page'] = current_page

    return render(request, 'dashboard/title-memory.html', context)


@login_required
def memory_summarizer(request):
    context = {}
    saved_summaries = []

    today_date = datetime.datetime.now()

    q_year = today_date.year
    q_month = today_date.month

    cate_list = []
    client_list = []

    user_profile = request.user.profile
    user_team_id = user_profile.user_team
    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_profile.user_team)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    # Get total summaries
    summaries = ContentSummary.objects.filter(profile=user_profile).order_by('last_updated')

    for summary in summaries:
        if not summary.deleted and summary.profile.user_team == user_team_id:
            saved_summaries.append(summary)

    context['saved_summaries'] = saved_summaries

    context['allowance'] = check_count_allowance(request.user.profile)

    current_page = 'Summariser Memory'
    context['current_page'] = current_page

    return render(request, 'dashboard/summarizer-memory.html', context)


@login_required
def memory_page_copy(request):
    context = {}

    saved_page_copies = []

    today_date = datetime.datetime.now()

    q_year = today_date.year
    q_month = today_date.month

    cate_list = []
    client_list = []

    user_profile = request.user.profile
    user_team_id = user_profile.user_team
    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_team_id:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_team_id)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    # Get total summaries
    page_copies = LandingPageCopy.objects.filter(profile=user_profile).order_by('last_updated')

    for page_copy in page_copies:
        if not page_copy.deleted and page_copy.profile.user_team == user_team_id:
            saved_page_copies.append(page_copy)

    context['saved_page_copies'] = saved_page_copies

    context['allowance'] = check_count_allowance(request.user.profile)

    current_page = 'Page Copy Memory'
    context['current_page'] = current_page

    return render(request, 'dashboard/page-copy-memory.html', context)


@login_required
def memory_meta_descr(request):
    context = {}

    saved_meta_descriptions = []

    cate_list = []
    client_list = []

    user_profile = request.user.profile
    user_team_id = user_profile.user_team
    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_team_id:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_team_id)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    # Get total summaries
    meta_descriptions = MetaDescription.objects.filter(profile=user_profile).order_by('last_updated')

    for meta_description in meta_descriptions:
        if not meta_description.deleted and meta_description.profile.user_team == user_team_id:
            saved_meta_descriptions.append(meta_description)

    context['saved_meta_descriptions'] = saved_meta_descriptions

    context['allowance'] = check_count_allowance(user_profile)

    current_page = 'Meta Description Memory'
    context['current_page'] = current_page

    return render(request, 'dashboard/meta-description-memory.html', context)


@login_required
def memory_content_improver(request):
    context = {}
    saved_content = []

    cate_list = []
    client_list = []

    user_profile = request.user.profile
    user_team_id = user_profile.user_team
    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_team_id:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_team_id)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    # Get total summaries
    improved_content = ContentImprover.objects.filter(profile=user_profile).order_by('last_updated')

    for content in improved_content:
        if not content.deleted and content.profile.user_team == user_team_id:
            saved_content.append(content)

    context['saved_content'] = saved_content

    context['allowance'] = check_count_allowance(user_profile)

    current_page = 'Content Improver Memory'
    context['current_page'] = current_page

    return render(request, 'dashboard/content-improver-memory.html', context)


@login_required
def categories(request):
    context = {}

    current_page = 'Categories'
    context['current_page'] = current_page

    cate_list = []
    client_list = []

    user_profile = request.user.profile
    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(team=user_profile.user_team)

    for category in team_categories:
        cate_list.append(category)

    context['cate_list'] = cate_list
    context['client_list'] = client_list

    if request.method == "POST":
        client_id = request.POST['client']

        team_client = TeamClient.objects.get(uniqueId=client_id)

        category_name = request.POST['new-cate-name']
        cate_descr = request.POST['cate-description']

        if len(category_name) > 3:
            new_cate = ClientCategory.objects.create(
                category_name=category_name,
                description=cate_descr,
                created_by=user_profile.uniqueId,
                team=user_profile.user_team,
                client=team_client,
            )
            new_cate.save()
            return redirect('categories')

    return render(request, 'dashboard/categories.html', context)


@login_required
def clients(request):
    context = {}

    current_page = 'Clients'
    context['current_page'] = current_page

    client_list = []
    user_profile = request.user.profile
    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    team_clients = TeamClient.objects.filter(team=user_profile.user_team)

    for client in team_clients:
        client_list.append(client)

    context['client_list'] = client_list

    if request.method == "POST":
        client_name = request.POST['new-client-name']
        contact_name = request.POST['nc-contact-name']
        client_email = request.POST['nc-contact-email']
        client_industry = request.POST['nc-industry']
        client_address = request.POST['nc-address']

        if len(client_name) > 3:
            new_client = TeamClient.objects.create(
                client_name=client_name,
                contact_person=contact_name,
                industry=client_industry,
                client_email=client_email,
                business_address=client_address,
                created_by=user_profile.uniqueId,
                team=user_profile.user_team,
            )
            new_client.save()

            return redirect('clients')

    return render(request, 'dashboard/clients.html', context)


@login_required
def delete_client(request, uniqueId):
    context = {}

    current_page = 'Delete Client'
    context['current_page'] = current_page

    user_profile = request.user.profile

    client = TeamClient.objects.get(uniqueId=uniqueId)

    if client.team == user_profile.user_team:
        client.delete()
    else:
        messages.error(request, "Action denied on this client!")
        return redirect('clients')

    return redirect('clients')


@login_required
def change_client_status(request, status, uniqueId):
    context = {}

    current_page = 'Edit Category'
    context['current_page'] = current_page

    client_status = False

    if status == 'activate':
        client_status = True

    user_profile = request.user.profile

    client = TeamClient.objects.get(uniqueId=uniqueId)

    if client.team == user_profile.user_team:
        client.is_active = client_status
        client.save()
    else:
        messages.error(request, "Action denied on this client!")
        return redirect('clients')

    return redirect('clients')


@login_required
def edit_client(request):
    context = {}
    current_page = 'Edit Client'
    parent_page = 'Clients'

    context['current_page'] = current_page
    context['parent_page'] = parent_page
    context['parent_page_url'] = 'clients'

    resp = "Error, something went wrong!"

    client_id = request.POST['client_code']

    try:
        this_client = TeamClient.objects.get(uniqueId=client_id)

        if request.method == 'POST':
            client_name = request.POST['client_name']
            contact_name = request.POST['contact_name']
            client_email = request.POST['contact_email']
            client_industry = request.POST['industry']
            client_address = request.POST['address']
            client_descr = request.POST['client_descr']

            if len(client_name) > 3:
                this_client.client_name = client_name
                this_client.contact_person = contact_name
                this_client.industry = client_industry
                this_client.client_email = client_email
                this_client.business_address = client_address
                this_client.description = client_descr
                this_client.save()
                resp = "Client updated successfully"
    except:
        resp = "Client updated successfully"

    return HttpResponse(resp)


@login_required
def edit_category(request, uniqueId):
    context = {}

    current_page = 'Edit Category'
    parent_page = 'Categories'
    context['current_page'] = current_page
    context['parent_page'] = parent_page
    context['parent_page_url'] = 'categories'

    client_list = []

    user_profile = request.user.profile
    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    team_clients = TeamClient.objects.filter(is_active=True)

    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    context['client_list'] = client_list

    this_cate = ClientCategory.objects.get(uniqueId=uniqueId)
    this_cate_name = this_cate.category_name
    this_cate_descr = this_cate.description

    context['cate_name'] = this_cate_name
    context['cate_descr'] = this_cate_descr
    context['cate_client'] = this_cate.client.uniqueId

    if request.method == 'POST':
        category_name = request.POST['new-cate-name']
        cate_descr = request.POST['cate-description']
        # cate_descr = request.POST['cate-description']

        client_id = request.POST['client']

        team_client = TeamClient.objects.get(uniqueId=client_id)

        if len(category_name) > 3:
            this_cate.category_name = category_name
            this_cate.description = cate_descr
            this_cate.client = team_client
            this_cate.save()

            return redirect('categories')

    return render(request, 'dashboard/edit-category.html', context)


@login_required
def change_category_status(request, status, uniqueId):
    context = {}

    current_page = 'Edit Category'
    context['current_page'] = current_page

    cate_status = False

    if status == 'activate':
        cate_status = True

    user_profile = request.user.profile
    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(user_profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    context['lang'] = lang
    context['flag_avatar'] = flag_avatar

    category = ClientCategory.objects.get(uniqueId=uniqueId)

    if category.client.team == user_profile.user_team:
        category.is_active = cate_status
        category.save()
    else:
        messages.error(request, "Action denied on this category!")

        return redirect('categories')

    return redirect('categories')


@login_required
def delete_category(request, uniqueId):
    context = {}

    current_page = 'Delete Category'
    context['current_page'] = current_page

    user_profile = request.user.profile

    category = ClientCategory.objects.get(uniqueId=uniqueId)

    if category.client.team == user_profile.user_team:
        category.delete()
    else:
        messages.error(request, "Action denied on this category!")
        return redirect('categories')

    return redirect('categories')


@login_required
def user_roles(request):
    context = {}

    current_page = "User Roles"
    user_roles = []

    permission_levels = []
    user_profile = request.user.profile
    this_user_team = Team.objects.get(uniqueId=user_profile.user_team)

    lang = settings.LANGUAGE_CODE
    flag_avatar = 'dash/images/gb_flag.jpg'

    lang = check_user_lang(request.user.profile, lang)

    if lang == 'en-us':
        flag_avatar = 'dash/images/us_flag.jpg'

    if not 'teams' in user_profile.subscription_type:
        messages.error(request, "You subscription packages does not have access to this feature!")
        return redirect('billing')

    if user_profile.user_team is not None:

        try:
            perm_levels = PermissionLevel.objects.filter(is_active=True).order_by('date_created')
            for p_level in perm_levels:
                permission_levels.append(p_level)

            u_roles = UserRole.objects.filter(is_active=True).order_by('date_created')
            for role in u_roles:
                if role.user_team == this_user_team.uniqueId:
                    user_roles.append(role)

        except:
            return redirect('profile')

        context['current_page'] = current_page
        context['this_user_team'] = this_user_team
        context['user_roles'] = user_roles
        context['permission_levels'] = permission_levels
        context['lang'] = lang
        context['flag_avatar'] = flag_avatar

    else:
        return redirect('billing')

    if request.method == 'POST':
        permission = PermissionLevel.objects.get(uniqueId=request.POST['permission'])
        role_name = request.POST['role-name']
        abbreviation = request.POST['abbreviation']

        can_write = True if request.POST.get('role-can-write', False) == 'on' else False
        can_edit = True if request.POST.get('role-can-edit', False) == 'on' else False
        can_delete = True if request.POST.get('role-can-delete', False) == 'on' else False

        can_create_team = True if request.POST.get('can-invite', False) == 'on' else False
        can_edit_team = True if request.POST.get('can-edit-team', False) == 'on' else False
        can_delete_team = True if request.POST.get('can-delete-team', False) == 'on' else False

        new_role = UserRole.objects.create(
            role_name=role_name,
            abbreviation=abbreviation,
            permission=permission,
            user_team=request.user.profile.user_team,
            can_write=can_write,
            can_edit=can_edit,
            can_delete=can_delete,
            can_create_team=can_create_team,
            can_edit_team=can_edit_team,
            can_delete_team=can_delete_team,
        )
        new_role.save()

    return render(request, 'dashboard/user-roles.html', context)


@login_required
def edit_user_roles(request, team_uid, uniqueId):
    resp = ''
    try:
        user_role = UserRole.objects.get(uniqueId=uniqueId)

        if team_uid == request.user.profile.user_team:
            # assign users to the closest role
            if request.method == 'POST':
                user_role.role_name = request.POST['role_name']
                user_role.permission = request.POST['role_permission']
                user_role.abbreviation = request.POST['role_abbr']
                user_role.can_write = request.POST['role_can_write']
                user_role.can_edit = request.POST['role_can_edit']
                user_role.can_delete = request.POST['role_can_delete']
                user_role.can_create_team = request.POST['can_invite']
                user_role.can_edit_team = request.POST['can_edit_team']
                user_role.can_delete_team = request.POST['can_delete_team']
                user_role.save()

                resp = "Role updated successfully"
            else:
                resp = "Not allowed, Post method not found!"
        else:
            resp = "Not allowed, You have no permission to make this change!"
    except:
        resp = "Something went wrong, please try again!"

    return HttpResponse(resp)


def download_content_file(request, content_type, uniqueId):
    cont_text = ''

    if 'blog' in content_type:

        blog_body = ''
        blog_sections = []
        try:
            blog = Blog.objects.get(uniqueId=uniqueId)
        except:
            messages.error(request, "Something went wrong with your request, please try again!")
            return redirect('blog-topic')

        if content_type == 'blog_writer':
            # fetch created blog sections
            blog_sects = BlogSection.objects.filter(blog=blog)
            for sect in blog_sects:
                blog_sections.append(sect.body)

            blog_body = "\n".join(blog_sections)

        elif content_type == 'edit_blog':
            # fetch edited blog sections
            blog_sects = SavedBlogEdit.objects.filter(blog=blog)
            for sect in blog_sects:
                blog_sections.append(sect.body)

            blog_body = "\n".join(blog_sections)

        cont_text = blog_body.replace('<br>', '\n')

    elif 'social' in content_type:
        soc_type = content_type.split('_')

        # if soc_type == ''
        soc_post = SocialPost.objects.get(uniqueId=uniqueId)
        cont_text = soc_post.post

    elif content_type == 'paragraph_writer':
        paragraph = Paragraph.objects.get(uniqueId=uniqueId)
        cont_text = paragraph.paragraph

    elif content_type == 'sentence_writer':
        sentence = Sentence.objects.get(uniqueId=uniqueId)
        cont_text = sentence.new_sentence

    elif content_type == 'meta_writer':
        meta_descr = MetaDescription.objects.get(uniqueId=uniqueId)
        cont_text = meta_descr.meta_description

    elif content_type == 'copy_writer':
        gen_copy = LandingPageCopy.objects.get(uniqueId=uniqueId)
        cont_text = gen_copy.page_copy

    elif content_type == 'content_improver':
        impr_cont = ContentImprover.objects.get(uniqueId=uniqueId)
        cont_text = impr_cont.content_body_new.replace('<br>', '\n')

    # print(str(uuid4()))

    uuid_str = str(uuid4()).split('-')[3]

    filen = "writesome_{}_{}".format(content_type, uuid_str)
    # to write to your file
    file_name = open("{}.txt".format(filen), "w+")
    file_name.write(cont_text)
    file_name.close()

    # to read the content of it
    read_file = open("{}.txt".format(filen), "r")
    response = HttpResponse(read_file.read(), content_type="text/plain,charset=utf8")
    read_file.close()

    response['Content-Disposition'] = 'attachment; filename="{}.txt"'.format(filen)
    return response


@login_required
def delete_user_role(request, team_uid, uniqueId):
    try:
        user_role = UserRole.objects.get(uniqueId=uniqueId)

        if team_uid == request.user.profile.user_team:
            # assign users to the closest role
            user_role.is_active
            user_role.save()
    except:
        messages.error(request, "Something went wrong, please try again!")
        return redirect('user-roles')

    return redirect('user-roles')


@login_required
def get_role_details(request):
    resp_data = {}

    if request.method == 'POST':
        role_id = request.POST['role_id']

        user_role = UserRole.objects.get(uniqueId=role_id)

        resp_data = {
            'result': 'success',
            'message': 'Role found successfully',
            'role_name': user_role.role_name,
            'role_team_id': user_role.user_team,
            'role_perm_name': user_role.permission.permission_name,
            'abbreviation': user_role.abbreviation,
            'can_write': user_role.can_write,
            'can_edit': user_role.can_edit,
            'can_delete': user_role.can_delete,
            'can_create_team': user_role.can_create_team,
            'can_edit_team': user_role.can_edit_team,
            'can_delete_team': user_role.can_delete_team
        }
    else:
        resp_data = {
            'result': 'error',
            'message': 'User role could not be found!',
        }

    return JsonResponse(json.dumps(resp_data), content_type="application/json", safe=False)
#
