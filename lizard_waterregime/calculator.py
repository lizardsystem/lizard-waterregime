from lizard_waterregime.models import TimeSeriesFactory
from lizard_waterregime.models import WaterRegimeShape

from datetime import datetime
from datetime import timedelta

from numpy import abs
from numpy import arange
from numpy import ones
from numpy import convolve
from numpy import array
from numpy import vstack

class RegimeCalculator(object):

    erouter = {
            'P_HAZOF' : 'E_LELYSTAD',
            'P_LAZOF' : 'E_LELYSTAD',
            'P_HANOP' : 'E_MARKNESSE',
            'P_LANOP' : 'E_MARKNESSE',
            'P_TANOP' : 'E_MARKNESSE',
    }
    
    @classmethod
    def weights(cls,r=1.5, tmax=7, stretch=1):
        """Return an array of weightfactors with length (tmax * stretch).
        
        Each value represents the weight of a given value in the total P, E
        or P-E. The most recent value, with the highest weight, is last."""
        days = arange(-tmax + 1.,1)
        factors = 1 / abs(days - r)
        #factors.resize((tmax,1))
        #tmp = ones(tmax,stre
        stretched_factors = (factors.reshape(tmax,1) * ones((tmax,stretch))).ravel()
        normalized_factors = stretched_factors / sum(stretched_factors)
        return normalized_factors

        
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
    def weighted_series(cls,timeseries, weights):
        return None


    @classmethod
    def test(cls):
        t1 = datetime(2011,3,16)
        t2 = datetime(2011,3,31)
        tsd = {
            'E_LELYSTAD' : TimeSeriesFactory.get('E_LELYSTAD'),
            'E_MARKNESSE' : TimeSeriesFactory.get('E_MARKNESSE'),
            'P_HAZOF' : TimeSeriesFactory.get('P_HAZOF'),
            'P_LAZOF' : TimeSeriesFactory.get('P_LAZOF'),
            'P_HANOP' : TimeSeriesFactory.get('P_HANOP'),
            'P_LANOP' : TimeSeriesFactory.get('P_LANOP'),
            'P_TANOP' : TimeSeriesFactory.get('P_TANOP'),
        }

        for x in tsd['E_LELYSTAD'].events(t1,t2):
            print x
        
        y=array(list(tsd['E_LELYSTAD'].events(t1,t2)))
        print y.shape
        print cls.stretch(y,2)

    @classmethod        
    def test2(cls):
        x = cls.weights(tmax=5,r=5.6,stretch=7)
        print x
        print sum(x)
        print x.size

