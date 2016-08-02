from django.contrib import admin
from django.db.models import ExpressionWrapper, F, FloatField
from cards.models import *

# Register your models here.
class MetaDataAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']
admin.site.register(MetaData, MetaDataAdmin)

class CardSetAdmin(admin.ModelAdmin):
    list_display = ['name']
admin.site.register(CardSet, CardSetAdmin)

class CardTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
admin.site.register(CardType, CardTypeAdmin)

class FactionAdmin(admin.ModelAdmin):
    list_display = ['name']
admin.site.register(Faction, FactionAdmin)

class RarityAdmin(admin.ModelAdmin):
    list_display = ['name']
admin.site.register(Rarity, RarityAdmin)

class RaceAdmin(admin.ModelAdmin):
    list_display = ['name']
admin.site.register(Race, RaceAdmin)

class CharacterClassAdmin(admin.ModelAdmin):
    list_display = ['name']
admin.site.register(CharacterClass, CharacterClassAdmin)

class CardMechanicInline(admin.TabularInline):
    model = CardMechanic
    extra = 0

class MechanicAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'value']
    inlines = [CardMechanicInline]
admin.site.register(Mechanic, MechanicAdmin)

class CardAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'complex_delta_round', 'simple_delta_round', 'complex_value_round', 'simple_value_round', 'mana', 'health', 'attack']

    def get_queryset(self, request):
        qs = super(CardAdmin, self).get_queryset(request)
        qs = qs.annotate(complex_delta=ExpressionWrapper(F('complex_value') - F('mana'), output_field=FloatField()))
        qs = qs.annotate(simple_delta=ExpressionWrapper(F('simple_value') - F('mana'), output_field=FloatField()))
        return qs

    def complex_delta_round(self, obj):
        return round(obj.complex_delta, 1)
    complex_delta_round.admin_order_field="complex_delta"
    complex_delta_round.short_description="Value (Complex)"

    def simple_delta_round(self, obj):
        return round(obj.simple_delta, 1)
    simple_delta_round.admin_order_field="simple_delta"
    simple_delta_round.short_description="Value (Simple)"

    def avg_delta_round(self, obj):
        return round(obj.avg_value, 1)
    avg_delta_round.admin_order_field="avg_delta"
    avg_delta_round.short_description="Value (avg)"

    def complex_value_round(self, obj):
        return round(obj.complex_value, 1)
    complex_value_round.admin_order_field="complex_value"
    complex_value_round.short_description="Expected Mana (Complex)"

    def simple_value_round(self, obj):
        return round(obj.simple_value, 1)
    simple_value_round.admin_order_field="simple_value"
    simple_value_round.short_description="Expected Mana (Simple)"

    fieldsets = [
        (None, {
            'fields': [
                'name',
                'cardId'
            ]
        }),
        ("Meta", {
            'fields': [
                'cardType',
                'cardSet',
                'faction',
            ]
        }),
        ("Card", {
            'fields': [
                'rarity',
                'race',
                'character_class'
            ]
        }),
        ("Basic stats", {
            'fields': [
                'mana',
                'health',
                'attack'
            ]
        }),
    ]
    inlines = [CardMechanicInline]
admin.site.register(Card, CardAdmin)
