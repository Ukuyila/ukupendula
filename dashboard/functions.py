import datetime
import os
import openai
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import uuid
import socket
import requests
import platform
from math import ceil, floor


from .models import *


# Load your API key from an environment variable or secret management service
openai.api_key = settings.OPENAI_API_KEYS


def generate_blog_topic_ideas(profile, topic, audience, keywords):

    lang = 'English (GB)' if check_user_lang(profile, 'en-gb') == 'en-gb' else 'English (US)'
    blog_topics = []

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Generate 5 blog topic ideas in {} without numbering prefixes about {}\nAudience: {}\nKeywords: {}\n\n*".format(lang, topic, audience, keywords),
        temperature=0.7,
        max_tokens=250,
        top_p=1,
        best_of=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
        else:
            return []
    else:
        return []

    a_list = res.split('*')
    if len(a_list) > 0:
        for blog in a_list:
            blog_topics.append(blog)
    else:
        return []

    return blog_topics


def generate_blog_section_headings(profile, topic, audience, keywords):

    lang = 'English (GB)' if check_user_lang(profile, 'en-gb') == 'en-gb' else 'English (US)'
    blog_sections = []

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Generate Blog Sections in {} for the following blog topic, target audience, and keywords:\nTopic: {}\nAudience: {}\nKeywords: {}\n*".format(lang, topic, audience, keywords),
        temperature=0.7,
        max_tokens=250,
        top_p=1,
        best_of=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
        else:
            return []
    else:
        return []

    a_list = res.split('*')
    if len(a_list) > 0:
        for blog in a_list:
            blog_sections.append(blog)
    else:
        return []

    return blog_sections


def generate_full_blog(blog_topic, section_heads, audience, keywords, tone, min_words, max_words, profile):

    lang = 'English (GB)' if check_user_lang(profile, 'en-gb') == 'en-gb' else 'English (US)'

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Generate a blog write-up in {} with a length between {} and {} words for the following blog title, target audience, tone of voice, and keywords:\nBlog Title: {}\nAudience: {}\nThe tone of voice: {}\nKeywords: {}\nUse the section headings below: \n{}\n*".format(lang, 
            min_words, max_words, blog_topic, audience, tone, keywords, section_heads),
        temperature=1,
        max_tokens=1000,
        top_p=1,
        best_of=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
            if not res == '':
                cleaned_res = res.replace('*', '').replace('\n', '<br>')
                if profile.monthly_count:
                    prof_count = int(profile.monthly_count)
                else:
                    prof_count = 0

                prof_count += len(cleaned_res.split(' '))

                if profile.monthly_memory_count:
                    prof_mmry_count = int(profile.monthly_memory_count)
                else:
                    prof_mmry_count = 0

                prof_mmry_count + 1

                profile.monthly_count = str(prof_count)
                profile.monthly_memory_count = str(prof_mmry_count)
                profile.save()
                return cleaned_res
            else:
                return ''
        else:
            return ''
    else:
        return ''


def generate_blog_section_details(blog_topic, section_topic, audience, keywords, profile):

    lang = 'English (GB)' if check_user_lang(profile, 'en-gb') == 'en-gb' else 'English (US)'

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Generate a detailed blog section write-up in {} for the following blog section heading, using the blog title, target audience, and keywords:\nBlog Title: {}\nSection Heading: {}\nAudience: {}\nKeywords: {}\n*".format(lang, 
            blog_topic, section_topic, audience, keywords),
        temperature=1,
        max_tokens=1000,
        top_p=1,
        best_of=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
            if not res == '':
                cleaned_res = res.replace('\n', '<br>')
                if profile.monthly_count:
                    prof_count = int(profile.monthly_count)
                else:
                    prof_count = 0

                prof_count += len(cleaned_res.split(' '))

                if profile.monthly_memory_count:
                    prof_mmry_count = int(profile.monthly_memory_count)
                else:
                    prof_mmry_count = 0

                prof_mmry_count + 1

                profile.monthly_count = str(prof_count)
                profile.monthly_memory_count = str(prof_mmry_count)
                profile.save()
                return cleaned_res
            else:
                return ''
        else:
            return ''
    else:
        return ''
    

