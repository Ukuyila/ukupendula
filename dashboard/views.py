import datetime
import hashlib
import time
import urllib.parse

#payfast imports
import requests
import urllib.parse
import socket
from werkzeug.urls import url_parse

# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages

# Other Auth imports
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse

from uuid import uuid4

# local imports.
from .forms import *
from .models import *
from .functions import *


@login_required
def home(request):
    context = {}

    user_profile = request.user.profile

    empty_blogs = []
    complete_blogs = []

    max_devices_allow = 5

    today_date = datetime.datetime.now()

    remove_api_requests(user_profile)

    remote_addr = requests.get('https://checkip.amazonaws.com').text.strip()

    q_year = today_date.year
    q_month = today_date.month

    # DIRECT TO PROFILE IF EMAIL IS VERIFIED AND USER DETAILS ARE NOT FILLED OUT
    if User.first_name is None:
        messages.error(request, "Your profile is not complete, please fill all the details!")
        return redirect('profile')
    
    # REGISTER DEVICE
    device_reg = device_registration(request, max_devices_allow)

    if device_reg == 'error: max device':
        # log user out and give solution to remove device
        messages.error(request, "You have maximum devices logged in on your profile!")
        return redirect('login')
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
        sections = BlogSection.objects.filter(blog=blog)
        if sections.exists():
            # calculate blog words
            blog_words = 0
            for section in sections:

                blog_words += int(section.word_count)

                # month_word_count += int(section.word_count)
            blog.word_count = str(blog_words)
            blog.save()
            complete_blogs.append(blog)
        else:
            empty_blogs.append(blog)

    blog_word_cnt = get_blog_word_cnt(str(q_year), str(q_month), user_profile)
    lm_blog_word_cnt = get_blog_word_cnt(str(q_year), str(q_month-1), user_profile)
    # lm_blog_word_cnt = 10000

    para_word_cnt = get_para_word_cnt(str(q_year), str(q_month), user_profile)
    lm_para_word_cnt = get_para_word_cnt(str(q_year), str(q_month-1), user_profile)

    sentence_word_cnt = get_sentence_word_cnt(str(q_year), str(q_month), user_profile)
    lm_sentence_word_cnt = get_sentence_word_cnt(str(q_year), str(q_month-1), user_profile)

    meta_word_cnt = get_meta_word_cnt(str(q_year), str(q_month), user_profile)
    lm_meta_word_cnt = get_meta_word_cnt(str(q_year), str(q_month-1), user_profile)

    summarizer_word_cnt = get_summarizer_word_cnt(str(q_year), str(q_month), user_profile)
    lm_summarizer_word_cnt = get_summarizer_word_cnt(str(q_year), str(q_month-1), user_profile)

    landing_copy_word_cnt = get_land_copy_word_cnt(str(q_year), str(q_month), user_profile)
    lm_landing_copy_word_cnt = get_land_copy_word_cnt(str(q_year), str(q_month-1), user_profile)

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
        context['blg_carret_set'] = ' fa-caret-up text-success '
    else:
        context['clm_blog_word_cnt'] = get_percent_of(blog_word_cnt, lm_blog_word_cnt)
        context['blg_carret_set'] = ' fa-caret-down text-danger '

    if int(summarizer_word_cnt) > int(lm_summarizer_word_cnt):
        context['clm_summarizer_word_cnt'] = get_percent_of(lm_summarizer_word_cnt, summarizer_word_cnt)
        context['sumry_carret_set'] = ' fa-caret-up text-success '
    else:
        context['clm_summarizer_word_cnt'] = get_percent_of(summarizer_word_cnt, lm_summarizer_word_cnt)
        context['sumry_carret_set'] = ' fa-caret-down text-danger '

    if int(meta_word_cnt) > int(lm_meta_word_cnt):
        context['clm_meta_word_cnt'] = get_percent_of(lm_meta_word_cnt, meta_word_cnt)
        context['meta_carret_set'] = ' fa-caret-up text-success '
    else:
        context['clm_meta_word_cnt'] = get_percent_of(meta_word_cnt, lm_meta_word_cnt)
        context['meta_carret_set'] = ' fa-caret-down text-danger '

    if int(landing_copy_word_cnt) > int(lm_landing_copy_word_cnt):
        context['clm_landing_copy_word_cnt'] = get_percent_of(lm_landing_copy_word_cnt, landing_copy_word_cnt)
        context['lpc_carret_set'] = ' fa-caret-up text-success '
    else:
        context['clm_landing_copy_word_cnt'] = get_percent_of(landing_copy_word_cnt, lm_landing_copy_word_cnt)
        context['lpc_carret_set'] = ' fa-caret-down text-danger '

    context['clm_para_word_cnt'] = para_word_cnt
    context['clm_sentence_word_cnt'] = sentence_word_cnt
    
    context['num_blogs'] = len(complete_blogs)
    context['count_reset'] = '01 June 2023'  # update later

    context['empty_blogs'] = empty_blogs
    context['complete_blogs'] = complete_blogs

    context['allowance'] = check_count_allowance(user_profile)

    current_page = 'Home'
    context['current_page'] = current_page

    return render(request, 'dashboard/index.html', context)


