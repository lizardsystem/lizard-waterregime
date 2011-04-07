# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

# Create your views here.

#import datetime
import logging
logger = logging.getLogger(__name__)
#import time

from django.core.urlresolvers import reverse
#from django.core.cache import cache
#from django.http import HttpResponse
#from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
#from django.utils import simplejson
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#from matplotlib.lines import Line2D
#import mapnik
#import pkg_resources

#from lizard_map import coordinates
#from lizard_map.adapter import Graph
from lizard_map.daterange import current_start_end_dates
from lizard_map.daterange import DateRangeForm
#from lizard_map.models import Workspace
from lizard_map.models import WorkspaceItem
from lizard_map.workspace import WorkspaceManager
from lizard_map.animation import slider_layout_extra

#from timeseries.timeseriesstub import TimeseriesStub
#from timeseries.timeseriesstub import grouped_event_values
#from timeseries.timeseriesstub import multiply_timeseries

#import hotshot
#import os

from lizard_waterregime.models import WaterRegimeShape


def start(request,
          template='lizard_waterregime/lizard_waterregime.html',
          crumbs_prepend=None):
    """ Show waterregime homepage.
    """

    if crumbs_prepend is None:
        crumbs = [{'name': 'home', 'title': 'hoofdpagina', 'url': '/'}]
    else:
        crumbs = list(crumbs_prepend)

    crumbs.append({'name': 'waterregime',
                   'title': 'waterregime',
                   'url': reverse('waterregime_start')})

    workspace_manager = WorkspaceManager(request)
    workspaces = workspace_manager.load_or_create()

    date_range_form = DateRangeForm(
        current_start_end_dates(request, for_form=True))

    shapes = WaterRegimeShape.objects.all()

    return render_to_response(template,
        {
            'crumbs': crumbs,
            'workspaces': workspaces,
            'date_range_form': date_range_form,
            'waterregime_shapes': shapes,
            'javascript_hover_handler': 'popup_hover_handler',
            'javascript_click_handler': 'popup_click_handler',
            'use_workspaces': False,
        },
        context_instance=RequestContext(request))
        
def workspace_item_graph_image(request, workspace_item_id):
    """Shows image corresponding to workspace item and location identifier(s)
    only works with regime adapter
    identifier_list
    """
    
#    identifier_json_list = request.GET.getlist('identifier')
#    identifier_list = [json.loads(identifier_json) for identifier_json in
#                       identifier_json_list]
    
    identifier_list = [{'afdeling': request.GET.get('afdeling'),}]

    width = request.GET.get('width')
    height = request.GET.get('height')
    if width:
        width = int(width)
    else:
        # We want None, not u''.
        width = None
    if height:
        height = int(height)
    else:
        # We want None, not u''.
        height = None

    workspace_item = get_object_or_404(WorkspaceItem, pk=workspace_item_id)
    start_date, end_date = current_start_end_dates(request)

    # add animation slider position
    layout_extra = slider_layout_extra(request)

    return workspace_item.adapter.graph_image(identifier_list, start_date, end_date,
                                        width, height,
                                        layout_extra=layout_extra)

def workspace_item_bar_image(request, workspace_item_id):
    """Shows image corresponding to workspace item and location identifier(s)

    identifier_list
    """

#    identifier_json_list = request.GET.getlist('identifier')
#    identifier_list = [json.loads(identifier_json) for identifier_json in
#                       identifier_json_list]
                       
    identifier_list = [{'afdeling': request.GET.get('afdeling'),}]

    width = request.GET.get('width')
    height = request.GET.get('height')
    if width:
        width = int(width)
    else:
        # We want None, not u''.
        width = None
    if height:
        height = int(height)
    else:
        # We want None, not u''.
        height = None

    workspace_item = get_object_or_404(WorkspaceItem, pk=workspace_item_id)
    start_date, end_date = current_start_end_dates(request)

    # add animation slider position
    layout_extra = slider_layout_extra(request)

    return workspace_item.adapter.bar_image(identifier_list, start_date, end_date,
                                        width, height,
                                        layout_extra=layout_extra)
                
