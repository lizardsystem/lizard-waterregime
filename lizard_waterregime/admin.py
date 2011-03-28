from lizard_waterregime.models import WaterRegimeShape
from lizard_waterregime.models import Regime
from lizard_waterregime.models import Range
from lizard_waterregime.models import Season
from django.contrib import admin

admin.site.register(WaterRegimeShape)

class RegimeAdmin(admin.ModelAdmin):
    def link(self,other):
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
    def link(self,other):
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

class RangeAdmin(admin.ModelAdmin):
    def link(self,other):
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
    ordering = ['season','regime']
admin.site.register(Range, RangeAdmin)
