from lizard_waterregime.models import Constant
from lizard_waterregime.models import CropFactor
from lizard_waterregime.models import FewsTimeSeries
from lizard_waterregime.models import LandCover
from lizard_waterregime.models import LandCoverData
from lizard_waterregime.models import Range
from lizard_waterregime.models import Regime
from lizard_waterregime.models import Season
from lizard_waterregime.models import WaterRegimeShape
from django.contrib import admin


admin.site.register(Constant)
admin.site.register(FewsTimeSeries)
admin.site.register(LandCoverData)
admin.site.register(WaterRegimeShape)


class CropFactorInline(admin.TabularInline):
    model = CropFactor


class LandCoverAdmin(admin.ModelAdmin):
    inlines = [CropFactorInline, ]
admin.site.register(LandCover, LandCoverAdmin)


class RangeAdmin(admin.ModelAdmin):
    def link(self, other):
        return other
    list_display = (
        'link',
        'regime',
        'season',
        'lower_limit',
        'upper_limit',
    )
    list_editable = (
        'regime',
        'season',
        'lower_limit',
        'upper_limit',
    )
    ordering = ['season', 'regime']
admin.site.register(Range, RangeAdmin)


class RegimeAdmin(admin.ModelAdmin):
    def link(self, other):
        return other
    list_display = (
        'link',
        'name',
        'color255',
        'order',
    )
    list_editable = (
        'name',
        'color255',
        'order',
    )
admin.site.register(Regime, RegimeAdmin)


class SeasonAdmin(admin.ModelAdmin):
    def link(self, other):
        return other
    list_display = (
        'link',
        'month_from',
        'day_from',
        'month_to',
        'day_to',
    )
    list_editable = (
        'month_from',
        'day_from',
        'month_to',
        'day_to',
    )
admin.site.register(Season, SeasonAdmin)
