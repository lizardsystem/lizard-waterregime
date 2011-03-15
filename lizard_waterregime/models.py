# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# from django.db import models

# Create your models here.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.contrib.gis.db import models

class AfdelingenDissolve(models.Model):
    gid = models.IntegerField(primary_key=True)
    afdeling = models.CharField(max_length=5)
    naam = models.CharField(max_length=50)
    area_m2 = models.DecimalField(max_digits=65535, decimal_places=65535)
    the_geom = models.MultiPolygonField(srid=-1)
    objects = models.GeoManager()
    class Meta:
        db_table = u'afdelingen_dissolve'

