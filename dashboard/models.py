from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.utils import timezone
from uuid import uuid4
from django_resized import ResizedImageField


# My models
class Profile(models.Model):
    SUBSCRIPTION_OPTIONS = [
        ('free', 'Free'),
        ('initiator', 'Initiator'),
        ('teams', 'Teams'),
    ]
    # Standard Variables
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address_line1 = models.CharField(null=True, blank=True, max_length=100)
    address_line2 = models.CharField(null=True, blank=True, max_length=100)
    city = models.CharField(null=True, blank=True, max_length=60)
    province = models.CharField(null=True, blank=True, max_length=100)
    country = models.CharField(null=True, blank=True, max_length=100)
    postal_code = models.CharField(null=True, blank=True, max_length=5)
    profile_image = ResizedImageField(null=True, blank=True, size=[200, 200], quality=90, upload_to='profile_images')

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    # subscription helpers
    monthly_count = models.CharField(null=True, blank=True, max_length=100)
    subscribed = models.BooleanField(default=False)
    subscription_type = models.CharField(choices=SUBSCRIPTION_OPTIONS, default='free', max_length=100)
    subscription_reference = models.CharField(null=True, blank=True, max_length=500)

    # device
    current_ip = models.CharField(null=True, blank=True, max_length=100)
    current_device = models.CharField(null=True, blank=True, max_length=100)

    # team
    user_team = models.CharField(null=True, blank=True, max_length=100)
    
    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {} {}'.format(self.user.first_name, self.user.last_name, self.user.email)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {} {}'.format(self.user.first_name, self.user.last_name, self.user.email))
        self.last_updated = timezone.localtime(timezone.now())
        super(Profile, self).save(*args, **kwargs)


class PermissionLevel(models.Model):
    permission_name = models.CharField(max_length=255)
    abbreviation = models.CharField(null=True, blank=True, max_length=60)
    is_active = models.BooleanField(default=True)
    
    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.permission_name, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.permission_name, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(PermissionLevel, self).save(*args, **kwargs)


class UserRole(models.Model):
    role_name = models.CharField(max_length=255)
    abbreviation = models.CharField(null=True, blank=True, max_length=60)
    permission = models.ForeignKey(PermissionLevel, on_delete=models.CASCADE)
    # team
    user_team = models.CharField(null=True, blank=True, max_length=100)
    # generator
    can_write = models.BooleanField(default=True)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    # teams
    can_create_team = models.BooleanField(default=False)
    can_edit_team = models.BooleanField(default=False)
    can_delete_team = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    
    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.role_name, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.role_name, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(UserRole, self).save(*args, **kwargs)


class UserSetting(models.Model):
    facebook_link = models.CharField(null=True, blank=True, max_length=255)
    twitter_link = models.CharField(null=True, blank=True, max_length=255)
    instagram_link = models.CharField(null=True, blank=True, max_length=255)
    linkedin_link = models.CharField(null=True, blank=True, max_length=255)
    website_link = models.CharField(null=True, blank=True, max_length=255)
    lang = models.CharField(null=True, blank=True, max_length=100, default='en-gb')

    email_verification = models.CharField(null=True, blank=True, max_length=255)

    email_notify = models.BooleanField(default=True)
    multiple_email_notify = models.BooleanField(default=True)

    # django related field
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    user_role = models.ForeignKey(UserRole, on_delete=models.PROTECT)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.profile.user.email, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.profile.user.email, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(UserSetting, self).save(*args, **kwargs)


class RegisteredDevice(models.Model):
    device_name = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=255)
    mac_address = models.CharField(max_length=255)
    agent_browser = models.CharField(blank=True, null=True, max_length=255)
    agent_os = models.CharField(blank=True, null=True, max_length=255)
    agent_type = models.CharField(blank=True, null=True, max_length=255)
    is_logged_in = models.BooleanField(default=True)

    # django related field
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.device_name, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.device_name, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(RegisteredDevice, self).save(*args, **kwargs)


class Team(models.Model):
    business_name = models.CharField(max_length=255)
    business_size = models.CharField(null=True, blank=True, max_length=100)
    industry = models.CharField(null=True, blank=True, max_length=255)
    business_email = models.CharField(null=True, blank=True, max_length=255)
    business_description = models.TextField(null=True, blank=True)
    business_address = models.TextField(null=True, blank=True)
    business_status = models.BooleanField(default=True)

    is_active = models.BooleanField(default=False)

    team_principal = models.CharField(null=True, blank=True, max_length=100)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.business_name, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.business_name, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(Team, self).save(*args, **kwargs)


