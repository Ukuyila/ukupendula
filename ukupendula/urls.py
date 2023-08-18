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

handler404 = 'dashboard.views.error_404'
handler500 = 'dashboard.views.error_500'
handler403 = 'dashboard.views.error_403'
handler400 = 'dashboard.views.error_400'
