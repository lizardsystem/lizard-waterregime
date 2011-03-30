from lizard_waterregime.models import TimeSeriesFactory
from lizard_waterregime.models import WaterRegimeShape

from datetime import datetime
from datetime import timedelta

from numpy import abs
from numpy import arange
from numpy import ones
from numpy import convolve
from numpy import array

class RegimeCalculator(object):

    erouter = {
            'P_HAZOF' : 'E_LELYSTAD',
            'P_LAZOF' : 'E_LELYSTAD',
            'P_HANOP' : 'E_MARKNESSE',
            'P_LANOP' : 'E_MARKNESSE',
            'P_TANOP' : 'E_MARKNESSE',
    }            

    @classmethod
    def weights(cls,r=1.5, tmax=7.):
        """Return an array of weightfactors with length tmax.
        
        Each value represents the weight of a given day in the total P, E or
        P-E. The most recent day, with the highest weight, is last."""
        days = arange(-tmax + 1.,1)
        factors = 1 / abs(days - r)
        normalized_factors = factors / sum(factors)
        return normalized_factors

        
    @classmethod
    def stretch(cls, array, amount=24):
        """Return an new array with each element of array repeated by amount.
        
        """
        timedeltas = map(lambda h: timedelta(hours=h),arange(0.,-amount,-1.))
        time
        print timedeltas
        
        return None#(ones((amount,array.size)) / amount * array).transpose().flatten()
        

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
        t1 = datetime(2011,3,16)
        t2 = datetime(2011,3,31)
        tsarr=array(list(TimeSeriesFactory.get('E_LELYSTAD').events(t1,t2)))
        cls.stretch(tsarr)
        
        