class MemberInvite(models.Model):
    invite_email = models.CharField(max_length=255)
    first_name = models.CharField(null=True, blank=True, max_length=100)
    last_name = models.CharField(null=True, blank=True, max_length=100)

    # inviter team
    invited_by = models.CharField(null=True, blank=True, max_length=100)
    inviter_team = models.CharField(null=True, blank=True, max_length=100)

    invite_code = models.CharField(null=True, blank=True, max_length=255)
    invite_accepted = models.BooleanField(default=False)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.invite_email, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.invite_email, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(MemberInvite, self).save(*args, **kwargs)


class Blog(models.Model):
    title = models.CharField(max_length=255)
    blog_idea = models.CharField(null=True, blank=True, max_length=255)
    keywords = models.CharField(null=True, blank=True, max_length=255)
    audience = models.CharField(null=True, blank=True, max_length=255)
    word_count = models.CharField(null=True, blank=True, max_length=100)

    tone_of_voice = models.CharField(null=True, blank=True, max_length=255)
    max_words = models.CharField(default="1500", max_length=11)

    category = models.CharField(null=True, blank=True, max_length=255)

    deleted = models.BooleanField(default=False)

    # django related field
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.title, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.title, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(Blog, self).save(*args, **kwargs)


class SavedBlogSectionHead(models.Model):
    section_head = models.CharField(max_length=300)
    section_body = models.TextField(null=True, blank=True)

    # Django related field
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.section_head, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.section_head, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(SavedBlogSectionHead, self).save(*args, **kwargs)


class SavedBlogEdit(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField(null=True, blank=True)

    word_count = models.CharField(null=True, blank=True, max_length=100)

    # Django related field
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    category = models.CharField(null=True, blank=True, max_length=255)
    deleted = models.BooleanField(default=False)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.title, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.title, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        # count the words
        if self.body:
            x = len(self.body.split(' '))
            self.word_count = str(x)
        super(SavedBlogEdit, self).save(*args, **kwargs)


class BlogSection(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField(null=True, blank=True)

    word_count = models.CharField(null=True, blank=True, max_length=100)

    # Django related field
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.title, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.title, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        # count the words
        if self.body:
            x = len(self.body.split(' '))
            self.word_count = str(x)
        super(BlogSection, self).save(*args, **kwargs)


class SocialPost(models.Model):
    title = models.CharField(max_length=500)
    post_type = models.CharField(null=True, blank=True, max_length=255)
    tone_of_voice = models.CharField(null=True, blank=True, max_length=255)
    keywords = models.CharField(null=True, blank=True, max_length=255)
    audience = models.CharField(null=True, blank=True, max_length=255)
    post_idea = models.TextField(null=True, blank=True)
    post = models.TextField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    word_count = models.CharField(null=True, blank=True, max_length=100)

    category = models.CharField(null=True, blank=True, max_length=255)
    # Django related field
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.title, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.title, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        # count the words
        if self.post:
            x = len(self.post.split(' '))
            self.word_count = str(x)
        super(SocialPost, self).save(*args, **kwargs)


class SocialPlatform(models.Model):
    platform = models.CharField(max_length=255)
    post_name = models.CharField(null=True, blank=True, max_length=255)
    url_link = models.CharField(null=True, blank=True, max_length=255)
    max_char = models.CharField(null=True, blank=True, max_length=12)
    
    is_active = models.BooleanField(default=False)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.platform, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.platform, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())

        super(SocialPlatform, self).save(*args, **kwargs)

class BlogSocialPost(models.Model):
    title = models.CharField(max_length=255)
    post_type = models.CharField(null=True, blank=True, max_length=255)
    tone_of_voice = models.CharField(null=True, blank=True, max_length=255)
    keywords = models.CharField(null=True, blank=True, max_length=255)
    audience = models.CharField(null=True, blank=True, max_length=255)
    post = models.TextField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    word_count = models.CharField(null=True, blank=True, max_length=100)

    # Django related field
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.title, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.title, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        # count the words
        if self.post:
            x = len(self.post.split(' '))
            self.word_count = str(x)
        super(BlogSocialPost, self).save(*args, **kwargs)


class ContentImprover(models.Model):
    content_title = models.CharField(max_length=300)
    tone_of_voice = models.CharField(max_length=255)
    content_body_old = models.TextField(null=True, blank=True)
    content_keywords = models.TextField(null=True, blank=True)
    content_body_new = models.TextField(null=True, blank=True)

    deleted = models.BooleanField(default=False)

    # django related field
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    category = models.CharField(null=True, blank=True, max_length=255)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.content_title, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.content_title, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(ContentImprover, self).save(*args, **kwargs)


class Paragraph(models.Model):
    paragraph_topic = models.TextField(null=False)
    tone_of_voice = models.CharField(max_length=255)
    paragraph = models.TextField(null=True, blank=True)

    deleted = models.BooleanField(default=False)

    # django related field
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    category = models.CharField(null=True, blank=True, max_length=255)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.paragraph_topic, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.paragraph_topic, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(Paragraph, self).save(*args, **kwargs)


class Sentence(models.Model):
    old_sentence = models.CharField(max_length=255)
    tone_of_voice = models.CharField(null=True, blank=True, max_length=160)
    new_sentence = models.TextField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    # django related field
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    category = models.CharField(null=True, blank=True, max_length=255)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.old_sentence, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.old_sentence, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(Sentence, self).save(*args, **kwargs)


class ArticleTitle(models.Model):
    old_title = models.CharField(max_length=255)
    tone_of_voice = models.CharField(null=True, blank=True, max_length=160)
    new_title_options = models.TextField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    # django related field
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    category = models.CharField(null=True, blank=True, max_length=255)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.old_title, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.old_title, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(ArticleTitle, self).save(*args, **kwargs)


class MetaDescription(models.Model):
    article_title = models.CharField(max_length=255)
    tone_of_voice = models.CharField(null=True, blank=True, max_length=160)
    meta_description = models.TextField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    # django related field
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    category = models.CharField(null=True, blank=True, max_length=255)
    blog_id = models.CharField(max_length=100, blank=True, null=True)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.article_title, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.article_title, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(MetaDescription, self).save(*args, **kwargs)


class ContentSummary(models.Model):
    long_content = models.TextField(null=False, blank=False)
    summary_title = models.CharField(null=True, blank=True, max_length=200)
    tone_of_voice = models.CharField(null=True, blank=True, max_length=160)
    summarized = models.TextField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    # django related field
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    category = models.CharField(null=True, blank=True, max_length=255)
    blog_id = models.CharField(null=True, blank=True, max_length=100)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        # shortening the long prompt
        old_content_prefix = ' '.join(self.long_content.split()[:5])
        return '{} {}'.format(old_content_prefix, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        old_content_prefix = ' '.join(self.long_content.split()[:5])

        self.slug = slugify('{} {}'.format(old_content_prefix, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(ContentSummary, self).save(*args, **kwargs)


class LandingPageCopy(models.Model):
    company_name = models.CharField(max_length=200)
    company_purpose = models.CharField(null=True, blank=True, max_length=200)
    copy_title = models.CharField(null=True, blank=True, max_length=200)
    page_sections = models.CharField(null=True, blank=True, max_length=200)
    page_copy = models.TextField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    # django related field
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    category = models.CharField(null=True, blank=True, max_length=255)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.company_name, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.company_name, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(LandingPageCopy, self).save(*args, **kwargs)


class RequestsQueue(models.Model):
    request_type = models.CharField(max_length=200)
    call_code = models.CharField(max_length=200)
    is_done = models.BooleanField(default=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.request_type, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.request_type, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(RequestsQueue, self).save(*args, **kwargs)


class SubscriptionPackage(models.Model):
    package_name = models.CharField(max_length=200)
    package_price = models.CharField(max_length=100, blank=True, null=True)
    package_max_word = models.CharField(max_length=100, blank=True, null=True, default='0') # 0 is for unlimited
    package_max_device = models.CharField(max_length=12, blank=True, null=True, default='0') # 0 is for unlimited
    package_max_memory = models.CharField(max_length=12, blank=True, null=True, default='0') # 0 is for unlimited
    package_status = models.BooleanField(default=True)
    package_description = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=False)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.package_name, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.package_name, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(SubscriptionPackage, self).save(*args, **kwargs)


class ToneOfVoice(models.Model):
    tone_of_voice = models.CharField(max_length=200)
    tone_status = models.BooleanField(default=True)
    tone_description = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.tone_of_voice, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.tone_of_voice, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(ToneOfVoice, self).save(*args, **kwargs)


class TeamClient(models.Model):
    client_name = models.CharField(max_length=255)

    contact_person = models.CharField(null=True, blank=True, max_length=255)
    industry = models.CharField(null=True, blank=True, max_length=255)
    client_email = models.CharField(null=True, blank=True, max_length=255)
    business_address = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    created_by = models.CharField(null=True, blank=True, max_length=100)
    team = models.CharField(null=True, blank=True, max_length=100)
    
    is_active = models.BooleanField(default=True)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.client_name, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.client_name, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(TeamClient, self).save(*args, **kwargs)


class ClientCategory(models.Model):
    category_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    created_by = models.CharField(null=True, blank=True, max_length=100)
    is_active = models.BooleanField(default=True)
    
    team = models.CharField(null=True, blank=True, max_length=100)
    # django related field
    client = models.ForeignKey(TeamClient, on_delete=models.CASCADE)

    # Utility Variable
    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.category_name, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[4]

        self.slug = slugify('{} {}'.format(self.category_name, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(ClientCategory, self).save(*args, **kwargs)
#
