# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'WaterRegimeShape'
        db.create_table('lizard_waterregime_waterregimeshape', (
            ('gid', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('afdeling', self.gf('django.db.models.fields.CharField')(unique=True, max_length=5)),
            ('naam', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('area_m2', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=10)),
            ('the_geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=-1)),
        ))
        db.send_create_signal('lizard_waterregime', ['WaterRegimeShape'])

        # Adding model 'LandCover'
        db.create_table('lizard_waterregime_landcover', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
        ))
        db.send_create_signal('lizard_waterregime', ['LandCover'])

        # Adding model 'LandCoverData'
        db.create_table('lizard_waterregime_landcoverdata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_waterregime.WaterRegimeShape'])),
            ('cover', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_waterregime.LandCover'])),
            ('fraction', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('lizard_waterregime', ['LandCoverData'])

        # Adding unique constraint on 'LandCoverData', fields ['region', 'cover']
        db.create_unique('lizard_waterregime_landcoverdata', ['region_id', 'cover_id'])

        # Adding model 'CropFactor'
        db.create_table('lizard_waterregime_cropfactor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('crop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_waterregime.LandCover'])),
            ('month', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('day', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('factor', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('lizard_waterregime', ['CropFactor'])

        # Adding unique constraint on 'CropFactor', fields ['crop', 'month', 'day']
        db.create_unique('lizard_waterregime_cropfactor', ['crop_id', 'month', 'day'])

        # Adding model 'TimeSeriesFactory'
        db.create_table('lizard_waterregime_timeseriesfactory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('series_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('lizard_waterregime', ['TimeSeriesFactory'])

        # Adding model 'DefaultTimeSeries'
        db.create_table('lizard_waterregime_defaulttimeseries', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('hours', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('lizard_waterregime', ['DefaultTimeSeries'])

        # Adding model 'TimeSeriesEvent'
        db.create_table('lizard_waterregime_timeseriesevent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time_series', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_waterregime.DefaultTimeSeries'])),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('value', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('lizard_waterregime', ['TimeSeriesEvent'])

        # Adding unique constraint on 'TimeSeriesEvent', fields ['time_series', 'datetime']
        db.create_unique('lizard_waterregime_timeseriesevent', ['time_series_id', 'datetime'])

        # Adding model 'FewsTimeSeries'
        db.create_table('lizard_waterregime_fewstimeseries', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('hours', self.gf('django.db.models.fields.IntegerField')()),
            ('moduleinstanceid', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('timestep', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('fid', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('lid', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('pid', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('lizard_waterregime', ['FewsTimeSeries'])

        # Adding unique constraint on 'FewsTimeSeries', fields ['moduleinstanceid', 'timestep', 'fid', 'lid', 'pid']
        db.create_unique('lizard_waterregime_fewstimeseries', ['moduleinstanceid', 'timestep', 'fid', 'lid', 'pid'])

        # Adding model 'Constant'
        db.create_table('lizard_waterregime_constant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('value', self.gf('django.db.models.fields.FloatField')()),
            ('description', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('lizard_waterregime', ['Constant'])

        # Adding model 'Regime'
        db.create_table('lizard_waterregime_regime', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('color255', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=11)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('lizard_waterregime', ['Regime'])

        # Adding model 'Season'
        db.create_table('lizard_waterregime_season', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('month_from', self.gf('django.db.models.fields.IntegerField')()),
            ('day_from', self.gf('django.db.models.fields.IntegerField')()),
            ('month_to', self.gf('django.db.models.fields.IntegerField')()),
            ('day_to', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('lizard_waterregime', ['Season'])

        # Adding model 'Range'
        db.create_table('lizard_waterregime_range', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('regime', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_waterregime.Regime'])),
            ('season', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_waterregime.Season'])),
            ('lower_limit', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=4, decimal_places=1, blank=True)),
            ('upper_limit', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=4, decimal_places=1, blank=True)),
        ))
        db.send_create_signal('lizard_waterregime', ['Range'])

        # Adding model 'PrecipitationSurplus'
        db.create_table('lizard_waterregime_precipitationsurplus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('waterregimeshape', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_waterregime.WaterRegimeShape'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('value', self.gf('django.db.models.fields.FloatField')()),
            ('valid', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('lizard_waterregime', ['PrecipitationSurplus'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'FewsTimeSeries', fields ['moduleinstanceid', 'timestep', 'fid', 'lid', 'pid']
        db.delete_unique('lizard_waterregime_fewstimeseries', ['moduleinstanceid', 'timestep', 'fid', 'lid', 'pid'])

        # Removing unique constraint on 'TimeSeriesEvent', fields ['time_series', 'datetime']
        db.delete_unique('lizard_waterregime_timeseriesevent', ['time_series_id', 'datetime'])

        # Removing unique constraint on 'CropFactor', fields ['crop', 'month', 'day']
        db.delete_unique('lizard_waterregime_cropfactor', ['crop_id', 'month', 'day'])

        # Removing unique constraint on 'LandCoverData', fields ['region', 'cover']
        db.delete_unique('lizard_waterregime_landcoverdata', ['region_id', 'cover_id'])

        # Deleting model 'WaterRegimeShape'
        db.delete_table('lizard_waterregime_waterregimeshape')

        # Deleting model 'LandCover'
        db.delete_table('lizard_waterregime_landcover')

        # Deleting model 'LandCoverData'
        db.delete_table('lizard_waterregime_landcoverdata')

        # Deleting model 'CropFactor'
        db.delete_table('lizard_waterregime_cropfactor')

        # Deleting model 'TimeSeriesFactory'
        db.delete_table('lizard_waterregime_timeseriesfactory')

        # Deleting model 'DefaultTimeSeries'
        db.delete_table('lizard_waterregime_defaulttimeseries')

        # Deleting model 'TimeSeriesEvent'
        db.delete_table('lizard_waterregime_timeseriesevent')

        # Deleting model 'FewsTimeSeries'
        db.delete_table('lizard_waterregime_fewstimeseries')

        # Deleting model 'Constant'
        db.delete_table('lizard_waterregime_constant')

        # Deleting model 'Regime'
        db.delete_table('lizard_waterregime_regime')

        # Deleting model 'Season'
        db.delete_table('lizard_waterregime_season')

        # Deleting model 'Range'
        db.delete_table('lizard_waterregime_range')

        # Deleting model 'PrecipitationSurplus'
        db.delete_table('lizard_waterregime_precipitationsurplus')


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
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
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
            'the_geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '-1'})
        }
    }

    complete_apps = ['lizard_waterregime']