@login_required
def profile(request):
    context = {}

    current_page = 'My Profile'
    context['current_page'] = current_page

    context['allowance'] = check_count_allowance(request.user.profile)

    remove_api_requests(request.user.profile)

    if request.method == 'GET':
        form = ProfileForm(instance=request.user.profile, user=request.user)
        image_form = ProfileImageForm(instance=request.user.profile)
        context['form'] = form
        context['image_form'] = image_form

        return render(request, 'dashboard/profile.html', context)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile, user=request.user)
        image_form = ProfileImageForm(request.POST, request.FILES, instance=request.user.profile)

        if form.is_valid():
            form.save()
            return redirect('profile')

        if image_form.is_valid():
            image_form.save()
            return redirect('profile')
        else:
            messages.error(request, "Something is a foot")

    return render(request, 'dashboard/profile.html', context)


@login_required
def blog_topic(request):
    context = {}

    tone_of_voices = []

    current_page = 'Blog Topic Generator'

    context['current_page'] = current_page

    context['allowance'] = check_count_allowance(request.user.profile)

    remove_api_requests(request.user.profile)

    tones = ToneOfVoice.objects.filter(tone_status=True)

    for tone in tones:
        tone_of_voices.append(tone)

    context['tone_of_voices'] = tone_of_voices

    if request.method == 'POST':
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
                    blog_topics = generate_blog_topic_ideas(blog_idea, audience, keywords)
                
                    add_to_list.is_done=True
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

    if 'blog_topics' in request.session:
        pass
    else:
        messages.error(request, "You have to create blog topic first!")
        return redirect('blog-topic')

    context = {'current_page': current_page, 'allowance': check_count_allowance(request.user.profile), 'blog_topics': request.session['blog_topics']}

    return render(request, 'dashboard/blog-sections.html', context)


@login_required
def delete_blog_topic(request, uniqueId):
    try:
        blog = Blog.objects.get(uniqueId=uniqueId)
        if blog.profile == request.user.profile:
            blog.delete()
            messages.info(request, "Blog deleted successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Access denied!")
            return redirect('dashboard')
    except:
        messages.error(request, "Blog not found!")
        return redirect('dashboard')


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
            max_words= str(request.session['max_words']),
            profile=request.user.profile,
        )
        blog.save()

        blog_topics = request.session['blog_topics']
        blog_topics.remove(blog_topic)
        request.session['blog_topics'] = blog_topics

        return redirect('blog-sections')
    else:
        return redirect('blog-topic')


# This generates blog from session topic
@login_required
def use_blog_topic(request, blog_topic):

    blog_topic = requests.utils.unquote(blog_topic)
    print('Blog topic: '.format(blog_topic))
    context = {}

    current_page = 'Use Blog Sections Generator'

    context['current_page'] = current_page

    context['allowance'] = check_count_allowance(request.user.profile)

    remove_api_requests(request.user.profile)

    if 'blog-sections' in request.session and 'uniqueId' in request.session:

        uniqueId = request.session['uniqueId']
        
        context['uniqueId'] = uniqueId
        blog_section_heads = request.session['blog-sections']
        saved_sect_head = request.session['saved_sect_head']

        blog = Blog.objects.get(uniqueId=uniqueId)
        
        context['saved_sect_head'] = saved_sect_head

    else:

        if 'blog_idea' in request.session and 'keywords' in request.session and 'audience' in request.session:
            # save blog topic idea first
            # code to save
            blog = Blog.objects.create(
                title=blog_topic,
                blog_idea=request.session['blog_idea'],
                keywords=request.session['keywords'],
                audience=request.session['audience'],
                profile=request.user.profile,
            )
            blog.save()

            context['uniqueId'] = blog.uniqueId

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
                    blog_section_heads = generate_blog_section_headings(blog_topic, request.session['audience'], request.session['keywords'])
                    
                    add_to_list.is_done=True
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
        request.session['saved_sect_head'] = section_head
        context['blog_sections'] = blog_section_heads
        print("saved: ".format(section_head))
        return redirect('use-blog-topic', blog_topic)
    else:
        return redirect('blog-sections')

        