def gen_improve_content(old_content, min_words, max_words, content_keywords, tone_of_voice, profile):
    lang = 'English (GB)' if check_user_lang(profile, 'en-gb') == 'en-gb' else 'English (US)'

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Improve this content with a lenght between {} and {} words in {}, using given keywords and tone of voice:\nContent: {}\Keywords: {}\nTone of voice: {}\n\n".format(min_words, max_words, lang, old_content, content_keywords, tone_of_voice),
        temperature=1,
        max_tokens=1000,
        top_p=1,
        best_of=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
            if not res == '':
                cleaned_res = res.replace('\n', '<br>')
                if profile.monthly_count:
                    prof_count = int(profile.monthly_count)
                else:
                    prof_count = 0

                prof_count += len(cleaned_res.split(' '))

                if profile.monthly_memory_count:
                    prof_mmry_count = int(profile.monthly_memory_count)
                else:
                    prof_mmry_count = 0

                prof_mmry_count + 1

                profile.monthly_count = str(prof_count)
                profile.monthly_memory_count = str(prof_mmry_count)
                profile.save()

                return cleaned_res
            else:
                return ''
        else:
            return ''
    else:
        return ''
    

def generate_paragraph(paragraph_topic, tone_of_voice, profile):
    lang = 'English (GB)' if check_user_lang(profile, 'en-gb') == 'en-gb' else 'English (US)'

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Write a short paragraph in {} on the given topic and tone of voice:\nTopic: {}\nTone of voice: {}\n".format(lang, 
            paragraph_topic, tone_of_voice),
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        best_of=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
            if not res == '':
                cleaned_res = res.replace('\n', '<br>')
                if profile.monthly_count:
                    prof_count = int(profile.monthly_count)
                else:
                    prof_count = 0

                prof_count += len(cleaned_res.split(' '))

                if profile.monthly_memory_count:
                    prof_mmry_count = int(profile.monthly_memory_count)
                else:
                    prof_mmry_count = 0

                prof_mmry_count + 1

                profile.monthly_count = str(prof_count)
                profile.monthly_memory_count = str(prof_mmry_count)
                profile.save()
                return cleaned_res
            else:
                return ''
        else:
            return ''
    else:
        return ''


def generate_social_post(post_type, keywords, audience, tone_of_voice, prompt_text, max_char, profile, for_blog=True):
    lang = 'English (GB)' if check_user_lang(profile, 'en-gb') == 'en-gb' else 'English (US)'

    ptt = 'article' if for_blog else 'topic'

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Write a {} post in {} with a maximum of {} characters on this {} using these keywords, tone of voice and target audience:\nKeywords: {}\nTone of Voice: {}\nTarget Audience: {}\n{}:\n{}\n\n*".format(post_type, lang, max_char, ptt, keywords, tone_of_voice, audience, ptt.title(), prompt_text),
        temperature=1,
        max_tokens=256,
        top_p=1,
        best_of=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']

            cleaned_res = res.replace('*', '').replace('\n', '<br>')
            if profile.monthly_count:
                prof_count = int(profile.monthly_count)
            else:
                prof_count = 0

            prof_count += len(cleaned_res.split(' '))

            if profile.monthly_memory_count:
                prof_mmry_count = int(profile.monthly_memory_count)
            else:
                prof_mmry_count = 0

            prof_mmry_count + 1

            profile.monthly_count = str(prof_count)
            profile.monthly_memory_count = str(prof_mmry_count)
            profile.save()
            return cleaned_res
        else:
            return []
    else:
        return []


