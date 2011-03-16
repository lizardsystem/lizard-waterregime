# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# from django.db import models

# Create your models here.

from django.contrib.gis.db import models

class WaterRegimeShape(models.Model):
    gid = models.IntegerField(primary_key=True)
    afdeling = models.CharField(max_length=5)
    naam = models.CharField(max_length=50)
    area_m2 = models.DecimalField(max_digits=65535, decimal_places=65535)
    the_geom = models.MultiPolygonField(srid=-1)
    objects = models.GeoManager()
    class Meta:
        db_table = u'water_regime_shape'