# this generates blog from saved topic
@login_required
def create_blog_from_topic(request, uniqueId):
    context = {}

    current_page = 'Use Blog Sections Generator'

    context['current_page'] = current_page

    context['allowance'] = check_count_allowance(request.user.profile)

    try:
        blog = Blog.objects.get(uniqueId=uniqueId)

        # blog_section_heads = generate_blog_section_headings(blog.title, blog.audience, blog.keywords)

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
                blog_section_heads = generate_blog_section_headings(blog.title, blog.audience, blog.keywords)
                
                add_to_list.is_done=True
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
            for val in request.POST:
                if not 'csrfmiddlewaretoken' in val:

                    api_call_code = str(uuid4()).split('-')[4]

                    # api_requests = check_api_requests()

                    add_to_list = add_to_api_requests('generate_blog_section_details', api_call_code, request.user.profile)

                    n = 1
                    # runs until n < 50,just to avoid the infinite loop.
                    # this will execute the check_api_requests() func in every 5 seconds.
                    while n < 50:
                        # api_requests = check_api_requests()
                        time.sleep(5)
                        if api_call_process(api_call_code, add_to_list):
                            gen_section = generate_blog_section_details(blog.title, val, blog.audience, blog.keywords, request.user.profile)

                            # create database record
                            blog_sect = BlogSection.objects.create(
                                title=val,
                                body=gen_section,
                                blog=blog,
                            )
                            blog_sect.save()

                            add_to_list.is_done=True
                            add_to_list.save()

                            time.sleep(5)
                            break
                        else:
                            # we might need to delete all abandoned calls
                            pass
                        n += 1

                    # Analyze how this makes the AI not to repeat what was already done
                    # collect previous blog sections
                    # prev_blog = ''
                    # b_sections = BlogSection.objects.filter(blog=blog).order_by('date_created')
                    # for sec in b_sections:
                    #     prev_blog += sec.title + '\n'
                    #     prev_blog += sec.body.replace('<br>', '\n')
                    # # generating blog section details
                    # prev_blog = ''
                    # gen_section = generate_blog_section_details(
                    #     blog_topic, val, request.session['audience'], request.session['keywords'], prev_blog,
                    #     request.user.profile)
                    #
                    # # create database record
                    # blog_sect = BlogSection.objects.create(
                    #     title=val,
                    #     body=gen_section,
                    #     blog=blog,
                    # )
                    # blog_sect.save()
                    # time.sleep(2)

            return redirect('view-generated-blog', slug=blog.slug)

    except:
        messages.error(request, "Blog not found!")
        redirect('dashboard')

    return render(request, 'dashboard/select-blog-sections.html', context)


@login_required
def view_gen_blog(request, slug):

    context = {}

    current_page = 'Blog Generator'

    context['current_page'] = current_page

    context['allowance'] = check_count_allowance(request.user.profile)

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
                            gen_section = generate_full_blog(blog.title, section_heads, blog.audience, blog.keywords, blog.tone_of_voice, min_words, blog.max_words, request.user.profile)

                            # create database record
                            blog_sect = BlogSection.objects.create(
                                title=blog.title,
                                body=gen_section,
                                blog=blog,
                            )
                            blog_sect.save()

                            add_to_list.is_done=True
                            add_to_list.save()

                            # fetch created blog sections
                            blog_sects = BlogSection.objects.filter(blog=blog)

                            del request.session['uniqueId']
                            del request.session['blog-sections']
                            del request.session['selectd_sections']
                            del request.session['blog_idea']
                            del request.session['keywords']
                            del request.session['audience']
                            del request.session['saved_sect_head']

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

    context['current_page'] = current_page

    context['allowance'] = check_count_allowance(request.user.profile)

    try:
        blog = Blog.objects.get(uniqueId=uniqueId)
    except:
        messages.error(request, "Something went wrong with your request, please try again!")
        return redirect('blog-topic')
    
    blog_sections = []

    saved_blog = SavedBlogEdit.objects.get(blog=blog)

    if saved_blog:
        blog_body = saved_blog.body

    else:
        blog_sects = BlogSection.objects.filter(blog=blog)

        for blog_sect in blog_sects:
            blog_sections.append(blog_sect.body)

        blog_body = "\n".join(blog_sections)

        saved_blog = SavedBlogEdit.objects.create(
            title=blog.title,
            body=blog_body,
            blog=blog,
        )
        saved_blog.save()

    context['blog'] = blog
    context['blog_title'] = blog.title
    context['blog_audience'] = blog.audience
    context['uniqueId'] = uniqueId
    context['saved_blog'] = saved_blog
    context['blog_body'] = blog_body

    if request.method == 'POST':
        blog_title = request.POST['blog-title']
        generated_blog_edit = request.POST['generated-blog']

        saved_blog.title = blog_title
        saved_blog.body = generated_blog_edit
        saved_blog.save()

        return redirect('edit-gen-blog', uniqueId)

        # print('new title: {}'.format(blog_title))

    return render(request, 'dashboard/edit-generated-blog.html', context)


