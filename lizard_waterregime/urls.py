# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import *
from django.contrib import admin

from lizard_ui.urls import debugmode_urlpatterns
from lizard_waterregime.views import StartView

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$',
        StartView.as_view(),
        name='waterregime_start'),

    # Images other than the lizard-map default
    url(r'^workspace_item/(?P<workspace_item_id>\d+)/graph_image/',
        'lizard_waterregime.views.workspace_item_graph_image',
        name="lizard_waterregime.workspace_item_graph_image"),
    url(r'^workspace_item/(?P<workspace_item_id>\d+)/bar_image/',
        'lizard_waterregime.views.workspace_item_bar_image',
        name="lizard_waterregime.workspace_item_bar_image"),

    # Enable these for local testing
    #(r'', include('staticfiles.urls')),
    #(r'^admin/', include(admin.site.urls)),
    #(r'^map/', include('lizard_map.urls')),
)

urlpatterns += debugmode_urlpatterns()
