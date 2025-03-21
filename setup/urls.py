from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from api import routers as api_routers
from apps.person.views import urls as person_urls

urlpatterns = [
    path('api/', include(api_routers)),
    path('person/', include(person_urls)),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL,
                      document_root=settings.STATIC_ROOT)

# Remove admin sidebar nav sidebar
# https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.AdminSite.enable_nav_sidebar
admin.site.enable_nav_sidebar = False
admin.site.site_header = 'HSE Admin Panel'
admin.site.site_title = 'HSEAdmin Panel'

if settings.DEBUG and not settings.IS_UNIX:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
