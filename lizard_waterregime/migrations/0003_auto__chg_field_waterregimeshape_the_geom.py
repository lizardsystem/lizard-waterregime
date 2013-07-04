# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'WaterRegimeShape.the_geom'
        db.alter_column('lizard_waterregime_waterregimeshape', 'the_geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=28992))

    def backwards(self, orm):

        # Changing field 'WaterRegimeShape.the_geom'
        db.alter_column('lizard_waterregime_waterregimeshape', 'the_geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=-1))

    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'lizard_waterregime.constant': {
            'Meta': {'object_name': 'Constant'},
            'description': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        'lizard_waterregime.cropfactor': {
            'Meta': {'unique_together': "(('crop', 'month', 'day'),)", 'object_name': 'CropFactor'},
            'crop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_waterregime.LandCover']"}),
            'day': ('django.db.models.fields.SmallIntegerField', [], {}),
            'factor': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'lizard_waterregime.defaulttimeseries': {
            'Meta': {'object_name': 'DefaultTimeSeries'},
            'hours': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'lizard_waterregime.fewstimeseries': {
            'Meta': {'unique_together': "(('moduleinstanceid', 'timestep', 'fid', 'lid', 'pid'),)", 'object_name': 'FewsTimeSeries'},
            'fid': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'hours': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lid': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'moduleinstanceid': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'pid': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'timestep': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'lizard_waterregime.landcover': {
            'Meta': {'object_name': 'LandCover'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'lizard_waterregime.landcoverdata': {
            'Meta': {'unique_together': "(('region', 'cover'),)", 'object_name': 'LandCoverData'},
            'cover': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_waterregime.LandCover']"}),
            'fraction': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_waterregime.WaterRegimeShape']"})
        },
        'lizard_waterregime.precipitationsurplus': {
            'Meta': {'object_name': 'PrecipitationSurplus'},
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'valid': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'value': ('django.db.models.fields.FloatField', [], {}),
            'waterregimeshape': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_waterregime.WaterRegimeShape']"})
        },
        'lizard_waterregime.range': {
            'Meta': {'object_name': 'Range'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lower_limit': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '1', 'blank': 'True'}),
            'regime': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_waterregime.Regime']"}),
            'season': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_waterregime.Season']"}),
            'upper_limit': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '1', 'blank': 'True'})
        },
        'lizard_waterregime.regime': {
            'Meta': {'ordering': "['order']", 'object_name': 'Regime'},
            'color255': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '11'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'order': ('django.db.models.fields.IntegerField', [], {})
        },
        'lizard_waterregime.season': {
            'Meta': {'ordering': "['month_from', 'day_from']", 'object_name': 'Season'},
            'day_from': ('django.db.models.fields.IntegerField', [], {}),
            'day_to': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month_from': ('django.db.models.fields.IntegerField', [], {}),
            'month_to': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'lizard_waterregime.timeseriesevent': {
            'Meta': {'ordering': "('datetime',)", 'unique_together': "(('time_series', 'datetime'),)", 'object_name': 'TimeSeriesEvent'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_series': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_waterregime.DefaultTimeSeries']"}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        'lizard_waterregime.timeseriesfactory': {
            'Meta': {'object_name': 'TimeSeriesFactory'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'series_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'lizard_waterregime.waterregimeshape': {
            'Meta': {'object_name': 'WaterRegimeShape'},
            'afdeling': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '5'}),
            'area_m2': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '10'}),
            'gid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'naam': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'the_geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '28992'})
        }
    }

    complete_apps = ['lizard_waterregime']