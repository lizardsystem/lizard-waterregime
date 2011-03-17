# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

# Create your views here.

import datetime
import logging
import time

from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.lines import Line2D
import mapnik
import pkg_resources

from lizard_map import coordinates
from lizard_map.adapter import Graph
from lizard_map.daterange import current_start_end_dates
from lizard_map.daterange import DateRangeForm
from lizard_map.models import Workspace
from timeseries.timeseriesstub import TimeseriesStub
from timeseries.timeseriesstub import grouped_event_values
from timeseries.timeseriesstub import multiply_timeseries

import hotshot
import os

def start(request,
          template='lizard_waterregime/lizard_waterregime.html',
          crumbs_prepend=None):
    """Show waterbalance overview workspace.

    The workspace for the waterbalance homepage should already be present.

    Parameters:
    * crumbs_prepend -- list of breadcrumbs

    """

    if crumbs_prepend is None:
        crumbs = [{'name': 'home', 'url': '/'}]
    else:
        crumbs = list(crumbs_prepend)

    crumbs.append({'name': 'Waterregime',
                   'title': 'Waterregime',
                   'url': reverse('waterregime_start')})

    return render_to_response(
        template,
        {
            'javascript_hover_handler': 'popup_hover_handler',
            'javascript_click_handler': 'waterbalance_area_click_handler',
            'crumbs': crumbs
        },
        context_instance=RequestContext(request))

