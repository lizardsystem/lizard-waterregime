from lizard_waterregime.models import Constant
from lizard_waterregime.models import PrecipitationSurplus
from lizard_waterregime.models import TimeSeriesFactory
from lizard_waterregime.models import WaterRegimeShape

from datetime import datetime
from datetime import timedelta

from numpy import abs
from numpy import arange
from numpy import array
from numpy import convolve
from numpy import ones
from numpy import vstack

def _first_of_hour(dt):
    """Return the first moment of the hour for a datetime."""
    return datetime(dt.year, dt.month, dt.day, dt.hour)

# This *could* also be in the database. It relates timeseries
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
    method."""
    

    
        
    @classmethod
    def weights(cls,r=1.5, tmax=7, stretch=1):
        """Return an array of weightfactors with length (tmax * stretch).
        
        Each value represents the weight of a given value in the total P, E
        or P-E. The most recent value, with the highest weight, is first,
        since it is inded to be used with numpy.convolve() which flips its
        second argument. The sum of the resulting list is equal to stretch.
        In this way the result of the weighting is always a daily value, even
        if the values to be weighted are for example hourly."""
        days = arange(-tmax + 1.,1)
        factors = 1 / abs(days - r)
        stretched_factors = (factors.reshape(tmax, 1) *
                                ones((tmax, stretch))).ravel()
        normalized_factors = (stretched_factors / 
                                sum(stretched_factors) * stretch)
        return normalized_factors


    @classmethod
    def weighted_events(cls, events, weights):
        """ Return array of weighted events."""
        dates,values = array([list(events)]).transpose()

        weighted_values = convolve(values.reshape(-1,),weights,'valid')
        weighted_dates = dates[weights.size - 1:].reshape(-1)
        return vstack((weighted_dates,weighted_values)).transpose()
        
        
    @classmethod
    def make_hourly(cls, events):
        """Return an array of hourly events.
        
        The events are expected to be daily at midnight. The values are
        divided by 24. The extra dates come before the existing date."""
        
        dates,values = array([list(events)]).transpose()

        timedeltas = map(lambda h: timedelta(hours=h),arange(-23.,1.))
        hourly_dates = (dates+timedeltas).flatten()

        valuefactors = ones((1,24))/24.
        hourly_values = (values*valuefactors).flatten()
        
        return vstack((hourly_dates,hourly_values)).transpose()

    @classmethod
    def make_daily(cls, events):
        """Return an array of daily events.
        
        The list of events is truncated to the last 24 * n values, n integer.
        For every group of 24 events, the last date and the sum of the values
        is returned."""
        
        events_list = list(events)
        
        # Make an array and truncate to last 24 * n values, n integer.
        dates,values = array(events_list[len(events_list) % 24:]).transpose()
        
        dates.shape = (dates.size / 24, 24)
        values.shape = (dates.size / 24, 24)

        daily_dates = map(max,dates)
        daily_values = map(sum,values)

        return vstack((daily_dates,daily_values)).transpose()

    @classmethod
    def subtract_event_values(cls, events_a, events_b):
        """ Return events with dates from a and values a - b """
        return [
            (pair[0][0], pair[0][1] - pair[1][1])
            for pair in zip(list(events_a),list(events_b))]


    @classmethod
    def multiply_event_values(cls, events_a, events_b):
        """ Return events with dates from a and values a * b """
        return [
            (pair[0][0], pair[0][1] * pair[1][1])
            for pair in zip(list(events_a),list(events_b))]

    @classmethod
    def refresh(cls,dt):
        """ Check and if necessary insert precipitationsurplus values in
        database for datetime """
        
        try:
            counts = PrecipitationSurplus.objects.get(
                date=_first_of_hour(dt)).count()
            return counts
        except PrecipitationSurplus.DoesNotExist:
            pass

        tmax = int(abs(Constant.get('Tmax')))
        # 1 second less, to prevent a value to much
        date1 = dt - timedelta(days=tmax, seconds=-1)
        date2 = dt

        shapes = WaterRegimeShape.objects.all()

        for s in shapes:
            pmine,p,e = cls.weighted_precipitation_surplus(
                s.afdeling, date1, date2)
            p = PrecipitationSurplus(
                waterregimeshape=s,
                date=_first_of_hour(dt),
                value=pmine[0][1],
            )
            p.save()


    @classmethod
    def weighted_precipitation_surplus(
        cls, area, date1, date2):
        """Return all data tuple of weighted events weighted. Since daily
        values maybe required, everything is converted to daily."""
        
        tmax = abs(int(Constant.get('Tmax')))
        r = abs(int(Constant.get('R_' + area)))

        weights = cls.weights(r=r, tmax=tmax, stretch=24)
        shape = WaterRegimeShape.objects.get(afdeling=area)
        
        p_series = TimeSeriesFactory.get(timeseries_dict['P_' + area])
        e_series = TimeSeriesFactory.get(timeseries_dict['E_' + area])

        
        # P must be hourly anyway
        if p_series.hours == 24:
            p_events_hourly = cls.make_hourly(p_series.events(date1,date2))
        elif p_series.hours == 1:
            p_events_hourly = tuple(p_series.events(date1,date2))
        # else: raise some error?

        # E daily is also necessary, to reduce load on the 
        # get_cropfactor() method.
        if e_series.hours == 24:
            eref_events_daily = tuple(e_series.events(date1,date2))
            eref_events_hourly = cls.make_hourly(eref_events_daily)
        elif e_series.hours == 1:
            eref_events_hourly = tuple(e_series.events(date1,date2))
            eref_events_daily = cls.make_daily(eref_events_hourly)
        # else: raise some error?

        c_events_daily = [(dt, shape.get_cropfactor(dt))
                        for dt, v in eref_events_daily]
        c_events_hourly = cls.make_hourly(c_events_daily)
                        
        e_events_hourly = cls.multiply_event_values(
                            eref_events_hourly,c_events_hourly)

                            
        p_weighted = cls.weighted_events(p_events_hourly, weights)
        e_weighted = cls.weighted_events(e_events_hourly, weights)
        
        pmine_weighted = cls.subtract_event_values(p_weighted, e_weighted)

        return pmine_weighted,p_weighted,e_weighted
    
    @classmethod
    def test(cls):
        cls.refresh(datetime.now())