@login_required
def gen_social_post(request, postType, uniqueId):
    context = {}

    current_page = 'Generated Social Post From Blog'
    context['current_page'] = current_page

    context['allowance'] = check_count_allowance(request.user.profile)

    try:
        this_blog = Blog.objects.get(uniqueId=uniqueId)
    except:
        messages.error(request, "Something went wrong with your request, please try again!")
        return redirect('blog-topic')
    
    post_type = postType.replace('_', ' ').title()

    if postType == "twitter":
        max_char = 280
    elif postType == "twitter_blue":
        max_char = 10000
    elif postType == "linkedin":
        max_char = 3000
    elif postType == "facebook":
        max_char = 10000

    complete_blogs = []
    tone_of_voices = []

    tones = ToneOfVoice.objects.filter(tone_status=True)

    for tone in tones:
        tone_of_voices.append(tone)

    context['tone_of_voices'] = tone_of_voices
    
    blogs = Blog.objects.filter(profile=request.user.profile)

    for blog in blogs:
        sections = BlogSection.objects.filter(blog=blog)
        if sections.exists():
            # calculate blog words
            # blog_words = 0
            # for section in sections:

            #     blog_words += int(section.word_count)

                # month_word_count += int(section.word_count)
            # blog.word_count = str(blog_words)
            # blog.save()
            complete_blogs.append(blog)
        # else:
        #     empty_blogs.append(blog)
    
    blog_sections = []

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

    context['blog'] = this_blog
    context['blog_keywords'] = this_blog.keywords
    context['blog_audience'] = this_blog.audience
    context['blog_tone'] = this_blog.tone_of_voice
    context['uniqueId'] = uniqueId
    context['saved_blog'] = saved_blog
    context['blog_posts'] = complete_blogs
    context['post_type'] = postType

    if request.method == "POST":

        blog_title = request.POST['blog_title']
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
                social_post = generate_social_post(post_type, post_keywords, post_audience, tone_of_voice, blog_body, max_char, request.user.profile)

                # create database record
                new_post = BlogSocialPost.objects.create(
                    title=this_blog.title,
                    post_type=postType,
                    post=social_post,
                    blog=blog,
                )
                new_post.save()

                add_to_list.is_done=True
                add_to_list.save()
                
                context['new_post'] = new_post

                return redirect('social-media', postType, uniqueId)

            else:
                # we might need to delete all abandoned calls
                pass
            n += 1

    return render(request, 'dashboard/social-media-post.html', context)


