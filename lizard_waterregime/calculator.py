from lizard_waterregime.models import Constant
from lizard_waterregime.models import PrecipitationSurplus
from lizard_waterregime.models import TimeSeriesFactory
from lizard_waterregime.models import WaterRegimeShape

from datetime import datetime
from datetime import timedelta

from numpy import abs
from numpy import arange
from numpy import array
from numpy import concatenate
from numpy import convolve
from numpy import interp
from numpy import NaN
from numpy import ones
from numpy import vstack
from numpy import zeros

import logging
logger = logging.getLogger('nens.calculator')

def _first_of_hour(dt):
    """Return the first moment of the hour for a datetime."""
    return datetime(dt.year, dt.month, dt.day, dt.hour)
    
def _to_events(dates, values):
    """Return an array of date,value pairs."""
    return concatenate(([dates],[values])).transpose()

def  _split_events(events):
    """Return a (dates, values) tuple of arrays."""
    return events[:,0],events[:,1]


# This *could* also be in the database. It relates timeseries.
timeseries_dict = {
        'E_HAZOF' : 'E_LELYSTAD',
        'E_LAZOF' : 'E_LELYSTAD',
        'E_HANOP' : 'E_MARKNESSE',
        'E_LANOP' : 'E_MARKNESSE',
        'E_TANOP' : 'E_MARKNESSE',
        'P_HAZOF' : 'P_HAZOF',
        'P_LAZOF' : 'P_LAZOF',
        'P_HANOP' : 'P_HANOP',
        'P_LANOP' : 'P_LANOP',
        'P_TANOP' : 'P_TANOP',
}

class RegimeCalculator(object):
    """ Calculation methods for the waterregime djangoapp.
    
    TODO: Many methods transform lists into arrays and / or return arrays.
    Better to transform at one place instead of back and forth for each
    method.
    """
    
    @classmethod
    def map_events(cls, p_series, e_series):
        """
        """

        e_mapped = []
        e_dict = dict((event[0], event[1]) for event in e_series)

        for event in p_series:

            dt = event[0]

            try:
                dt_before = datetime(dt.year, dt.month, dt.day)
                e_before = float(e_dict[dt_before])
            except:
                e_before = None

            try:
                dt_after = dt_before + timedelta(days=1)
                e_after = float(e_dict[dt_after])
            except:
                e_after = None

            if e_before is not None and e_after is not None:
                delta = dt - dt_before
                e_dt = interp(delta.seconds, (0, 86400), (e_before, e_after))
            elif e_before is not None:
                e_dt = e_before
            elif e_after is not None:
                e_dt = e_after
            else:
                e_dt = cls.nearest(dt, e_series)

            e_mapped.append((dt, e_dt))

        return array(p_series), array(e_mapped)

    @classmethod
    def nearest(cls, dt, series):
        """
        """
        return NaN

    @classmethod
    def weights(cls, r, tmax):
        """Return an array of weightfactors"""
        
        # Start with an array of days [0, -1, ..., -tmax]
        days = arange(0., -tmax, -1)
        factors = 1 / abs(days - r)
        normalized_factors = factors / sum(factors)
        
        # Use numpy functions to insert 23 zeros between every factor
        a = concatenate((array([1]),zeros(23))).reshape(1,-1)
        b = normalized_factors.reshape(-1,1)
        result = (a * b).ravel()[:-23]

        return result

    @classmethod
    def weighted_precipitation_surplus(
        cls, shape, dt1, dt2):
        """Return all-data-tuple with resulting and source data.
        
        Returned data tuple contains three arrays of events:
        - calculated p minus e events
        - original p events
        - original e events
        
        If dt1 == dt2 and all data is present, exactly one calculated event
        is returned."""
        
        tmax = int(Constant.get('Tmax'))
        r = abs(int(Constant.get('R_' + shape.afdeling)))
        
        # To calculate weighted p min e over past we need some past events
        # as well, we need Tmax * 24 p values 
        p_dt1 = dt1 - timedelta(days = tmax, seconds = -1)       

        # however, for the map_events() to function properly, the e event at
        # the beginning of the day of the first p event must be there as well.
        e_dt1 = datetime(p_dt1.year, p_dt1.month, p_dt1.day)
        

        # Get the relevant timeseries
        p_series = TimeSeriesFactory.get(timeseries_dict['P_' + shape.afdeling])
        e_series = TimeSeriesFactory.get(timeseries_dict['E_' + shape.afdeling])
            
        # Get the events from the period of interest
        p_events = tuple(p_series.events(p_dt1, dt2, missing=NaN))
        eref_events = tuple(e_series.events(e_dt1, dt2, missing=NaN))
        e_events = [[dt, v * shape.get_cropfactor(dt)]
                        for dt, v in eref_events]  

        # Make sure there is an e_event for every p_event
        p_aligned, e_aligned = cls.map_events(p_events, e_events)

        # p values are for the past hour, e values for the past day.
        # Therefore p has to be accumulated, and the length of e has to
        # be adjusted accordingly. But only do this if p is at least 24 long,
        # else return empty lists.
        if p_aligned.shape[0] >= 24:
            p_daily_values = convolve(p_aligned[:,1],ones(24),'valid')
            e_daily_values = e_aligned[23:,1]
            daily_dates =  p_aligned[23:,0]
        else:
            p_daily_values = array([])
            e_daily_values = array([])
            daily_dates =  array([])
            
        # Only do the weighting if p_daily_values is long enough for the
        # weights, so that at least one value as returned.
        weights = cls.weights(r=r, tmax=tmax)
        if p_daily_values.shape[0] >= weights.size:
            p_weighted = convolve(p_daily_values, weights, 'valid')
            e_weighted = convolve(e_daily_values, weights, 'valid')
            dates_weighted = daily_dates[weights.size - 1:]
        else:
            p_weighted = array([])
            e_weighted = array([])
            dates_weighted = array([])

        pmine_weighted = p_weighted - e_weighted

        return (
            _to_events(dates_weighted,pmine_weighted),
            array(p_events),
            array(e_events)
        )

    
    @classmethod
    def refresh(cls,dt):
        """Insert PrecipitationSurplus values in database.
        
        All PrecipitationSurplus objects in de database are deleted.
        To be called from the waterregime adapter."""
        for obj in PrecipitationSurplus.objects.all():
            obj.delete()

        shapes = WaterRegimeShape.objects.all()

        valid_values = 0
        for s in shapes:
            pmine,p,e = cls.weighted_precipitation_surplus(
                shape = s, dt1 = dt, dt2 = dt
            )
            if pmine.shape == (1,2) and not pmine[0,1] == NaN:
                value = pmine[0,1]
                valid = 'Y'
                valid_values += 1
            else:
                value = 0
                valid = 'N'
            p = PrecipitationSurplus(
                waterregimeshape=s,
                date=_first_of_hour(dt),
                value=value,
                valid=valid
            )
            p.save()

        return valid_values


    @classmethod
    def test(cls):
        #a,b,c = cls.weighted_precipitation_surplus(
        #    WaterRegimeShape.objects.all()[0], datetime.now(),datetime.now()+timedelta(5))
        cls.refresh(datetime(2011,3,29))
        
