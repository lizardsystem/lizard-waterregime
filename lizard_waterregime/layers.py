import logging
import mapnik
import os
from datetime import datetime
from datetime import timedelta
from matplotlib.dates import date2num
from matplotlib.dates import num2date

from django.core.urlresolvers import reverse
from django.conf import settings

from lizard_map import coordinates
from lizard_map import adapter
from lizard_map.models import ICON_ORIGINALS
from lizard_map.coordinates import RD
from lizard_map.workspace import WorkspaceItemAdapter
from lizard_map.symbol_manager import SymbolManager

from lizard_waterregime.models import WaterRegimeShape
from lizard_waterregime.models import Regime

logger = logging.getLogger('nens.waterregimeadapter')

class AdapterWaterRegime(WorkspaceItemAdapter):
    """Adapter for module lizard_waterregime.

    Registered as adapter_waterregime.

    Uses default database table "water_regime_shape" as geo database.
    """
    # To be moved to table lizard_waterregime_regimes
    REGIMES = [{
    # nu gebaseerd op gewogen neerslagoverschot (p-e?)
    # alleen geldig binnen groeiseizoen, zie grenswaardentabel
        'regime': 'Droog',
#       'color_255': (249, 191, 143),
        'color_255': (225,  89,  47),
        'lower_limit': None,
        'upper_limit': -4,
    },{
        'regime': 'Gemiddeld',
        'color_255': (219, 229, 241),
        'lower_limit': -4,
        'upper_limit': 7,
    },{
        'regime': 'Nat',
        'color_255': (149, 179, 215),
        'lower_limit': 7,
        'upper_limit': 10,
    },{
        'regime': 'Zeer nat',
        'color_255': ( 53,  95, 145),
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

        
    # Regime Legend from table
    legend_data = [{
            'name':regime.name,
            'color255':tuple(map(int,regime.color255.split(',')))
        } for regime in Regime.objects.all()]

    # Generate rgba colors
    for regime in REGIMES:
        regime['color_rgba'] = tuple(
            [component/255. for component in regime['color_255']] + [1]
        )

    for data in legend_data:
        logger.debug(data['color255'])
        data['color_rgba'] = tuple(
            [component/255. for component in data['color255']] + [1]
        )

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
            mapnik_rule(regime['color_255'],regime['mapnik_filter'])
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
                'Gewogen P-E: %1.1f mm/dag (%s)' % (
                    feature.properties['value'], afdeling[:2]+'-'+afdeling[2:])
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
            'name': 'Peilgebied: ' + afdeling[:2]+'-'+afdeling[2:],
            'shortname': afdeling,
            'object': None, # what object? --  TODO?
            'workspace_item': self.workspace_item,
            'google_coords': (google_x, google_y),
            'identifier': identifier,
            }

    def colorfunc_rgba(self,value):
        """Return rgba_color corresponding to value.
        
        Need to get it from table in the future, or get the values object at
        once. 
        """
        for regime in self.REGIMES:
            if (
                value > regime['lower_limit'] or
                regime['lower_limit'] == None
               ) and (
                value <= regime['upper_limit'] or
                regime['upper_limit'] == None
               ):
                return regime['color_rgba']

        return (0,1,0,0)

    def get_fake_data(self,identifier_list, start_date, end_date):
        """Make up some testdata."""
        from numpy import sin
        from numpy import arange
        startdate = datetime(2011,1,1)
        enddate = datetime(2013,12,31)
        numbers = arange(int(date2num(startdate)),int(date2num(enddate)))
        dates = [num2date(num) for num in numbers]
        values = list(10. * sin(numbers / 4. ) + 5.)
        return dates,values

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

        # Plot testdata.
        dates, values = self.get_fake_data(
            identifier_list, start_date, end_date
        )
        valuesP = [value * 1.2 for value in values]
        valuesE = [value * 0.2 for value in values]
        graph.axes.plot(dates, values,'darkgreen', label='P - E', linewidth=2)
        graph.axes.plot(dates, valuesP,color='gray', label='P')
        graph.axes.plot(
            dates, valuesE,color='gray', label='E',linestyle='--')
        
        # Create an extra margin outside the data
        margin = 0.1 # Fraction of ylim padding outside data
        allvalues = values + valuesP + valuesE
        lowest_value = min(allvalues)
        highest_value = max(allvalues)
        span = highest_value - lowest_value
        graph.axes.set_ylim(
            lowest_value - margin * span,
            highest_value + margin * span
        )
        
        # Labeling and legend position
        graph.axes.set_ylabel('Neerslagoverschot (mm/dag)')
        graph.axes.legend(loc=3)

        return graph.http_png()

    def bar_image(self, identifier_list, start_date, end_date,
        width=None, height=None, layout_extra=None):
        """Return a colored bar representing the regime against the time."""
        
        if width is None:
            width = 380.0
        if height is None:
            height = 170.0

        dates, values = self.get_fake_data(
            identifier_list, start_date, end_date
        )

        graph = adapter.Graph(start_date, end_date, width, height)
        graph.add_today()

        # Make a nice broken_barh:
        colors = [self.colorfunc_rgba(value) for value in values]
        xranges = [(
            date2num(date.replace(hour=2)),
            20./24.
        ) for date in dates]
        yrange = (0.1,0.8)

        graph.axes.broken_barh(xranges,yrange,facecolors=colors)

        # Legend building
        logger.debug(graph.figure.get_size_inches())
        from matplotlib.patches import Rectangle
        artists = [Rectangle((0., 0.), .1, .1, fc=data['color_rgba'])
            for data in self.legend_data]
        labels = [data['name'] for data in self.legend_data]
        # Make room for the legend, see the graph class from lizard-map
        graph.legend_on_bottom_height = 0.3
        graph.axes.legend(artists,labels,bbox_to_anchor=(0., -0.7, 1., 1.),
        loc=3,ncol=4,mode="expand", borderaxespad=0.)

        graph.axes.grid()
        graph.axes.set_yticks([])
        graph.axes.set_ylabel('Regime')
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
                'icon': 'waterbalance.png',
                'color': (0.5,1.0,0.5,0),
            }
        output_filename = sm.get_symbol_transformed(icon_style['icon'],
                                                    **icon_style)
        return settings.MEDIA_URL + 'generated_icons/' + output_filename   
        
    def legend(self, updates=None):
        """Return a legend in a list of dictionaries."""

        legend_result = []

        for data in self.legend_data:
            img_url = self.symbol_url(
                icon_style = {
                    'icon': 'empty.png',
                    'color': data['color_rgba'],
                }
            )
            description = data['name']
            legend_result.append({
                'img_url': img_url, 
                'description': description,
            })
       
        return legend_result

    def values(self, identifier_list, start_date, end_date):
        """ Return values in list of dictionaries (datetime, value, unit)
        """
        dates,values = self.get_fake_data(
            identifier_list, start_date, end_date
        )
        return [{
                'datetime':date,
                'value':value,
                'unit':None
            } for date,value in zip(dates,values) ]
        
        