@login_required
def view_generated_blog(request, slug):
    context = {}

    current_page = 'Blog Generator'

    context['current_page'] = current_page

    context['allowance'] = check_count_allowance(request.user.profile)

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
def paragraph_writer(request, uniqueId=''):
    context = {}

    tone_of_voices = []

    current_page = 'Paragraph Writer'

    context['current_page'] = current_page

    context['allowance'] = check_count_allowance(request.user.profile)

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
                        )
                        s_paragraph.save()

                        add_to_list.is_done=True
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
def sentence_writer(request, uniqueId=''):
    context = {}

    tone_of_voices = []

    current_page = 'Sentence Writer'

    context['current_page'] = current_page

    context['allowance'] = check_count_allowance(request.user.profile)

    tones = ToneOfVoice.objects.filter(tone_status=True)

    for tone in tones:
        tone_of_voices.append(tone)

    context['tone_of_voices'] = tone_of_voices

    if len(uniqueId) > 0:
        sentence_opts = []
        # search database for sentences with this slug
        sentence_obj = Sentence.objects.get(uniqueId=uniqueId)

        new_sentences = sentence_obj.new_sentence

        a_list = new_sentences.split('*')
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

        # context['paragraph'] = sentence
    else:
        pass

    if request.method == 'POST':
        old_sentence = request.POST['old_sentence']
        tone_of_voice = request.POST['tone_of_voice']
        # request.session['old_sentence'] = old_sentence

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

                    new_sentence = rewrite_sentence(old_sentence, tone_of_voice, request.user.profile)

                    if len(new_sentence) > 0:

                        # create database record
                        s_sentence = Sentence.objects.create(
                            old_sentence=old_sentence,
                            new_sentence=new_sentence,
                            tone_of_voice=tone_of_voice,
                            profile=request.user.profile,
                        )
                        s_sentence.save()

                        add_to_list.is_done=True
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
def article_title_writer(request, uniqueId=''):
    context = {}

    tone_of_voices = []

    current_page = 'Title Writer'

    context['current_page'] = current_page

    context['allowance'] = check_count_allowance(request.user.profile)
    
    tones = ToneOfVoice.objects.filter(tone_status=True)

    for tone in tones:
        tone_of_voices.append(tone)

    context['tone_of_voices'] = tone_of_voices

    if len(uniqueId) > 0:
        title_opts = []
        # search database for titles with this slug
        title_obj = ArticleTitle.objects.get(uniqueId=uniqueId)

        new_titles = title_obj.new_title_options

        a_list = new_titles.split('*')
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

        # context['paragraph'] = title
    else:
        pass

    if request.method == 'POST':
        old_title = request.POST['old_title']
        tone_of_voice = request.POST['tone_of_voice']
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
                        )
                        s_title.save()

                        add_to_list.is_done=True
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
def meta_description_writer(request, uniqueId=''):
    context = {}

    tone_of_voices = []

    current_page = 'Meta Description Generator'

    context['current_page'] = current_page

    context['allowance'] = check_count_allowance(request.user.profile)
        
    tones = ToneOfVoice.objects.filter(tone_status=True)

    for tone in tones:
        tone_of_voices.append(tone)

    context['tone_of_voices'] = tone_of_voices

    if len(uniqueId) > 0:
        # search database for meta descriptions with this slug
        meta_descr = MetaDescription.objects.get(uniqueId=uniqueId)

        context['meta_descr'] = meta_descr
    else:
        pass

    if request.method == 'POST':
        article_title = request.POST['article_title']
        tone_of_voice = request.POST['tone_of_voice']
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
                        )
                        s_meta_descr.save()

                        add_to_list.is_done=True
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
def summarize_content(request, uniqueId=""):
    context = {}

    tone_of_voices = []

    current_page = 'Content Summarizer'

    context['current_page'] = current_page

    context['allowance'] = check_count_allowance(request.user.profile)

    tones = ToneOfVoice.objects.filter(tone_status=True)

    for tone in tones:
        tone_of_voices.append(tone)

    context['tone_of_voices'] = tone_of_voices

    if len(uniqueId) > 0:
        # search database for meta descriptions with this slug
        content_summary = ContentSummary.objects.get(uniqueId=uniqueId)

        context['content_summary'] = content_summary
    else:
        pass

    if request.method == 'POST':
        long_content = request.POST['long_content']
        summary_title = request.POST['summary_title']
        tone_of_voice = request.POST['tone_of_voice']
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
                        )
                        s_content_data.save()

                        add_to_list.is_done=True
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
def landing_page_copy(request, uniqueId=""):
    context = {}

    current_page = 'Landing Page Copy Generator'

    context['current_page'] = current_page

    page_sections = "Header, Subheader, About Us, Call to Action, FAQ, Testimonials"

    context['allowance'] = check_count_allowance(request.user.profile)

    context['page_sections'] = page_sections

    if len(uniqueId) > 0:
        # search database for meta descriptions with this slug
        copy_content = LandingPageCopy.objects.get(uniqueId=uniqueId)

        context['copy_content'] = copy_content
        context['page_sections'] = copy_content.page_sections
    else:
        pass

    if request.method == 'POST':
        company_name = request.POST['company_name']
        copy_title = request.POST['copy_title']
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

                    gen_page_copy = generate_landing_page_copy(company_name, company_purpose, page_sections, request.user.profile)

                    if len(gen_page_copy) > 0:

                        # create database record
                        s_content_data = LandingPageCopy.objects.create(
                            company_name=company_name,
                            company_purpose=company_purpose,
                            copy_title=copy_title,
                            page_sections=page_sections,
                            page_copy=gen_page_copy,
                            profile=request.user.profile,
                        )
                        s_content_data.save()

                        add_to_list.is_done=True
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
def billing(request):
    context = {}

    current_page = 'Billing'

    user_sub_type = request.user.profile.subscription_type.title()

    # get user current tier
    user_curr_tier = SubscriptionPackage.objects.get(package_name=user_sub_type)

    context['current_page'] = current_page
    context['month_word_count'] = request.user.profile.monthly_count
    context['user_curr_tier'] = user_curr_tier

    return render(request, 'dashboard/billing.html', context)


