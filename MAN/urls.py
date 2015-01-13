from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'MAN.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^', include('orderSystem.urls', namespace='man')),

    url(r'^admin/', include(admin.site.urls)),
)

#This is to allow for dev envinronment to be able to serve files
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )