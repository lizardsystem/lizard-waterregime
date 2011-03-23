import logging
import mapnik
import os
from datetime import datetime

from django.core.urlresolvers import reverse
from django.conf import settings

from lizard_map import coordinates
from lizard_map import adapter
from lizard_map.models import ICON_ORIGINALS
from lizard_map.coordinates import RD
from lizard_map.workspace import WorkspaceItemAdapter
from lizard_map.symbol_manager import SymbolManager

from lizard_waterregime.models import WaterRegimeShape

logger = logging.getLogger('nens.waterregimeadapter')

class AdapterWaterRegime(WorkspaceItemAdapter):
    """Adapter for module lizard_waterregime.

    Registered as adapter_waterregime.

    Uses default database table "water_regime_shape" as geo database.
    """

    REGIMES = [{
    # zeer droog komt niet voor in grenswaardentabel
    # nu gebaseerd op gewogen neerslagoverschot (p-e?)
    # alleen geldig binnen groeiseizoen, zie grenswaardentabel
        'regime': 'Zeer droog',
        'color': (226, 108,  10),
        'lower_limit': None,
        'upper_limit': -400,
    },{
        'regime': 'Droog',
        'color': (249, 191, 143),
        'lower_limit': None,
        'upper_limit': -4,
    },{
        'regime': 'Gemiddeld',
        'color': (219, 229, 241),
        'lower_limit': -4,
        'upper_limit': 7,
    },{
        'regime': 'Nat',
        'color': (149, 179, 215),
        'lower_limit': 7,
        'upper_limit': 10,
    },{
        'regime': 'Zeer nat',
        'color': ( 53,  95, 145),
        'lower_limit': 10,
        'upper_limit': None,
    }]
    
    # Generate mapnik filters
    for regime in REGIMES:
        filter =''
        if regime['lower_limit']:
            filter += '[value] > ' + str(regime['lower_limit'])
        if regime['lower_limit'] and regime['upper_limit']:
            filter += ' and '
        if regime['upper_limit']:
            filter += '[value] <= ' + str(regime['upper_limit'])
        regime['mapnik_filter'] = filter    
        
        


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
            mapnik_rule(regime['color'],regime['mapnik_filter'])
            for regime in self.REGIMES
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
                lizard_waterregime_waterregimeshape) result_view
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
            popup_string = (
                'Peilgebied %s, waarde: %i' % (
                    afdeling, feature.properties['value'])
            )
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

        graph_img_url = reverse(
            "lizard_waterregime.workspace_item_graph_image",
            kwargs={'workspace_item_id': self.workspace_item.id},
            )
        bar_img_url = reverse(
            "lizard_waterregime.workspace_item_bar_image",
            kwargs={'workspace_item_id': self.workspace_item.id},
            )

        return super(AdapterWaterRegime, self).html_default(
            snippet_group=snippet_group,
            identifiers=identifiers,
            layout_options=layout_options,
            template='lizard_waterregime/popup.html',
            extra_render_kwargs={
                'graph_img_url':graph_img_url,
                'bar_img_url':bar_img_url,
            }
        )        
            
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

    def graph_image(self, identifier_list,
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

    def bar_image(self, identifier_list, start_date, end_date,              
        width=None, height=None, layout_extra=None):
        """Return a colored bar representing the regime against the time."""

        if width is None:
            width = 380.0
        if height is None:
            height = 170.0

        # Data TODO get with real data...
        from numpy.random import rand
        from numpy import arange
        dates = [datetime(2011,3,x) for x in range(1,30)]
        values = [int(round(y)) for y in 20*rand(29)-4]


        graph = adapter.Graph(start_date, end_date, width, height)
        graph.add_today()

        # Make a nice broken_barh:
        """
        Loop this:
        ax.broken_barh([ (date, ), (150, 10) ] , (10, 9), facecolor=(0,0,0))

        xranges = [(date.replace(hour=1),
            date.replace(hour=23)) for date in dates]
        facecolors=
        yrange = ()   
        c
        
        #Value to color function: Just loop the regimes every time? Seems slow to me.
        [list of ranges around date.]
        list of colors
                
        graph.axes.broken_barh([ (10, 50), (100, 20),  (130, 10)] , (20, 9),
                        facecolors=('red', 'yellow', 'green'))
        graph.axes.set_ylim(0,10)
        graph.axes.set_yticks([5])
        graph.axes.set_yticklabels(['Regime'])
        """

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
                'color': (0.5,1.0,0.5,0),
            }
        output_filename = sm.get_symbol_transformed(icon_style['icon'],
                                                    **icon_style)
        return settings.MEDIA_URL + 'generated_icons/' + output_filename   
        
    def legend(self, updates=None):
        """Return a legend in a list of dictionaries."""

        legend_result = []

        for regime in self.REGIMES:
            color = [component/255. for component in regime['color']]
            color.append(1)
            img_url = self.symbol_url(
                icon_style = {
                    'icon': 'empty.png',
                    'color': color,
                }
            )
            description = regime['regime']
            legend_result.append({
                'img_url': img_url, 
                'description': description,
            })
       
        return legend_result

