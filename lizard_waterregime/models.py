# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# from django.db import models

# Create your models here.

from datetime import datetime
from django.contrib.gis.db import models
from lizard_fewsunblobbed.models import Filter
from lizard_fewsunblobbed.models import Location
from lizard_fewsunblobbed.models import Parameter
from lizard_fewsunblobbed.models import Timeserie


class WaterRegimeShape(models.Model):
    gid = models.IntegerField(primary_key=True)
    afdeling = models.CharField(max_length=5)
    naam = models.CharField(max_length=50)
    area_m2 = models.DecimalField(max_digits=20, decimal_places=10)
    the_geom = models.MultiPolygonField(srid= -1)
    objects = models.GeoManager()


class LandCover(models.Model):
    """ Land cover is the physical material or vegetation at the surface
    of the earth. For example: corn, forest, grass, water, etc.
    """
    name = models.CharField(max_length=64, unique=True)

    def get_cropfactor(self, date):
        try:
            obj = self.cropfactor_set.get(month=date.month, day=date.day)
        except CropFactor.DoesNotExist:
            obj = None
        return obj


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


class DefaultTimeSeries(models.Model):
    """ Represents a time series, i.e. a sequence of time series
    events (or data points) measured at successive times.
    Data is physically located in the default database.
    """
    name = models.CharField(max_length=64, unique=True)

    def events(self, start=datetime.min, end=datetime.max):
        """
        """
        for event in self.timeseriesevent_set.filter(
            datetime__range=(start, end)):
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


class FewsTimeSeries(models.Model):
    """ Represents a time series, i.e. a sequence of time series
    events (or data points) measured at successive times.
    Data is physically located in the fews database.
    """
    name = models.CharField(max_length=64, unique=True)
    ## By design, a fews time series is not uniquely defined by
    ## fid, lid, and pid. The next 2 fields are required too?
    moduleinstanceid = models.CharField(max_length=64)
    timestep = models.CharField(max_length=64)
    ## Alternative keys are stored instead of the primary keys,
    ## because the former are considered more stable.
    fid = models.CharField(max_length=64)
    lid = models.CharField(max_length=64)
    pid = models.CharField(max_length=64)

    def events(self, start=datetime.min, end=datetime.max):
        """
        """
        fpk = Filter.objects.get(id=self.fid).pk
        lpk = Location.objects.get(id=self.lid).pk
        ppk = Parameter.objects.get(id=self.pid).pk

        timeseries = Timeserie.objects.get(
            moduleinstanceid=self.moduleinstanceid,
            timestep=self.timestep,
            filterkey=fpk,
            locationkey=lpk,
            parameterkey=ppk)

        for event in timeseries.timeseriesdata.filter(
            tsd_time__range=(start, end)).order_by('tsd_time'):
            yield event.tsd_time, event.tsd_value

    class Meta:
        unique_together = (("moduleinstanceid", "timestep",
            "fid", "lid", "pid"),)