@login_required
def payment_plans(request):
    context = {}
    
    current_page = 'Payment Plans'
    context['current_page'] = current_page

    return render(request, 'dashboard/process-initiator-plan.html', context)


@login_required
def process_initiator_plan(request):

    context = {}

    merchant_id = "10024789"
    merchant_key = "dtz5khr0cbz74"
    return_url = "http://138.68.155.44:8000/dash/billing"
    notify_url = "http://138.68.155.44:8000/dash/payment-success"
    order_id = str(uuid4()).split('-')[4]

    amount = "550.00"
    item_name = "Initiator"
    
    current_page = 'Billing | Initiator'
    context['current_page'] = current_page

    pfData = {
        "merchant_id": merchant_id,
        "merchant_key": merchant_key,
        "return_url": notify_url,
        "notify_url": notify_url,
        # # Buyer details
        "name_first": request.user.first_name,
        "name_last": request.user.last_name,
        "email_address": request.user.email,
        "m_payment_id": order_id,
        "amount": amount,
        "item_name": item_name,
        "item_description": "Initiator subscription",
        # # Subscription details
        "subscription_type": "1",
        "billing_date": "",
        "recurring_amount": amount,
        "frequency": "3",
        "cycles": "0",
        "user_id": request.user.profile.uniqueId
    }

    def generateSignature(dataArray, passPhrase = ''):
        payload = ""
        for key in dataArray:
            # Get all the data from Payfast and prepare parameter string
            payload += key + "=" + urllib.parse.quote_plus(dataArray[key].replace("+", " ")) + "&"
        # After looping through, cut the last & or append your passphrase
        payload = payload[:-1]
        if passPhrase != '':
            payload += f"&passphrase={passPhrase}"
        return hashlib.md5(payload.encode()).hexdigest()

    passPhrase = 'AnotidaL2022'
    signature = generateSignature(pfData, passPhrase)

    context['signature'] = signature
    context['order_id'] = order_id
    context['merchant_id'] = merchant_id
    context['merchant_key'] = merchant_key
    context['return_url'] = return_url
    context['notify_url'] = notify_url
    context['amount'] = amount
    context['item_name'] = item_name
    context['action_url'] = "https://sandbox.payfast.co.za/eng/process"

    return render(request, 'dashboard/process-initiator-plan.html', context)


@require_POST
@csrf_exempt
def webhook(request):
    # verify that the request is from PayPal

    # check the type of webhook event
    #1. subscription created
    #2. subscription got cancelled

    # process the event
    return redirect('billing')


