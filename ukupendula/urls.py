from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('landing.urls')),
    path('auth/', include('authorisation.urls')),
    path('dash/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'dashboard.views.custom_page_not_found_view'
handler500 = 'dashboard.views.custom_error_view'
handler403 = 'dashboard.views.custom_permission_denied_view'
handler400 = 'dashboard.views.custom_bad_request_view'
