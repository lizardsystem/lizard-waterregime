import mapnik
from django.conf import settings
from lizard_map import coordinates
from lizard_map.coordinates import RD
from lizard_map.workspace import WorkspaceItemAdapter


class AdapterWaterRegime(WorkspaceItemAdapter):
    """Adapter for module lizard_waterregime.

    Registered as adapter_waterregime.

    Uses default database table "water_regime_shape" as geo database.
    """

    def _mapnik_style(self):
        """
        Temp function to return a default mapnik style
        """

        def mapnik_rule(r, g, b, mapnik_filter=None):
            """
            Makes mapnik rule for looks. For lines and polygons.

            From lizard_map.models.
            """
            rule = mapnik.Rule()
            if mapnik_filter is not None:
                rule.filter = mapnik.Filter(mapnik_filter)
            mapnik_color = mapnik.Color(r, g, b)

            symb_line = mapnik.LineSymbolizer(mapnik_color, 1)
            rule.symbols.append(symb_line)

            symb_poly = mapnik.PolygonSymbolizer(mapnik_color)
            symb_poly.fill_opacity = .2
            rule.symbols.append(symb_poly)
            return rule

        mapnik_style = mapnik.Style()
        rule = mapnik_rule(255, 255, 0)
        mapnik_style.rules.append(rule)
        # for gid in range(100):
        #     rule = mapnik_rule(0, 10 * gid ,0, '[gid] = %d' % gid)
        #     mapnik_style.rules.append(rule)
        rule = mapnik_rule(0, 0, 255, '[value] <= 75')
        mapnik_style.rules.append(rule)
        rule = mapnik_rule(255, 0, 0, '[value] > 75')
        mapnik_style.rules.append(rule)
        return mapnik_style

    def layer(self, layer_ids=None, request=None):
        """ Generates and returns mapnik layers and styles.
        """
        
        layers = []
        styles = {}

        db_settings = settings.DATABASES['default']
        table_view = """ (
            select
                gid,
                afdeling,
                naam,
                area_m2,
                the_geom,
                gid * 30 as value
            from
                water_regime_shape) result_view
        """
        layer = mapnik.Layer('Geometry from PostGIS')
        layer.srs = RD  #GOOGLE
        layer.datasource = mapnik.PostGIS(
            host=db_settings['HOST'],
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            dbname=db_settings['NAME'],
            table=str(table_view))
        layers.append(layer)

        style_name = 'waterregime_style'
        layer.styles.append(style_name)
        mapnik_style = self._mapnik_style()
        styles[style_name] = mapnik_style

        return layers, styles
        
    def search(self, google_x, google_y, radius=None):
        """ Search by coordinates, return matching items as list of dicts

        Required in result:
            distance, name, workspace_item, google_coords
        Highly recommended (else some functions will not work):
            identifier (for popups)

        Hacky at the moment as searching shapefiles is harder than
        expected. Copied from lizard_map.layers.py """

        result = []

        # Set up a basic map as only map can search...
        mapnik_map = mapnik.Map(400, 400)
        mapnik_map.srs = coordinates.GOOGLE

        layers, styles = self.layer()
        for layer in layers:
            mapnik_map.layers.append(layer)
        for name in styles:
            mapnik_map.append_style(name, styles[name])
        # 0 is the first layer.
        feature_set = mapnik_map.query_point(0, google_x, google_y)

        for feature in feature_set.features:
            afdeling = feature.properties['afdeling']
            gid = feature.properties['gid']
            popup_string = '<br />'.join([
                afdeling,
                'Area: %s km2' % int(feature.properties['area_m2'] * 10e-6),
                'Value: %s' % feature.properties['value'],
            ])
            identifier = {
                'afdeling': afdeling,
                'google_x': google_x,
                'google_y': google_y,
            }
            single_result = {
                'distance': 0.0,
                'object': gid,
                'name': popup_string,
                'shortname': afdeling,
                'google_coords': (google_x, google_y),
                'workspace_item': self.workspace_item,
                'identifier': identifier,
            }
            result.append(single_result)
        return result        