def rewrite_sentence(old_sentence, tone_of_voice, profile):
    lang = 'English (GB)' if check_user_lang(profile, 'en-gb') == 'en-gb' else 'English (US)'

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Give me an unnumbered list of 5 rewrite options in {} for this sentence: {}\nTone of voice: {}\n\n*".format(lang, old_sentence, tone_of_voice),
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        best_of=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']

            cleaned_res = res.replace('*', '').replace('\n', '<br>')
            if profile.monthly_count:
                prof_count = int(profile.monthly_count)
            else:
                prof_count = 0

            prof_count += len(cleaned_res.split(' '))

            if profile.monthly_memory_count:
                prof_mmry_count = int(profile.monthly_memory_count)
            else:
                prof_mmry_count = 0

            prof_mmry_count + 1

            profile.monthly_count = str(prof_count)
            profile.monthly_memory_count = str(prof_mmry_count)
            profile.save()
            return cleaned_res
        else:
            return []
    else:
        return []


def rewriter_article_title(old_title, tone_of_voice, profile):
    lang = 'English (GB)' if check_user_lang(profile, 'en-gb') == 'en-gb' else 'English (US)'

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Give me 5 rewrite options in {} for this article title: {}\nTone of voice: {}\n\n*".format(lang, old_title, tone_of_voice),
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        best_of=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']

            cleaned_res = res.replace('*', '').replace('\n', '<br>')
            if profile.monthly_count:
                prof_count = int(profile.monthly_count)
            else:
                prof_count = 0

            prof_count += len(cleaned_res.split(' '))

            if profile.monthly_memory_count:
                prof_mmry_count = int(profile.monthly_memory_count)
            else:
                prof_mmry_count = 0

            prof_mmry_count + 1

            profile.monthly_count = str(prof_count)
            profile.monthly_memory_count = str(prof_mmry_count)
            profile.save()
            return cleaned_res
        else:
            return []
    else:
        return []
    

def generate_meta_description(article_title, tone_of_voice, profile):
    lang = 'English (GB)' if check_user_lang(profile, 'en-gb') == 'en-gb' else 'English (US)'

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Write an article meta description with a maximum of 160 characters on this article title in {} using given tone of voice:\nTitle: {}\nTone of voice: {}\n\n".format(
            lang, article_title, tone_of_voice),
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        best_of=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
            if not res == '':
                cleaned_res = res.replace('\n', '<br>')
                if profile.monthly_count:
                    prof_count = int(profile.monthly_count)
                else:
                    prof_count = 0

                prof_count += len(cleaned_res.split(' '))

                if profile.monthly_memory_count:
                    prof_mmry_count = int(profile.monthly_memory_count)
                else:
                    prof_mmry_count = 0

                prof_mmry_count + 1

                profile.monthly_count = str(prof_count)
                profile.monthly_memory_count = str(prof_mmry_count)
                profile.save()
                return cleaned_res
            else:
                return ''
        else:
            return ''
    else:
        return ''
    

def write_content_summary(article_title, tone_of_voice, profile):
    lang = 'English (GB)' if check_user_lang(profile, 'en-gb') == 'en-gb' else 'English (US)'

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Write a {} summary in {} for this content;\n{}\n\nSummary:\n".format(tone_of_voice, lang, article_title),
        temperature=0.8,
        max_tokens=1000,
        top_p=1,
        best_of=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
            if not res == '':
                cleaned_res = res.replace('\n', '<br>')
                if profile.monthly_count:
                    prof_count = int(profile.monthly_count)
                else:
                    prof_count = 0

                prof_count += len(cleaned_res.split(' '))

                if profile.monthly_memory_count:
                    prof_mmry_count = int(profile.monthly_memory_count)
                else:
                    prof_mmry_count = 0

                prof_mmry_count + 1

                profile.monthly_count = str(prof_count)
                profile.monthly_memory_count = str(prof_mmry_count)
                profile.save()
                return cleaned_res
            else:
                return ''
        else:
            return ''
    else:
        return ''
    

def generate_landing_page_copy(company_name, company_purpose, page_sections, profile):
    lang = 'English (GB)' if check_user_lang(profile, 'en-gb') == 'en-gb' else 'English (US)'

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Generate a website landing page copy in {} for the given company name and company purpose, and sections below:\nCompany Name: {}\nCompany Purpose: {}\nSection: {}\n\n".format(lang, 
            company_name, company_purpose, page_sections),
        temperature=0.7,
        max_tokens=1000,
        top_p=1,
        best_of=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    if 'choices' in response:
        if len(response['choices']) > 0:
            res = response['choices'][0]['text']
            if not res == '':
                cleaned_res = res.replace('\n', '<br>')
                if profile.monthly_count:
                    prof_count = int(profile.monthly_count)
                else:
                    prof_count = 0

                prof_count += len(cleaned_res.split(' '))

                if profile.monthly_memory_count:
                    prof_mmry_count = int(profile.monthly_memory_count)
                else:
                    prof_mmry_count = 0

                prof_mmry_count + 1

                profile.monthly_count = str(prof_count)
                profile.monthly_memory_count = str(prof_mmry_count)
                profile.save()
                return cleaned_res
            else:
                return ''
        else:
            return ''
    else:
        return ''
    

def check_count_memories(profile):
    memory_cnt = 0
    if profile.monthly_memory_count:
        memory_cnt = int(profile.monthly_memory_count)

    return memory_cnt


def package_memory_limit(profile):
    # zero means NONE
    max_memory = 0
    num_of_gen = 10
    if profile.subscribed:
        profile_package = profile.subscription_reference.split('-')[1]
        user_package = SubscriptionPackage.objects.get(uniqueId=profile_package)
        # divide by the number of content generators
        max_memory = round(int(user_package.package_max_memory)/num_of_gen)
    
    return max_memory


def max_devices(profile):
    max_devices = 1
    if profile.subscribed:
        profile_package = profile.subscription_reference.split('-')[1]
        user_package = SubscriptionPackage.objects.get(uniqueId=profile_package)

        max_devices = int(user_package.package_max_device)

    return max_devices


def check_count_allowance(profile):

    # max_devices = 1
    if profile.subscribed:
        profile_package = profile.subscription_reference.split('-')[1]
        user_package = SubscriptionPackage.objects.get(uniqueId=profile_package)

        max_limit = int(user_package.package_max_word)
        print('max_limit: {}'.format(max_limit))
        if profile.monthly_count:
            if int(profile.monthly_count) < max_limit:
                return True
            else:
                return False
        else:
            return True

    # if profile.subscribed:

    #     sub_type = profile.subscription_type
    #     if sub_type == 'free':
    #         max_limit = 5000
    #         if profile.monthly_count:
    #             if int(profile.monthly_count) < max_limit:
    #                 return True
    #             else:
    #                 return False
    #         else:
    #             return True
    #     elif sub_type == 'initiator':
    #         max_limit = 40000
    #         if profile.monthly_count:
    #             if int(profile.monthly_count) < max_limit:
    #                 return True
    #             else:
    #                 return False

    #         else:
    #             return True
    #     elif sub_type == 'teams':
    #         return True
    #     else:
    #         return False
    else:
        max_limit = 5000
        if profile.monthly_count:
            if int(profile.monthly_count) < max_limit:
                return True
            else:
                return False

        else:
            return True


def get_blog_word_cnt(q_year, q_month, profile):
    blog_word_cnt = 0

    blogs = Blog.objects.filter(profile=profile, date_created__year=q_year, date_created__month=q_month)

    for blog in blogs:
        sections = BlogSection.objects.filter(blog=blog)
        if sections.exists():
            # calculate blog words
            blog_words = 0
            for section in sections:

                blog_words += int(section.word_count)

                blog_word_cnt += int(section.word_count)
                
    return blog_word_cnt


