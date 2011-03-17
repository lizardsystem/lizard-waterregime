# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('lizard_waterregime.views',
    url(r'^$', 'start', name='waterregime_start'),
    url(r'^viewer/$', 'waterregime_viewer', name="waterregime_viewer"),
)

if settings.DEBUG:
    # Add this also to the projects that use this application
    urlpatterns += patterns('',
        (r'', include('staticfiles.urls')),
        (r'^admin/', include(admin.site.urls)),
    )
