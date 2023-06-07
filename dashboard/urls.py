from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='dashboard'),
    path('home', views.home, name='dashboard'),
    path('', views.home, name='home'),
    path('profile', views.profile, name='profile'),

    path('device-manager', views.device_manager, name='device-manager'),
    path('delete-device/<str:uniqueId>/', views.delete_device, name='delete-device'),

    path('team-manager', views.team_manager, name='team-manager'),
    path('delete-member/<str:orgUniqueId>/<str:uniqueId>/', views.delete_member, name='delete-member'),
    path('delete-invite/<str:userUid>/<str:uniqueId>/', views.delete_invite, name='delete-invite'),

    # billing
    path('billing', views.billing, name='billing'),
    path('dea248f7-dcfa-4edb-b012-3ad3ca07ead6', views.webhook, name='webhook'),

    path('payment-plans', views.payment_plans, name='payment-plans'),
    path('process-initiator-plan', views.process_initiator_plan, name='process-initiator-plan'),


    # home page url paths
    path('delete-blog-topic/<str:uniqueId>/', views.delete_blog_topic, name='delete-blog-topic'),
    path('generate-blog-from-topic/<str:uniqueId>/', views.create_blog_from_topic, name='generate-blog-from-topic'),

    # Blog generation routes
    path('generate-blog-topic', views.blog_topic, name='blog-topic'),
    path('generate-blog-sections', views.blog_sections, name='blog-sections'),

    path('save-section-head/<str:uniqueId>/<str:section_head>/', views.save_section_head, name='save-section-head'),

    # blog action routes
    path('save-blog-topic/<str:blog_topic>/', views.save_blog_topic, name='save-blog-topic'),
    path('use-blog-topic/<str:blog_topic>/', views.use_blog_topic, name='use-blog-topic'),
    path('view-generated-blog/<slug:slug>/', views.view_generated_blog, name='view-generated-blog'),

    path('view-blog/<slug:slug>/', views.view_gen_blog, name='view-gen-blog'),
    path('edit-blog/<str:uniqueId>/', views.edit_gen_blog, name='edit-gen-blog'),

    # Paragraph writer urls
    path('paragraph-writer', views.paragraph_writer, name='paragraph-writer'),
    path('paragraph-writer/<str:uniqueId>/', views.paragraph_writer, name='paragraph-writer-response'),

    # sentence rewriter urls
    path('sentence-writer', views.sentence_writer, name='sentence-writer'),
    path('sentence-writer/<str:uniqueId>/', views.sentence_writer, name='sentence-writer-response'),

    # title rewriter urls
    path('title-writer', views.article_title_writer, name='title-writer'),
    path('title-writer/<str:uniqueId>/', views.article_title_writer, name='title-writer-response'),

    # meta description generator urls
    path('meta-description-generator', views.meta_description_writer, name='meta-description-generator'),
    path('meta-description-generator/<str:uniqueId>/', views.meta_description_writer, name='meta-description-generator-response'),

    
    # content summarizer urls
    path('content-summarizer', views.summarize_content, name='content-summarizer'),
    path('content-summarizer/<str:uniqueId>/', views.summarize_content, name='content-summarizer-response'),

    # content landing page copy urls
    path('landing-page-copy', views.landing_page_copy, name='landing-page-copy'),
    path('landing-page-copy/<str:uniqueId>/', views.landing_page_copy, name='landing-page-copy-response'),

    # ajax URLs
    path('paypal-payment-success', views.paypal_payment_success, name='paypal-payment-success'),
    path('payment-success', views.payment_success, name='payment-success'),

    #memory pages 
    path('blog-memory', views.memory_blogs, name='blog-memory'),
    path('summarizer-memory', views.memory_summarizer, name='summarizer-memory'),
    path('page-copy-memory', views.memory_page_copy, name='page-copy-memory'),
    path('meta-description-memory', views.memory_meta_descr, name='meta-descr-memory'),
]
