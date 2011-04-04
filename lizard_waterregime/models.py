# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# from django.db import models

# Create your models here.

from datetime import date
from datetime import datetime
from datetime import timedelta
from django.contrib.gis.db import models
from django.core.cache import cache
from lizard_fewsunblobbed.models import Filter
from lizard_fewsunblobbed.models import Location
from lizard_fewsunblobbed.models import Parameter
from lizard_fewsunblobbed.models import Timeserie


class WaterRegimeShape(models.Model):
    gid = models.IntegerField(primary_key=True)
    afdeling = models.CharField(max_length=5, unique=True)
    naam = models.CharField(max_length=50)
    area_m2 = models.DecimalField(max_digits=20, decimal_places=10)
    the_geom = models.MultiPolygonField(srid= -1)
    objects = models.GeoManager()

    def get_cropfactor(self, date=date.today()):
        """ Returns a weighted crop factor: each land cover's crop factor is
        weighted according to the fraction it contributes to the total area.
        """

        ## Each instance has a set of LandCoverData (LCD).
        ## Caching its elements is worthwhile.

        key = "%s.LCD" % self.afdeling
        lcd = cache.get(key)

        if not lcd:

            ## Without select_related() the database will be hit each
            ## time we navigate over cover in the for loop below!

            lcd = tuple(self.landcoverdata_set.select_related('cover'))
            cache.set(key, lcd)

        factor = 0

        for land in lcd:
            factor += land.fraction * land.cover.get_cropfactor(date)

        return factor


class LandCover(models.Model):
    """ Land cover is the physical material or vegetation at the surface
    of the earth. For example: corn, forest, grass, water, etc.
    """
    name = models.CharField(max_length=64, unique=True)

    def get_cropfactor(self, date=date.today()):
        """ Returns the crop factor - the value that is, not the object -
        for this particular type of land cover at the specified date.
        """

        ## Given the application, it's highly likely that we'll also
        ## need crop factors for other types of land cover at this
        ## date. We'll get them all at once and cache them for
        ## efficiency.

        key = "CF" + date.strftime(".%m%d") ## E.g. CF.0403
        value = cache.get(key) ## Crop factors (dict)

        if not value:
            cfs = CropFactor.objects.filter(month=date.month, day=date.day)
            value = dict((cf.crop_id, cf.factor) for cf in cfs)
            cache.set(key, value)

        return value[self.pk]


class LandCoverData(models.Model):
    """ Each geographical region can be characterized according to its
    land cover. For example: the province of Utrecht has 2% corn,
    10% forest, etc. The class LandCoverData describes how much
    a type of cover contributes to a total region (in % area).
    """
    region = models.ForeignKey(WaterRegimeShape)
    cover = models.ForeignKey(LandCover)
    fraction = models.FloatField()

    class Meta:
        unique_together = (("region", "cover"),)


class CropFactor(models.Model):
    """ Factor to correct the evaporation of a reference area for a
    certain vegetation. Since vegetation is a seasonal feature,
    crop factors generally do vary over the days of a year.

    For our purpose, a Penman factor can be considered as a crop
    factor for open water. Since the distinction is irrelevant,
    Penman factors are modeled accordingly.
    """
    crop = models.ForeignKey(LandCover)
    month = models.SmallIntegerField()
    day = models.SmallIntegerField()
    factor = models.FloatField()

    class Meta:
        unique_together = (("crop", "month", "day"),)


class TimeSeriesFactory(models.Model):
    """ Factory class responsible for creating time series.
    """
    series_name = models.CharField(max_length=64, unique=True)
    class_name = models.CharField(max_length=64)

    @classmethod
    def get(cls, series_name):
        """ Factory method that returns a time series. In this way, clients
        can remain ignorant to the concrete class and database used. For
        example: events = TimeSeriesFactory.get("P").events()
        """
        class_name = cls.objects.get(series_name=series_name).class_name
        return eval(class_name).objects.get(name=series_name)


class TimeSeries(object):
    """ Super class of all TimeSeries implementations. Not to be instantiated
    directly: should be considered as an abstract base class.
    """

    def events(self, start=datetime.min, end=datetime.max, missing=None):
        """ Returns all events between [start, end]. By default, any
        missing values between the first and last event are replaced
        by None. Magic values, e.g. -999.0, are not considered as
        missing - only datetimes that are completely absent.
        This might be better handled at the fews level?

        This method makes quite some assumptions about the data:

        1) Events are spaced at uniform time intervals.
        2) Naive datetime objects (no timezone).
        3) All datetimes are nicely rounded.
        4) Events are in ascending order.

        For example:

        2011-04-01 09:00,  123.4
        2011-04-01 11:00, -999.0

        becomes:

        2011-04-01 09:00,  123.4
        2011-04-01 10:00,  None
        2011-04-01 11:00, -999.0

        """
        next = datetime.max
        delta = timedelta(hours=self.hours)
        for time, value in self.raw_events(start, end):
            while next < time:
                yield next, missing
                next += delta
            yield time, value
            next = time + delta


