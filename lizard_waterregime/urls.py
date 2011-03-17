# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin


admin.autodiscover()

#crumb_waterregime = {'name': 'waterregime', 'url': '/waterregime/', 'title': 'Water Regime'}
crumb_home = [{'name': 'Home', 'url': '/', 'title': 'Hoofdpagina'}]


urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
    # waterregime urls
    (r'^$',
     'lizard_waterregime.views.start',
     {'crumbs_prepend': list(crumb_home),
      },
     'waterregime_start'),

    )


if settings.DEBUG:
    # Add this also to the projects that use this application
    urlpatterns += patterns('',
        (r'', include('staticfiles.urls')),
    )

