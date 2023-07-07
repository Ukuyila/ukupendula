from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='dashboard'),
    path('home', views.home, name='dashboard'),
    path('', views.home, name='home'),
    path('profile', views.profile, name='profile'),

    path('edit-settings', views.edit_settings, name='edit-settings'),

    path('device-manager', views.device_manager, name='device-manager'),
    path('delete-device/<str:uniqueId>/', views.delete_device, name='delete-device'),

    path('team-manager', views.team_manager, name='team-manager'),
    path('add-new-member', views.add_team_member, name='add-new-member'),
    path('edit-member', views.edit_team_member, name='edit-member'),
    path('delete-member/<str:orgUniqueId>/<str:uniqueId>/', views.delete_member, name='delete-member'),
    path('delete-invite/<str:userUid>/<str:uniqueId>/', views.delete_invite, name='delete-invite'),

    # billing
    path('billing', views.billing, name='billing'),
    path('dea248f7-dcfa-4edb-b012-3ad3ca07ead6', views.webhook, name='webhook'),
    path('subscription-plan/<str:uniqueId>/<str:planId>/', views.get_single_plan, name='subscription-plan'),

    path('payment-plans', views.payment_plans, name='payment-plans'),
    path('pay-now/<str:planId>/', views.payfast_payment, name='pay-now'),
    # path('process-initiator-plan', views.process_initiator_plan, name='process-initiator-plan'),

    # home page url paths
    path('delete-blog/<str:uniqueId>/', views.delete_blog, name='delete-blog'),
    path('delete-saved-blog/<str:uniqueId>/', views.delete_saved_blog, name='delete-saved-blog'),
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

    path('blog-social-media/<str:postType>/<str:uniqueId>/', views.gen_social_from_blog, name='gen-blog-social-media'),
    # path('social-media/<str:postType>/', views.gen_social_post, name='social-media'),
    path('view-social-media/<str:postType>/<str:uniqueId>/', views.view_social_post, name='view-social-media'),
    path('del-social-media/<str:uniqueId>/', views.delete_social_post, name='delete-social-media'),

    # Paragraph writer urls
    path('paragraph-writer', views.paragraph_writer, name='paragraph-writer'),
    path('paragraph-writer/<str:uniqueId>/', views.paragraph_writer, name='paragraph-writer-response'),
    path('delete-paragraph/<str:uniqueId>/', views.delete_paragraph, name='delete-paragraph'),

    # sentence rewriter urls
    path('sentence-writer', views.sentence_writer, name='sentence-writer'),
    path('sentence-writer/<str:uniqueId>/', views.sentence_writer, name='sentence-writer-response'),
    path('delete-sentence/<str:uniqueId>/', views.delete_sentence, name='delete-sentence'),

    # title rewriter urls
    path('title-writer', views.article_title_writer, name='title-writer'),
    path('title-writer/<str:uniqueId>/', views.article_title_writer, name='title-writer-response'),
    path('delete-title/<str:uniqueId>/', views.delete_title, name='delete-title'),

    # meta description generator urls
    path('meta-description-generator', views.meta_description_writer, name='meta-description-generator'),
    path('generate-blog-meta/<str:uniqueId>/', views.generate_blog_meta, name='generate-blog-meta'),
    path('meta-description-generator/<str:uniqueId>/', views.meta_description_writer, name='meta-description-generator-response'),
    path('delete-meta-description/<str:uniqueId>/', views.delete_meta_descr, name='delete-meta-descr'),
    
    # categories urls
    path('categories', views.categories, name='categories'),
    path('edit-category/<str:uniqueId>/', views.edit_category, name='edit-category'),
    path('delete-category/<str:uniqueId>/', views.delete_category, name='delete-category'),
    path('cate-status/<str:status>/<str:uniqueId>/', views.change_category_status, name='cate-status'),

    # clients url
    path('clients', views.clients, name='clients'),
    path('edit-client', views.edit_client, name='edit-client'),
    path('delete-client/<str:uniqueId>/', views.delete_client, name='delete-client'),
    path('client-status/<str:status>/<str:uniqueId>/', views.change_client_status, name='client-status'),
    
    # content summarizer urls
    path('content-summarizer', views.summarize_content, name='content-summarizer'),
    path('content-summarizer/<str:uniqueId>/', views.summarize_content, name='content-summarizer-response'),
    path('generate-blog-summary/<str:uniqueId>/', views.summarize_blog, name='generate-blog-summary'),
    path('delete-summary/<str:uniqueId>/', views.delete_summary, name='delete-summary'),

    # content landing page copy urls
    path('landing-page-copy', views.landing_page_copy, name='landing-page-copy'),
    path('landing-page-copy/<str:uniqueId>/', views.landing_page_copy, name='landing-page-copy-response'),
    path('delete-page-copy/<str:uniqueId>/', views.delete_page_copy, name='delete-copy'),

    # ajax URLs
    path('paypal-payment-success', views.paypal_payment_success, name='paypal-payment-success'),
    path('payment-success/<str:uniqueId>', views.payment_success, name='payment-success'),
    path('payment-cancel', views.payment_cancel, name='payment-cancel'),

    #memory pages 
    path('blog-memory/<str:status>/', views.memory_blogs, name='blog-memory'),
    path('blog-memory/<str:status>/', views.memory_blogs, name='incomplete-blog-memory'),
    path('blog-memory/<str:status>/', views.memory_blogs, name='saved-blog-memory'),
    path('paragraph-memory', views.memory_paragraph, name='paragraph-memory'),
    path('sentence-memory', views.memory_sentence, name='sentence-memory'),
    path('title-memory', views.memory_title, name='title-memory'),
    path('summarizer-memory', views.memory_summarizer, name='summarizer-memory'),
    path('page-copy-memory', views.memory_page_copy, name='page-copy-memory'),
    path('meta-description-memory', views.memory_meta_descr, name='meta-descr-memory'),
    path('social-post-memory', views.memory_social_post, name='social-post-memory'),

    # user roles
    path('user-roles', views.user_roles, name='user-roles'),
    path('delete-user-role/<str:team_uid>/<str:uniqueId>', views.delete_user_role, name='delete-user-role'),
]
