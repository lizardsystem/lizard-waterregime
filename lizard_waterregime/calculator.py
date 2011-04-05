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

        p_mapped = []
        e_mapped = []
        e_dict = dict((event[0], event[1]) for event in e_series)

        for event in p_series:
            dt = event[0]
            try:
                e = e_dict[datetime(dt.year, dt.month, dt.day)]
            except KeyError:
                e = cls.nearest(dt, e_series)
            p_mapped.append(event)
            e_mapped.append((dt, e))

        return array(p_mapped), array(e_mapped)

    @classmethod
    def nearest(cls, dt, series):
        return 0 #TODO

    @classmethod
    def weights(cls, r, tmax):
        """Return an array of weightfactors"""
        
        days = arange(-tmax + 1.,1)
        factors = 1 / abs(days - r)
        normalized_factors = factors / sum(factors)
        
        a = concatenate((zeros(23),array([1]))).reshape(1,-1)
        b = normalized_factors.reshape(-1,1)
        
        result = (a * b).ravel()
        
        return result

    @classmethod
    def weighted_precipitation_surplus(
        cls, shape, date1, date2):
        """Return all data tuple of weighted events weighted. Since daily
        values maybe required, everything is converted to daily."""
        
        tmax = int(Constant.get('Tmax'))
        r = abs(int(Constant.get('R_' + shape.afdeling)))
        
        extra_time = timedelta(days = tmax, hours = 23, seconds = -1)       
        internal_start = date1 - extra_time

        weights = cls.weights(r=r, tmax=tmax)
        
        p_series = TimeSeriesFactory.get(timeseries_dict['P_' + shape.afdeling])
        e_series = TimeSeriesFactory.get(timeseries_dict['E_' + shape.afdeling])
            
        p_events = tuple(p_series.events(internal_start, date2, missing=0))
        eref_events = tuple(e_series.events(internal_start, date2, missing=0))
        e_events = [(dt, v * shape.get_cropfactor(dt))
                        for dt, v in eref_events]  
        
        p_aligned, e_aligned = cls.map_events(p_events, e_events)
        
        p_daily_values = convolve(p_aligned[:,1],ones(24),'valid')
        e_daily_values = e_aligned[23:,1]
        dates =  p_aligned[23:,0]

        p_weighted = convolve(p_daily_values,weights,'valid')
        e_weighted = convolve(e_daily_values,weights,'valid')
        dates_weighted = dates[weights.size - 1:]

        pmine_weighted = p_weighted - e_weighted

        #print concatenate(([dates],[p_daily_values])).transpose()
        
        return (
            _to_events(dates_weighted,pmine_weighted),
            _to_events(dates,p_daily_values),
            array(e_events),
        )

    
    @classmethod
    def refresh(cls,dt):
        """ Check and if necessary insert precipitationsurplus values in
        database for datetime.
        
        To be called from the waterregime adapter."""

        qs = PrecipitationSurplus.objects.filter(date=_first_of_hour(dt))       
        # if PrecipitationSurplus.objects.filter(date=_first_of_hour(dt)).exists():
        if bool(qs):
            for obj in qs:
                obj.delete()
        # return False


        shapes = WaterRegimeShape.objects.all()

        for s in shapes:
            pmine,p,e = cls.weighted_precipitation_surplus(
                s, dt, dt)
            p = PrecipitationSurplus(
                waterregimeshape=s,
                date=_first_of_hour(dt),
                value=pmine[0][1],
            )
            p.save()

        return True


    @classmethod
    def test(cls):
        a,b,c = cls.weighted_precipitation_surplus(
            WaterRegimeShape.objects.all()[0],
            datetime.now(),
            datetime.now()
        )
        print a
        print b
        print c

