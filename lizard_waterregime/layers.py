import logging
import mapnik
import os
from datetime import datetime
from matplotlib.dates import date2num

from django.core.urlresolvers import reverse
from django.conf import settings

from lizard_map import coordinates
from lizard_map import adapter
from lizard_map.models import ICON_ORIGINALS
from lizard_map.coordinates import RD
from lizard_map.workspace import WorkspaceItemAdapter
from lizard_map.symbol_manager import SymbolManager

from lizard_waterregime.models import Regime
from lizard_waterregime.calculator import RegimeCalculator
from lizard_waterregime.models import Season
from lizard_waterregime.models import WaterRegimeShape

from numpy import isnan

logger = logging.getLogger('nens.waterregimeadapter')


class AdapterWaterRegime(WorkspaceItemAdapter):
    """Adapter for module lizard_waterregime.

    Registered as adapter_waterregime.
    Uses default database table "water_regime_shape" as geo database.
    Set the regimedatetime attribute to determine for which moment the colors
    on the map are shown. """

    regimedatetime = datetime.now()

    def _mapnik_style(self, season):
        """ Return a mapnik_style, accounting for season """

        def _filters(season):

            """Generate mapnikfilters and colors for the ranges in this
            season."""
            colors = []
            filters = []

            regimeranges = season.range_set.all()
            for r in regimeranges:
                # only append filter and color if at least one range is set
                if r.lower_limit or r.upper_limit:
                    mapnik_filter = "[valid] = 'Y' and "
                    if r.lower_limit:
                        mapnik_filter += '[value] > ' + str(r.lower_limit)
                    if r.lower_limit and r.upper_limit:
                        mapnik_filter += ' and '
                    if r.upper_limit:
                        mapnik_filter += '[value] <= ' + str(r.upper_limit)
                    filters.append(mapnik_filter)
                    colors.append(r.regime.color_255())

                # Extra filter for invalid pmine's
                filters.append("[valid] = 'N'")
                colors.append((127, 0, 127, 63))

            return zip(colors, filters)

        def _mapnik_rule(color, mapnik_filter):
            """ Return a mapnik_rule

            Here also the line thickness and fill opacity can be set."""
            rule = mapnik.Rule()

            rule.filter = mapnik.Filter(mapnik_filter)

            mapnik_color = mapnik.Color(*color)
            symb_line = mapnik.LineSymbolizer(mapnik_color, 2)
            rule.symbols.append(symb_line)

            symb_poly = mapnik.PolygonSymbolizer(mapnik_color)
            symb_poly.fill_opacity = .8
            rule.symbols.append(symb_poly)
            return rule

        mapnik_style = mapnik.Style()
        mapnik_style.rules.extend(
            [_mapnik_rule(*args) for args in _filters(season)])
        return mapnik_style

    def layer(self, layer_ids=None, request=None):
        """Generates and returns mapnik layers and styles.
        """

        layers = []
        styles = {}

        db_settings = settings.DATABASES['default']

        # Refresh the p min e values in the database if necessary.
        RegimeCalculator.refresh(self.regimedatetime)
        shape_view = str("""(
            select
                shp.gid,
                shp.afdeling,
                shp.naam,
                shp.area_m2,
                shp.the_geom,
                pme.value,
                pme.valid
            from
                lizard_waterregime_waterregimeshape shp
                join lizard_waterregime_precipitationsurplus pme
                    on pme.waterregimeshape_id = shp.gid
        ) result_view""")
        layer = mapnik.Layer('Geometry from PostGIS')
        # RD = rijksdriehoek. Somehow 'Google' is also mentioned originally?
        layer.srs = RD
        layer.datasource = mapnik.PostGIS(
            host=db_settings['HOST'],
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            dbname=db_settings['NAME'],
            table=shape_view)

        style_name = 'waterregime_style'

        layer.styles.append(style_name)
        layers.append(layer)
        cf = self.Colorfunc()
        mapnik_style = self._mapnik_style(cf.season(self.regimedatetime))
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
            valid = feature.properties['valid']
            value = feature.properties['value']
            if valid == 'Y':
                precipitationsurplus = '%1.1f mm/dag' % value
            else:
                precipitationsurplus = 'Onbekend'
            popup_string = ('Gewogen P-E: %s (%s)' % (
                    precipitationsurplus,
                    afdeling[:2] + '-' + afdeling[2:]))
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

        if snippet_group is not None:
            snippets = snippet_group.snippets.all()
            identifiers = [snippet.identifier for snippet in snippets]

        graph_img_url = reverse(
            "lizard_waterregime.workspace_item_graph_image",
            kwargs={'workspace_item_id': self.workspace_item.id},
            )
        bar_img_url = reverse(
            "lizard_waterregime.workspace_item_bar_image",
            kwargs={'workspace_item_id': self.workspace_item.id},
            )
        graphs = []
        for identifier in identifiers:
            afdeling = "?afdeling=" + identifier['afdeling']
            graphs.append({
                'afdeling': identifier['afdeling'],
                'graph_img_url': graph_img_url + afdeling,
                'bar_img_url': bar_img_url + afdeling})
        return super(AdapterWaterRegime, self).html_default(
            snippet_group=snippet_group,
            identifiers=identifiers,
            layout_options=layout_options,
            template='lizard_waterregime/popup.html',
            extra_render_kwargs={
                'graphs': graphs})

    def location(self, afdeling, google_x, google_y, layout=None):
        """Lookup 'peilgebied' by 'afdeling'

        """
        identifier = {
            'afdeling': afdeling,
            'google_x': google_x,
            'google_y': google_y,
        }

        return {
            'name': 'Peilgebied: ' + afdeling[:2] + '-' + afdeling[2:],
            'shortname': afdeling,
            'object': None,
            'workspace_item': self.workspace_item,
            'google_coords': (google_x, google_y),
            'identifier': identifier,
            }

    class Colorfunc(object):
        """ Class with colorfunction method."""
        def __init__(self):
            self.seasons = Season.objects.all()
            self.regimeranges = {}
            for s in self.seasons:
                self.regimeranges[s] = s.range_set.all()

        def season(self, dt):
            for s in self.seasons:
                if (
                    (
                        dt.month > s.month_from and
                        dt.month < s.month_to
                    ) or (
                        dt.month == s.month_from and
                        dt.day >= s.day_from
                    ) or (
                     dt.month == s.month_to and
                     dt.day <= s.day_to
                    )
                ):
                    return s

        def colorfunc(self, datetime, value):
            """ Return the colorfunc corresponding to value and datetime."""
            for r in self.regimeranges[self.season(datetime)]:
            # only valid range if at least one limit is set
                if r.upper_limit or r.lower_limit:
                    if (
                        r.lower_limit == None or
                        value >= float(r.lower_limit)
                       ) and (
                        r.upper_limit == None or
                        value < float(r.upper_limit)
                       ):
                        color = r.regime.color_rgba()
                        return color

            # if no rule applied, get this ugly green color.
            return (0, 1, 0, 0)

    def graph_image(self, identifier_list, start_date, end_date,
                    width=None, height=None, layout_extra=None):
        """Visualize scores or measures in a graph each row is an area.

        Not suitable for collages presently, since the 'afdeling' is passed
        via the image url.
        """

        if width is None:
            width = 380.0
        if height is None:
            height = 170.0

        graph = adapter.Graph(start_date, end_date, width, height)
        graph.add_today()

        shape = WaterRegimeShape.objects.get(
            afdeling=identifier_list[0]['afdeling']
        )

        events_weighted_pmine, events_p, events_e = (
            RegimeCalculator.weighted_precipitation_surplus(
                shape,
                datetime(start_date.year, start_date.month, start_date.day),
                datetime(end_date.year, end_date.month, end_date.day)
            )
        )

        if events_e.size > 0:
            graph.axes.plot(events_e[:, 0], events_e[:, 1],
                color='red', label='E (mm/dag)', linestyle='', marker='o')
        if events_p.size > 0:
            graph.axes.bar(events_p[:, 0], events_p[:, 1], 1. / 24,
                edgecolor='blue',
                color='blue', label='P (mm/uur)')
        if events_weighted_pmine.size > 0:
            graph.axes.plot(
                events_weighted_pmine[:, 0],
                events_weighted_pmine[:, 1],
                'darkgreen',
                label='P - E (mm/dag)',
                linestyle='-',
                marker='.')

        # Create an extra margin outside the data
        margin = 0.1  # Fraction of ylim padding outside data
        mins = []
        maxs = []

        for arr in (events_weighted_pmine, events_p, events_e):
            if arr.size > 0:
                arrmin = min(arr[:, 1])
                if not isnan(arrmin):
                    mins.append(arrmin)
                arrmax = max(arr[:, 1])
                if not isnan(arrmax):
                    maxs.append(arrmax)
        if len(mins) == 0:
            lowest_value = 0.
        else:
            lowest_value = min(mins)

        if len(maxs) == 0:
            highest_value = 1.
        else:
            highest_value = max(maxs)

        span = highest_value - lowest_value
        graph.axes.set_ylim(
            lowest_value - margin * span,
            highest_value + margin * span
        )

        # Labeling and legend position
        #graph.axes.set_ylabel('Neerslagoverschot (mm/dag)')
        graph.legend_on_bottom_height = 0.15
        graph.axes.legend(bbox_to_anchor=(0., -0.3, 1., 1.),
        loc=3, ncol=4, mode="expand", borderaxespad=0.)

        response = graph.http_png()
        response['Cache-Control'] = 'max-age=15'

        return response

    def bar_image(self, identifier_list, start_date, end_date,
        width=None, height=None, layout_extra=None):
        """Return a colored bar representing the regime against the time.

        Not suitable for collages presently, since the 'afdeling' is passed
        via the image url.
        """

        if width is None:
            width = 380.0
        if height is None:
            height = 170.0

        shape = WaterRegimeShape.objects.get(
            afdeling=identifier_list[0]['afdeling']
        )

        events_weighted_pmine, events_p, events_e = (
            RegimeCalculator.weighted_precipitation_surplus(
                shape,
                datetime(start_date.year, start_date.month, start_date.day),
                datetime(end_date.year, end_date.month, end_date.day)
            )
        )

        graph = adapter.Graph(start_date, end_date, width, height)
        graph.add_today()

        # Make a nice broken_barh:
        cf = self.Colorfunc()

        colors = [cf.colorfunc(dt, v) for dt, v in filter(
            lambda x: not isnan(x[1]), events_weighted_pmine)]
        xranges = [(
            date2num(datetime(dt.year, dt.month, dt.day, dt.hour)),
            1. / 24
        ) for dt, v in filter(
            lambda x: not isnan(x[1]), events_weighted_pmine)]
        yrange = (0.1, 0.8)

        graph.axes.broken_barh(xranges, yrange, facecolors=colors, linewidth=0,
        antialiased=False,
        )

        # Legend building
        from matplotlib.patches import Rectangle
        artists = []
        labels = []
        for r in Regime.objects.all():
            artists.append(Rectangle((0., 0.), .1, .1, fc=r.color_rgba()))
            labels.append(r.name)
        # Make room for the legend, see the graph class from lizard-map
        graph.legend_on_bottom_height = 0.3
        graph.axes.legend(artists, labels, bbox_to_anchor=(0., -0.7, 1., 1.),
        loc=3, ncol=4, mode="expand", borderaxespad=0.)

        graph.axes.grid()
        graph.axes.set_yticks([])
        graph.axes.set_ylabel('Regime')

        response = graph.http_png()
        response['Cache-Control'] = 'max-age=15'

        return response

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
                'color': (0.5, 1.0, 0.5, 0),
            }
        output_filename = sm.get_symbol_transformed(icon_style['icon'],
                                                    **icon_style)
        return settings.MEDIA_URL + 'generated_icons/' + output_filename

    def legend(self, updates=None):
        """Return a legend in a list of dictionaries."""

        legend_result = []

        for r in Regime.objects.all():
            img_url = self.symbol_url(
                icon_style={
                    'icon': 'empty.png',
                    'color': r.color_rgba(),
                }
            )
            description = r.name
            legend_result.append({
                'img_url': img_url,
                'description': description,
            })

        return legend_result

    def values(self, identifier_list, start_date, end_date):
        """ Return weighted P - E values in list of
        dictionaries (datetime, value, unit)
        """
        afdeling = identifier_list['afdeling']
        shape = WaterRegimeShape.objects.get(afdeling=afdeling) 
        w, p, e = RegimeCalculator.weighted_precipitation_surplus(
            shape, start_date, end_date)
        return [
            {
            'datetime': date,
            'value': value,
            'unit': 'mm/dag',
            } for date, value in w
        ]