class DefaultTimeSeries(models.Model, TimeSeries):
    """ Represents a time series, i.e. a sequence of time series
    events (or data points) measured at successive times.
    Data is physically located in the default database.
    """
    name = models.CharField(max_length=64, unique=True)
    hours = models.IntegerField() ## timedelta

    def raw_events(self, start=datetime.min, end=datetime.max):
        """
        """
        for event in self.timeseriesevent_set.\
            only('datetime', 'value').\
            filter(datetime__range=(start, end)):
            yield event.datetime, event.value


class TimeSeriesEvent(models.Model):
    """ Represents a value measured at a particular point in
    time. Successive events together form a time series.
    """
    time_series = models.ForeignKey(DefaultTimeSeries)
    datetime = models.DateTimeField()
    value = models.FloatField()

    class Meta:
        unique_together = (("time_series", "datetime"),)
        ordering = ("datetime",)


class FewsTimeSeries(models.Model, TimeSeries):
    """ Represents a time series, i.e. a sequence of time series
    events (or data points) measured at successive times.
    Data is physically located in the fews database.
    """
    name = models.CharField(max_length=64, unique=True)
    hours = models.IntegerField() ## timedelta

    ## Fews timeseries are uniquely defined by the following 5
    ## fields. We do rely on primary keys, because these may
    ## vary across imports.
    moduleinstanceid = models.CharField(max_length=64)
    timestep = models.CharField(max_length=64)
    fid = models.CharField(max_length=64)
    lid = models.CharField(max_length=64)
    pid = models.CharField(max_length=64)

    def raw_events(self, start=datetime.min, end=datetime.max):
        """
        """
        fpk = Filter.objects.only('fews_id').get(fews_id=self.fid).pk
        lpk = Location.objects.only('id').get(id=self.lid).pk
        ppk = Parameter.objects.only('id').get(id=self.pid).pk

        timeseries = Timeserie.objects.get(
            moduleinstanceid=self.moduleinstanceid,
            timestep=self.timestep,
            filterkey=fpk,
            locationkey=lpk,
            parameterkey=ppk)

        for event in timeseries.timeseriedata.only('tsd_time', 'tsd_value').\
            filter(tsd_time__range=(start, end)).order_by('tsd_time'):
            yield event.tsd_time, event.tsd_value

    class Meta:
        unique_together = (("moduleinstanceid", "timestep",
            "fid", "lid", "pid"),)


class Constant(models.Model):
    """ This class represents some "constants" used in the various formulas.
    As per requirement, they have to be modifiable by a user/administrator.
    """
    name = models.CharField(max_length=64, unique=True)
    value = models.FloatField()
    description = models.CharField(max_length=128, unique=True)

    @classmethod
    def get(cls, name):
        """ Returns the value of the constant or None if no constant
        by this name is known.
        """
        try:
            return cls.objects.get(name=name).value
        except Constant.DoesNotExist:
            return None


class Regime(models.Model):
    name = models.CharField(max_length=16)
    color255 = models.CommaSeparatedIntegerField(max_length=11)
    order = models.IntegerField()

    def color_255(self):
        """Return an rgb color tuple in the (255,255,255) format."""
        return tuple(map(int,self.color255.split(',')))

    def color_rgba(self):
        """Return an rgba color tuple in the (1,1,1,1) format."""
        return tuple([c/255. for c in self.color_255()] + [1])
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['order']
    

class Season(models.Model):
    name = models.CharField(max_length=32)
    month_from = models.IntegerField()
    day_from = models.IntegerField()
    month_to = models.IntegerField()
    day_to = models.IntegerField()
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['month_from','day_from']

class Range(models.Model):
    regime = models.ForeignKey(Regime)
    season = models.ForeignKey(Season)
    # limits refer to the 'neerslagoverschot'
    lower_limit = models.DecimalField(
        max_digits = 4, decimal_places = 1, null = True, blank = True
    )
    upper_limit = models.DecimalField(
        max_digits = 4, decimal_places = 1, null = True, blank = True
    )

class PrecipitationSurplus(models.Model):
    waterregimeshape = models.ForeignKey(WaterRegimeShape)
    date = models.DateTimeField(db_index = True)
    value = models.FloatField()

