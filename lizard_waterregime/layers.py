import logging
import mapnik
import os
from datetime import datetime

from django.conf import settings
from lizard_map import coordinates
from lizard_map import adapter
from lizard_map.models import ICON_ORIGINALS

from lizard_map.coordinates import RD
from lizard_map.workspace import WorkspaceItemAdapter
from lizard_map.symbol_manager import SymbolManager

from lizard_waterregime.models import WaterRegimeShape

log = logging.getLogger('nens.waterregimeadapter')

class AdapterWaterRegime(WorkspaceItemAdapter):
    """Adapter for module lizard_waterregime.

    Registered as adapter_waterregime.

    Uses default database table "water_regime_shape" as geo database.
    """

    COLOR = {
    # zeer droog komt niet voor in grenswaardentabel
    #   'zeer droog':(226, 108,  10),
        'droog'     :(249, 191, 143),
        'gemiddeld' :(219, 229, 241),
        'nat'       :(149, 179, 215),
        'zeer nat'  :( 53,  95, 145),
    }
    # nu gebaseerd op gewogen neerslagoverschot (p-e?)
    # alleen geldig binnen groeiseizoen, zie grenswaardentabel

    FILTER = {
    # zeer droog komt niet voor in grenswaardentabel
    #    'zeer droog':'                 [value] <= -4',
         'droog'     :'                 [value] <= -4', 
         'gemiddeld' :'[value] > -4 and [value] <=  7', 
         'nat'       :'[value] >  7 and [value] <= 10', 
         'zeer nat'  :'[value] >  10                 ', 
    }

    def _mapnik_style(self):
        """
        Temp function to return a default mapnik style
        """

        def mapnik_rule(color, mapnik_filter=None):
            """
            Makes mapnik rule for looks. For lines and polygons.

            From lizard_map.models.
            """
            rule = mapnik.Rule()
            if mapnik_filter is not None:
                rule.filter = mapnik.Filter(mapnik_filter)
            mapnik_color = mapnik.Color(*color)

            symb_line = mapnik.LineSymbolizer(mapnik_color, 2)
            rule.symbols.append(symb_line)

            symb_poly = mapnik.PolygonSymbolizer(mapnik_color)
            symb_poly.fill_opacity = .8
            rule.symbols.append(symb_poly)
            return rule

        mapnik_style = mapnik.Style()
        mapnik_style.rules.extend([
            mapnik_rule(self.COLOR[key],self.FILTER[key])
            for key in self.COLOR.keys()
        ])
        return mapnik_style

    def layer(self, layer_ids=None, request=None):
        """Generates and returns mapnik layers and styles.
        """
        
        layers = []
        styles = {}

        db_settings = settings.DATABASES['default']
        table_view = """(
            select
                gid,
                afdeling,
                naam,
                area_m2,
                the_geom,
                gid * 5 - 12 as value
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
        """Search by coordinates, return matching items as list of dicts

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
                u'Area: %i km\u00b2' % round(feature.properties['area_m2'] * 1e-6),
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
        
    def html(self, snippet_group=None, identifiers=None, layout_options=None):
        """
        Html output for given identifiers. Optionally layout_options
        can be provided. Default layout_options:

        layout_options = {'add_snippet': False,
                         'editing': False}
        """
        return super(AdapterWaterRegime, self).html_default(
            snippet_group=snippet_group,
            identifiers=identifiers,
            layout_options=layout_options)        
            
    def location(self, afdeling, google_x, google_y, layout=None):
        """Lookup 'peilgebied' by 'afdeling'

        """
        shape = WaterRegimeShape.objects.get(afdeling=afdeling)
        gid = shape.gid
        identifier = {
            'afdeling': afdeling,
            'google_x': google_x,
            'google_y': google_y,
        }

        return {
            'name': 'Peilgebied: ' + afdeling,
            'shortname': afdeling,
            'object': None, # what object? --  TODO?
            'workspace_item': self.workspace_item,
            'google_coords': (google_x, google_y),
            'identifier': identifier,
            }

    def image(self, identifier_list,
              start_date, end_date,
              width=None, height=None,
              layout_extra=None):
        """
        visualizes scores or measures in a graph

        each row is an area
        """
        if width is None:
            width = 380.0
        if height is None:
            height = 170.0

        graph = adapter.Graph(start_date, end_date, width, height)
        graph.add_today()

        # Find database object that contains the timeseries data.
        """From fewsunblobbed:
        timeserie = fews_timeserie(
            self.filterkey,
            identifier['locationkey'],
            self.parameterkey)
        timeseriedata = timeserie.timeseriedata.filter(
            tsd_time__gte=start_date,
            tsd_time__lte=end_date)
         """

        # Plot testdata.
        from numpy import sin, cos
        from numpy import arange

        dates = [datetime(2011,3,x) for x in range(1,20)]

        values1 = [float(y) for y in sin(arange(1,20)/4.)]
        values2 = [float(y) for y in cos(arange(1,20)/4.)]
        values3 = [a-b for a,b in zip(values1,values2)]

        graph.axes.plot(dates, values1)
        graph.axes.plot(dates, values2)
        graph.axes.plot(dates, values3)


        return graph.http_png()
        
    def symbol_url(self, identifier=None, start_date=None, end_date=None,
                   icon_style=None):
        """Return symbol for identifier.

        Implementation: respect the fact when icon_style is already
        given. If it's empty, generate own icon if applicable.
        """
        sm = SymbolManager(ICON_ORIGINALS, os.path.join(
                settings.MEDIA_ROOT,
                'generated_icons'))
        if icon_style is None:
            icon_style = {
                'icon': 'empty.png',
                'color': (1.0,0.5,0.5,0),
            }
        output_filename = sm.get_symbol_transformed(icon_style['icon'],
                                                    **icon_style)
        return settings.MEDIA_URL + 'generated_icons/' + output_filename   
        
    def legend(self, updates=None):
        """Return a legend in a list of dictionaries."""

        legend_result = []

        for key in self.COLOR.keys():
            log.debug(key)
            log.debug(self.COLOR[key])
            color = [component/255. for component in self.COLOR[key]]
            log.debug(color)
            color.append(1)
            log.debug(color)
            img_url = self.symbol_url(
                icon_style = {
                    'icon': 'empty.png',
                    'color': color,
                }
            )
            description = key
            legend_result.append({
                'img_url': img_url, 
                'description': description,
            })
       
        return legend_result

