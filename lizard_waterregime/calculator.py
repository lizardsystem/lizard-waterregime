from lizard_waterregime.models import TimeSeriesFactory
from lizard_waterregime.models import WaterRegimeShape
from lizard_waterregime.models import PrecipitationSurplus

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
        or P-E. The most recent value, with the highest weight, is last."""
        days = arange(-tmax + 1.,1)
        factors = 1 / abs(days - r)
        stretched_factors = (factors.reshape(tmax,1) * ones((tmax,stretch))).ravel()
        normalized_factors = stretched_factors / sum(stretched_factors)
        return normalized_factors


    @classmethod
    def weighted_events(cls, events, weights):
        """ Return array of weighted events."""
        dates,values = array([list(events)]).transpose()

        weighted_dates = dates[weights.size - 1:]

        print weights.shape
        weighted_values = convolve(values.reshape(-1,),weights,'valid')
        return vstack((daily_dates,daily_values)).transpose()

        
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
        """ Return events with dates from a and values a - b """
        return [
            (pair[0][0], pair[0][1] * pair[1][1])
            for pair in zip(list(events_a),list(events_b))]

    @classmethod
    def multiply_event_values(cls, events, factor):
        """ Return events with values multiplied by factor """
        return [(e[0], e[1] * factor) for e in events]

    @classmethod
    def refresh(cls,dt):
        """ Check and if necessary insert precipitationsurplus values in
        database for datetime """
        try:
            counts = PrecipitationSurplus.objects.get(
                        date=_first_of_hour(dt)
                     ).count()

            return counts
        except PrecipitationSurplus.DoesNotExist:
            # nieuwe precipitationsurplusobjecten in database stoppen
            WaterRegimeShape.objects.all()
            t1 = dt
            t2 = dt + timedelta(days=-7)

            print(t1)
            print(t2)
            print(list(TimeSeriesFactory.get('E_MARKNESSE').events(t1,t2)))
            
            # get the events
            events = {}
            for s in set(timeseries_dict.itervalues()):
                events[s] = TimeSeriesFactory.get(s).events(t1,t2)

            # get the shapes
            shapes = WaterRegimeShape.objects.all()

            # tidying up:
            p_events = {}
            e_events = {}
            c_events = {}
            
            for s in shapes:
                p_events[s.afdeling] = events[timeseries_dict['P_' + s.afdeling]]
                e_events[s.afdeling] = events[timeseries_dict['E_' + s.afdeling]]

                c_events[s.afdeling] = [
                    (d,s.get_cropfactor(d)) for d,v in e_events[s.afdeling]
                ]

                # todo here:
                #   convert p_events to daily
                #   multiply e_events by c_events values (use the multiply... method)
                #   subtract p from e, use the subtract method
                #   use weighting method
                # save() the values in the database for each shape.
            return 0

    @classmethod        
    def test(cls):
        print cls.refresh(datetime.now())
        


