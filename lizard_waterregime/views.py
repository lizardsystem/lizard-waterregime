# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

# Create your views here.

#import datetime
#import logging
#import time

from django.core.urlresolvers import reverse
#from django.core.cache import cache
#from django.http import HttpResponse
#from django.http import HttpResponseRedirect
#from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
#from django.utils import simplejson
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#from matplotlib.lines import Line2D
#import mapnik
#import pkg_resources

#from lizard_map import coordinates
#from lizard_map.adapter import Graph
#from lizard_map.daterange import current_start_end_dates
#from lizard_map.daterange import DateRangeForm
#from lizard_map.models import Workspace
#from timeseries.timeseriesstub import TimeseriesStub
#from timeseries.timeseriesstub import grouped_event_values
#from timeseries.timeseriesstub import multiply_timeseries

#import hotshot
#import os

def start(
    request,
    template='lizard_waterregime/lizard_waterregime.html',
    special_homepage_workspace = get_object_or_404(
        Workspace, pk=1
    ),
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

    return render_to_response(
        template,
        {
            'workspaces': {'user': [special_homepage_workspace]},
            'javascript_hover_handler': 'popup_hover_handler',
            'javascript_click_handler': 'waterbalance_area_click_handler',
            'use_workspaces': False,
            'crumbs': crumbs
        },
        context_instance=RequestContext(request))