def get_para_word_cnt(q_year, q_month, profile):
    para_word_cnt = 0

    paragraphs = Paragraph.objects.filter(profile=profile, date_created__year=q_year, date_created__month=q_month)

    for para in paragraphs:

        res = para.paragraph

        if not res == '':
            cleaned_res = res.replace('\n', '<br>')
            para_word_cnt += len(cleaned_res.split(' '))
                
    return para_word_cnt


def get_sentence_word_cnt(q_year, q_month, profile):
    sentence_word_cnt = 0

    sentences = Sentence.objects.filter(profile=profile, date_created__year=q_year, date_created__month=q_month)

    for sentence in sentences:

        res = sentence.new_sentence

        if not res == '':
            cleaned_res = res.replace('\n', '<br>')
            sentence_word_cnt += len(cleaned_res.split(' '))
                
    return sentence_word_cnt


def get_meta_word_cnt(q_year, q_month, profile):
    meta_word_cnt = 0

    meta_descrps = MetaDescription.objects.filter(profile=profile, date_created__year=q_year, date_created__month=q_month)

    for meta_descrp in meta_descrps:

        res = meta_descrp.meta_description

        if not res == '':
            cleaned_res = res.replace('\n', '<br>')
            meta_word_cnt += len(cleaned_res.split(' '))
                
    return meta_word_cnt


def get_summarizer_word_cnt(q_year, q_month, profile):
    summary_word_cnt = 0

    summaries = ContentSummary.objects.filter(profile=profile, date_created__year=q_year, date_created__month=q_month)

    for summary in summaries:

        res = summary.summarized

        if not res == '':
            cleaned_res = res.replace('\n', '<br>')
            summary_word_cnt += len(cleaned_res.split(' '))
                
    return summary_word_cnt


def get_land_copy_word_cnt(q_year, q_month, profile):
    land_copy_word_cnt = 0

    land_copys = LandingPageCopy.objects.filter(profile=profile, date_created__year=q_year, date_created__month=q_month)

    for land_copy in land_copys:

        res = land_copy.page_copy

        if not res == '':
            cleaned_res = res.replace('\n', '<br>')
            land_copy_word_cnt += len(cleaned_res.split(' '))
                
    return land_copy_word_cnt


def get_percent_of(num_a, num_b):
    if int(num_a) > 0:
        percent = (int(num_a) / int(num_b)) * 100
    else:
        percent = 0
    return round_to_multiple(percent, 5)


def round_to_multiple(number, multiple, direction='nearest'):
    if direction == 'nearest':
        return multiple * round(number / multiple)
    elif direction == 'up':
        return multiple * ceil(number / multiple)
    elif direction == 'down':
        return multiple * floor(number / multiple)
    else:
        return multiple * round(number / multiple)


def get_subscription_details(profile):
    sub_id = profile.subscription_reference


def get_device_mac():

    device_mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
    for ele in range(0,8*6,8)][::-1])

    return device_mac


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device_info(request):

    # hostname = socket.gethostname()
    # ip_address = socket.gethostbyname(hostname)

    # NOTE: this device name is giving us the virtual machine name when in development
    device_name = platform.node()

    # remote_addr = requests.get('https://checkip.amazonaws.com').text.strip()
    remote_addr = get_client_ip(request)

    agent = request.user_agent
    agent_browser = '{} {}'.format(agent.browser.family, agent.browser.version_string)
    agent_os = '{} {}'.format(agent.os.family, agent.os.version_string)

    agent_type = 'unknown'
    if agent.is_mobile:
        agent_type = 'mobile'
    elif agent.is_tablet:
        agent_type = 'tablet'
    elif agent.is_pc:
        agent_type = 'pc'
    elif agent.is_bot:
        agent_type = 'bot'

    mac_address = get_device_mac()

    device_info = {'device_name':device_name, 'ip_address':remote_addr, 'mac_address':mac_address, 'agent_browser':agent_browser, 'agent_os':agent_os, 'agent_type':agent_type}

    return device_info


