# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',
        'lizard_waterregime.views.start',
        name='waterregime_start'),

    # Search stuff.
    url(r'^search_coordinates/',
        'lizard_map.views.search_coordinates',
        name="lizard_map.search_coordinates"),
    url(r'^search_name/',
        'lizard_map.views.search_name',
        name="lizard_map.search_name"),
)


if settings.DEBUG:
    # Add this also to the projects that use this application
    urlpatterns += patterns('',
        (r'', include('staticfiles.urls')),
        (r'^admin/', include(admin.site.urls)),
    )