@csrf_exempt
def payment_success(request):

    cartTotal = '550.00'

    context = {}
    SANDBOX_MODE = True

    pfHost = 'sandbox.payfast.co.za' if SANDBOX_MODE else 'www.payfast.co.za'

    # Get posted variables from ITN and convert to a string
    pfData = {}
    postData = request.get_data().decode().split('&')
    for i in range(0,len(postData)):
        splitData = postData[i].split('=')
        pfData[splitData[0]] = splitData[1]

    pfParamString = ""
    for key in pfData:
    # Get all the data from Payfast and prepare parameter string
        if key != 'signature':
            pfParamString += key + "=" + urllib.parse.quote_plus(pfData[key].replace("+", " ")) + "&"
    # After looping through, cut the last & or append your passphrase
    # payload += "passphrase=SecretPassphrase123"
    pfParamString = pfParamString[:-1]

    def pfValidSignature(pfData, pfParamString):
        # Generate our signature from Payfast parameters
        signature = hashlib.md5(pfParamString.encode()).hexdigest()
        return (pfData.get('signature') == signature)
    
    def pfValidIP():
        valid_hosts = [
        'www.payfast.co.za',
        'sandbox.payfast.co.za',
        'w1w.payfast.co.za',
        'w2w.payfast.co.za',
        ]
        valid_ips = []

        for item in valid_hosts:
            ips = socket.gethostbyname_ex(item)
            if ips:
                for ip in ips:
                    if ip:
                        valid_ips.append(ip)
        # Remove duplicates from array
        clean_valid_ips = []
        for item in valid_ips:
            # Iterate through each variable to create one list
            if isinstance(item, list):
                for prop in item:
                    if prop not in clean_valid_ips:
                        clean_valid_ips.append(prop)
            else:
                if item not in clean_valid_ips:
                    clean_valid_ips.append(item)

        # Security Step 3, check if referrer is valid
        if url_parse(request.headers.get("Referer")).host not in clean_valid_ips:
            return False
        else:
            return True
        
    def pfValidPaymentData(cartTotal, pfData):
        return not (abs(float(cartTotal)) - float(pfData.get('amount_gross'))) > 0.01
    
    def pfValidServerConfirmation(pfParamString, pfHost = 'sandbox.payfast.co.za'):
        url = f"https://{pfHost}/eng/query/validate"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
            }
        response = requests.post(url, data=pfParamString, headers=headers)
        return response.text == 'VALID'
    
    check1 = pfValidSignature(pfData, pfParamString)
    check2 = pfValidIP()
    check3 = pfValidPaymentData(cartTotal, pfData)
    check4 = pfValidServerConfirmation(pfParamString, pfHost)

    if(check1 and check2 and check3 and check4):
        # All checks have passed, the payment is successful

        if pfData.get('item_name') == 'Initiator':
            try:
                profile = Profile.objects.get(uniqueId=pfData.get('user_id'))
                profile.subscribed = True
                profile.subscription_type = pfData.get('item_name')
                profile.subscription_reference = request.POST['m_payment_id']
                profile.save()
                return redirect('billing')
            except:
                return redirect('billing')
            
        elif pfData.get('item_name') == 'Teams':
            try:
                profile = Profile.objects.get(uniqueId=pfData.get('user_id'))
                profile.subscribed = True
                profile.subscription_type = pfData.get('item_name')
                profile.subscription_reference = request.POST['m_payment_id']
                profile.save()
                return redirect('billing')
            except:
                return redirect('billing')

        else:
            return redirect('billing')
        
    else:
        # Some checks have failed, check payment manually and log for investigation
        messages.error(request, "Payment verification failed!")
        return redirect('billing')


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

    user_profile = request.user.profile

    if not user_profile.subscription_type == 'teams':
        messages.error(request, "You subscription packages does not have access to this feature!")
        return redirect('billing')

    if user_profile.user_team is not None:

        this_user_team = Team.objects.get(uniqueId=user_profile.user_team)

        context['this_user_team'] = this_user_team
    
        find_team_members = Profile.objects.filter(user_team=this_user_team.uniqueId)

        for team_member in find_team_members:
            total_members +=1
            team_members.append(team_member)

        if request.method == 'GET':
            invite_form = MemberInviteForm(instance=request.user.profile, user=request.user)

            context['invite_form'] = invite_form

            # return render(request, 'dashboard/team-manager.html', context)

    my_invites = MemberInvite.objects.filter(invited_by=request.user.profile.uniqueId, inviter_team=request.user.profile.user_team, invite_accepted=False)
    for member_inv in my_invites:
        member_invites.append(member_inv)

    context['current_page'] = current_page
    context['total_members'] = str(total_members)
    context['team_members'] = team_members
    context['max_members'] = str(max_members)
    context['team_uid'] = user_profile.user_team
    context['total_invites'] = total_invites
    context['member_invites'] = member_invites

    if request.method == 'POST':

        invite_form = MemberInviteForm(request.POST, instance=request.user.profile, user=request.user)

        if invite_form.is_valid():
            invite_email = request.POST['invite_email']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']

            # invite submit form
            new_invite = MemberInvite.objects.create(
                invite_email=invite_email,
                first_name=first_name,
                last_name=last_name,
                invited_by=request.user.profile.uniqueId,
                inviter_team=request.user.profile.user_team,
                invite_code=str(uuid4()).split('-')[4],
            )
            new_invite.save()

            # send invite email

            return redirect('team-manager')

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
                edit_org.business_name=biz_name
                edit_org.business_size=business_size
                edit_org.industry=industry
                edit_org.business_email=biz_email
                edit_org.business_description=biz_description
                edit_org.business_address=biz_address

    return render(request, 'dashboard/team-manager.html', context)


@login_required
def delete_member(request, orgUniqueId, uniqueId):

    get_this_org = Team.objects.get(uniqueId=orgUniqueId)

    try:
        if request.user.profile.user_team == orgUniqueId:

            member = Profile.objects.get(uniqueId=uniqueId)
            
            if member.profile.uniqueId == request.user.profile.uniqueId:
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
    max_devices = 5

    context['current_page'] = current_page

    reg_devices = []

    user_reg_devices = RegisteredDevice.objects.filter(profile=request.user.profile)

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
def memory_blogs(request):
    context = {}

    empty_blogs = []
    complete_blogs = []

    today_date = datetime.datetime.now()

    q_year = today_date.year
    q_month = today_date.month

    # Get total blogs
    blogs = Blog.objects.filter(profile=request.user.profile, date_created__year=q_year, date_created__month=q_month).order_by('last_updated')

    for blog in blogs:
        sections = BlogSection.objects.filter(blog=blog)
        if sections.exists():
            # calculate blog words
            blog_words = 0
            for section in sections:

                blog_words += int(section.word_count)

                # month_word_count += int(section.word_count)
            blog.word_count = str(blog_words)
            blog.save()
            complete_blogs.append(blog)
        else:
            empty_blogs.append(blog)

    context['empty_blogs'] = empty_blogs
    context['complete_blogs'] = complete_blogs

    context['allowance'] = check_count_allowance(request.user.profile)

    current_page = 'Blog Memory'
    context['current_page'] = current_page

    return render(request, 'dashboard/blog-memory.html', context)


@login_required
def memory_summarizer(request):
    context = {}
    
    saved_summaries = []

    today_date = datetime.datetime.now()

    q_year = today_date.year
    q_month = today_date.month

    # Get total summaries
    summaries = ContentSummary.objects.filter(profile=request.user.profile, date_created__year=q_year, date_created__month=q_month)

    for summary in summaries:
        saved_summaries.append(summary)

    context['saved_summaries'] = saved_summaries

    context['allowance'] = check_count_allowance(request.user.profile)

    current_page = 'Summarizer Memory'
    context['current_page'] = current_page

    return render(request, 'dashboard/summarizer-memory.html', context)


@login_required
def memory_page_copy(request):
    context = {}
    
    saved_page_copies = []

    today_date = datetime.datetime.now()

    q_year = today_date.year
    q_month = today_date.month

    # Get total summaries
    page_copies = LandingPageCopy.objects.filter(profile=request.user.profile, date_created__year=q_year, date_created__month=q_month)

    for page_copy in page_copies:
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

    today_date = datetime.datetime.now()

    q_year = today_date.year
    q_month = today_date.month

    # Get total summaries
    meta_descriptions = MetaDescription.objects.filter(profile=request.user.profile, date_created__year=q_year, date_created__month=q_month)

    for meta_description in meta_descriptions:
        saved_meta_descriptions.append(meta_description)

    context['saved_meta_descriptions'] = saved_meta_descriptions

    context['allowance'] = check_count_allowance(request.user.profile)

    current_page = 'Meta Description Memory'
    context['current_page'] = current_page

    return render(request, 'dashboard/meta-description-memory.html', context)


def categories(request):
    context = {}

    current_page = 'Categories'
    context['current_page'] = current_page

    cate_list = []
    client_list = []

    user_profile = request.user.profile

    team_clients = TeamClient.objects.filter(is_activate=True)

    for client in team_clients:
        if client.team == user_profile.user_team:
            client_list.append(client)

    team_categories = ClientCategory.objects.filter(is_activate=True)

    for category in team_categories:
        print("cate team:".format(category.client.team))
        if category.client.team == user_profile.user_team:
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
                client=team_client,
            )
            new_cate.save()
            return redirect('categories')

    return render(request, 'dashboard/categories.html', context)


def clients(request):
    context = {}

    current_page = 'Clients'
    context['current_page'] = current_page

    client_list = []
    user_profile = request.user.profile

    team_clients = TeamClient.objects.filter(is_activate=True)

    for client in team_clients:
        if client.team == user_profile.user_team:
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


def edit_client(request, uniqueId):
    context = {}

    current_page = 'Edit Client'
    context['current_page'] = current_page

    return render(request, 'dashboard/clients.html', context)


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
        client.is_activate=client_status
        client.save()
    else:
        messages.error(request, "Action denied on this client!")
        return redirect('clients')

    return redirect('clients')


def edit_category(request, uniqueId):
    context = {}

    current_page = 'Edit Category'
    context['current_page'] = current_page

    return render(request, 'dashboard/categories.html', context)


def change_category_status(request, status, uniqueId):
    context = {}

    current_page = 'Edit Category'
    context['current_page'] = current_page

    cate_status = False

    if status == 'activate':
        cate_status = True

    user_profile = request.user.profile

    category = ClientCategory.objects.get(uniqueId=uniqueId)

    if category.client.team == user_profile.user_team:
        category.is_activate=cate_status
        category.save()
    else:
        messages.error(request, "Action denied on this category!")
        
        return redirect('categories')

    return redirect('categories')


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
#