def datetime_difference(date_a, date_b):
    # returns a timedelta object
    diff = date_a-date_b
    # print('Difference: ', diff)

    # Total difference in seconds
    return diff.total_seconds()

def device_registration(request, max_devices_allow):
    user_profile = request.user.profile
    cnt_devices = 0
    device_info = get_device_info(request)
    # DEVICE REGISTRATION
    # check if device already exists
    # print('device_name: {}'.format(device_info['device_info']))
    # for key, value in device_info.items():
    #     print('{} => {}'.format(key, value))
    try:
        get_user_device = RegisteredDevice.objects.get(ip_address=device_info['ip_address'],agent_os=device_info['agent_os'],mac_address=device_info['mac_address'],profile=user_profile)
        get_user_device.date_created = timezone.localtime(timezone.now())
        # print('get_curr_device_name: {}'.format(get_user_curr_device.device_name))
        return get_user_device.uniqueId
    except:
        try:
            get_curr_device = RegisteredDevice.objects.get(uniqueId=user_profile.current_device)
            # print('get_curr_device_name: {}'.format(get_user_curr_device.device_name))

            # user current device INFO matched the registered device
            if get_curr_device.ip_address == device_info['ip_address'] and get_curr_device.agent_os == device_info['agent_os'] and get_curr_device.mac_address == device_info['mac_address']:
                get_curr_device.date_created = timezone.localtime(timezone.now())
                # print('get_curr_device_name: {}'.format(get_user_curr_device.device_name))
                return get_curr_device.uniqueId

        except:
            # search if the user has other devices in the profile
            user_reg_devices = RegisteredDevice.objects.filter(profile=user_profile)

            for user_device in user_reg_devices:

                # First we obtain de timezone info of last updated datatime variable
                tz_info = user_device.last_updated.tzinfo

                current_date = datetime.datetime.now(tz_info)
                
                # check last seen
                if (datetime_difference(user_device.last_updated, current_date) * 60 * 60) > 7:
                    # and if last seen is more than 7 hours delete device
                    RegisteredDevice.objects.get(uniqueId=user_device.uniqueId).delete()
                else:
                    cnt_devices += 1

                # check if user has this device registered already
                if user_device.ip_address == device_info['ip_address'] and user_device.agent_os == device_info['agent_os'] and user_device.mac_address == device_info['mac_address']:
                    # update user current_device and ip_address on profile
                    # Login user
                    logged_device = RegisteredDevice.objects.get(profile=user_profile, mac_address=user_device.mac_address)
                    logged_device.device_name = device_info['device_name']
                    logged_device.ip_address = device_info['ip_address']
                    logged_device.agent_browser = device_info['agent_browser']
                    logged_device.agent_os=device_info['agent_os']
                    logged_device.is_logged_in = True
                    logged_device.save()

                    print('device_name: {}'.format(device_info['device_name']))

                    return logged_device.uniqueId
                
            # if user has maxed logged in devices
            if cnt_devices >= max_devices_allow:
                # display error and ask for user to login using one of registered device and remove
                # post error message
                return 'error: max device'

            else:
                # if user has no device registered or user still has space for another device, register this device in database
                logged_device = RegisteredDevice.objects.create(
                    device_name=device_info['device_name'],
                    ip_address=device_info['ip_address'],
                    mac_address=device_info['mac_address'],
                    agent_browser=device_info['agent_browser'],
                    agent_os=device_info['agent_os'],
                    agent_type=device_info['agent_type'],
                    profile=request.user.profile,
                )
                logged_device.save()

                return logged_device.uniqueId
    

def save_section_head(blog_unique_id, section_head):
    response = {}

    blog = Blog.objects.get(uniqueId=blog_unique_id)

    if blog:
        saved_sect_head = SavedBlogSectionHead.objects.create(
            section_head=section_head,
            blog=blog,
        )
        saved_sect_head.save()

        # blog_section_heads = request.session['blog-sections']
        response['uniqueId'] = blog.uniqueId
        # adding the sections to the context
        response['saved_sect_head'] = saved_sect_head
        # response['blog_sections'] = blog_section_heads
        print("saved: ".format(section_head))
        return response
    else:
        return response
    

