import mapnik
from django.conf import settings
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

        def mapnik_rule(r, g, b, a, mapnik_filter=None):
            """
            Makes mapnik rule for looks. For lines and polygons.

            From lizard_map.models.
            """
            rule = mapnik.Rule()
            if mapnik_filter is not None:
                rule.filter = mapnik.Filter(mapnik_filter)
            mapnik_color = mapnik.Color(r, g, b, a)
            mapnik_stroke_color = mapnik.Color(r, g, b)

            symb_line = mapnik.LineSymbolizer(mapnik_stroke_color, 1)
            rule.symbols.append(symb_line)

            symb_poly = mapnik.PolygonSymbolizer(mapnik_color)
            symb_poly.fill_opacity = .8
            rule.symbols.append(symb_poly)
            return rule

        mapnik_style = mapnik.Style()
        rule = mapnik_rule(255, 255, 0, 128)
        mapnik_style.rules.append(rule)
        # for gid in range(100):
        #     rule = mapnik_rule(0, 10 * gid ,0, '[gid] = %d' % gid)
        #     mapnik_style.rules.append(rule)
        rule = mapnik_rule(0, 255, 0, 128, '[value] <= 75')
        mapnik_style.rules.append(rule)
        rule = mapnik_rule(255, 0, 0, 128, '[value] > 75')
        mapnik_style.rules.append(rule)
        return mapnik_style

    def layer(self, layer_ids=None, request=None):
        """Generates and returns mapnik layers and styles.
        """
        
        layers = []
        styles = {}

        db_settings = settings.DATABASES['default']
        gid = self.layer_arguments["layer"]
#        table_view = '(select gid, the_geom, 100 as value from water_regime_shape where gid=%s) result_view' % gid
        table_view = '(select gid, the_geom, gid * 30 as value from water_regime_shape) result_view'

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
