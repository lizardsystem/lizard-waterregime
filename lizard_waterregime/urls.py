# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from lizard_waterregime.views import StartView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',
        StartView.as_view(),
        name='waterregime_start'),

    # Search stuff.
    url(r'^search_coordinates/',
        'lizard_map.views.search_coordinates',
        name="lizard_map.search_coordinates"),
    url(r'^search_name/',
        'lizard_map.views.search_name',
        name="lizard_map.search_name"),

    # Images other than the lizard-map default
    url(r'^workspace_item/(?P<workspace_item_id>\d+)/graph_image/',
        'lizard_waterregime.views.workspace_item_graph_image',
        name="lizard_waterregime.workspace_item_graph_image"),
    url(r'^workspace_item/(?P<workspace_item_id>\d+)/bar_image/',
        'lizard_waterregime.views.workspace_item_bar_image',
        name="lizard_waterregime.workspace_item_bar_image"),
)


if settings.DEBUG:
    # Add this also to the projects that use this application
    urlpatterns += patterns('',
        (r'', include('staticfiles.urls')),
        (r'^admin/', include(admin.site.urls)),
    )