# Django backend check every 5 seconds
def check_api_requests():
    cnt_requests = 0
    result = []
    # Check the queue for any pending calls
    ai_requests_queue = RequestsQueue.objects.filter(is_done=False).order_by('date_created')[:1]
    for ai_request in ai_requests_queue:
        tz_info = ai_request.last_updated.tzinfo

        current_date = datetime.datetime.now(tz_info)
        # if the request has been here for more than 10 minutes without being executed, delete it and start over
        if (datetime_difference(ai_request.last_updated, current_date) * 60) > 10:
            ai_request.delete()
        else:
            cnt_requests += 1
            result.append(ai_request)    

    return result


def remove_api_requests(profile):
    cnt_req = 0
    user_requests = RequestsQueue.objects.filter(profile=profile)
    if user_requests:
        for u_req in user_requests:
            if not u_req.is_done:
                u_req.is_done=True
                u_req.save()
                u_req.delete()

                cnt_req+=1
            
    return cnt_req


# add new call to the list
def add_to_api_requests(request_type, call_code, profile):
    # first delete all user requests
    user_requests = RequestsQueue.objects.filter(profile=profile)
    if user_requests:
        for u_req in user_requests:
            if not u_req.is_done:
                u_req.is_done=True
                u_req.save()
                u_req.delete()

    # add new request
    add_to_queue = RequestsQueue.objects.create(
        request_type=request_type,
        call_code=call_code,
        profile=profile,
    )
    add_to_queue.save()
    return add_to_queue


def api_call_process(api_call_code, add_to_list):
    api_requests = check_api_requests()
    if len(api_requests) > 0:
        for api_req in api_requests:
            if api_req.call_code == api_call_code:
                print("process this call: {}".format(api_req.call_code))
                return True
            else:
                print("not this: {}".format(api_call_code))
                return False
    else:
        print("new call: {}".format(add_to_list.call_code))
        return True
        # blog_topics = generate_blog_topic_ideas(blog_idea, audience, keywords)
        # if len(blog_topics) > 0:

        #     add_to_list.is_done=True
        #     add_to_list.save()

        #     request.session['blog_topics'] = blog_topics
        #     return redirect('blog-sections')
        # else:
        #     messages.error(request, "The engine could not generate blog ideas, please try again!")
        #     return redirect('blog-topic')


def check_user_lang(profile, lang):
    try:
        user_settings = UserSetting.objects.get(profile=profile)
    except:
        user_settings = UserSetting.objects.create(lang=lang, profile=profile)
        user_settings.save()

    if user_settings.lang is not None:
        lang = user_settings.lang
        # print('Language: {}'.format(user_settings.lang))

    return lang


def populate_defaults():
    # populate default ToneOfVoice
    tones = [
        'Funny', 'Casual', 'Excited', 'Professional', 'Witty', 'Friendly', 'Sarcastic',
        'Expressive', 'Direct', 'Playful', 'Feminine', 'Masculine', 'Bold', 'Uplifting',
        'Dramatic', 'Grumpy', 'Motivating', 'Secretive', 'Sophisticated','Positive',
        'Confident', 'Educational'
    ]

    perm_lvls = [
        'Manager', 'Administrator', 'Editor', 'Assistant', 'Author', 'Reader'
    ]

    for perm in perm_lvls:
        try:
            perm_exist = PermissionLevel.objects.get(permission_name=perm)
            if perm_exist:
                pass
        except:
            PermissionLevel.objects.create(permission_name=perm)

    for tone in tones:
        try:
            tone_exist = ToneOfVoice.objects.get(tone_of_voice=tone)
        except:
            ToneOfVoice.objects.create(tone_of_voice=tone)


def validateEmail( email ):

    try:
        validate_email( email )
        return True
    except ValidationError:
        return False

#
