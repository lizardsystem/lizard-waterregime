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
from lizard_map.daterange import current_start_end_dates
from lizard_map.daterange import DateRangeForm
#from lizard_map.models import Workspace
from lizard_map.workspace import WorkspaceManager
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
