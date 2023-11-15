from django.contrib import admin
from django.db.models import Count

from .models import Products, HistoryProducts
from datetime import datetime, timedelta
from django.urls import path
from django.contrib import admin
from django.utils.html import format_html
from .models import Products
from .views import custom_admin_view


class ModuleFilter(admin.SimpleListFilter):
    title = 'Models'
    parameter_name = 'modules'

    def lookups(self, request, model_admin):
        # Get unique 'model' values and their counts
        unique_models = Products.objects.values('model').annotate(count=Count('model')).order_by('-count')[:15]


        # Convert the unique 'model' values into tuples of (value, display text)
        lookups = [(str(model['model']), f"{model['model']} ({model['count']})") for model in unique_models]

        return lookups

    def queryset(self, request, queryset):
        if self.value():
            # Filter the queryset based on the selected 'model'
            return queryset.filter(model=self.value())

class LastQtyOneFilter(admin.SimpleListFilter):
    title = 'Last Items'
    parameter_name = 'last_qty_one'

    def lookups(self, request, model_admin):
        return (
            ('last_items', 'Last Items'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'last_items':
            # Get the last items where qty is equal to 1
            last_items_qty_one = Products.objects.filter(qty=1)
            if last_items_qty_one:
                return last_items_qty_one
        return queryset

class ProductsAdmin(admin.ModelAdmin):
    list_display = ('ean', 'symbol', 'qty', 'model', 'sizechart_link')
    search_fields = ['model', 'symbol', 'ean']
    list_filter = (LastQtyOneFilter, ModuleFilter,)

    def sizechart_link(self, obj):
        if obj.sizechart:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.sizechart, obj.sizechart)
        return ""
    sizechart_link.short_description = 'Size Chart'

admin.site.register(Products, ProductsAdmin)



class TimeFrameFilter(admin.SimpleListFilter):
    title = 'Time Frame'
    parameter_name = 'time_frame'

    def lookups(self, request, model_admin):
        return (
            ('last_10_minutes', 'Last 10 Minutes'),
            ('last_hour', 'Last Hour'),
            ('last_24_hours', 'Last 24 Hours'),
        )

    def queryset(self, request, queryset):
        now = datetime.now()

        if self.value() == 'last_10_minutes':
            # Calculate the timestamp for 10 minutes ago
            ten_minutes_ago = now - timedelta(minutes=10)
            return queryset.filter(date__gte=ten_minutes_ago)

        if self.value() == 'last_hour':
            # Calculate the timestamp for one hour ago
            one_hour_ago = now - timedelta(hours=1)
            return queryset.filter(date__gte=one_hour_ago)

        if self.value() == 'last_24_hours':
            # Calculate the timestamp for 24 hours ago
            twenty_four_hours_ago = now - timedelta(hours=24)
            return queryset.filter(date__gte=twenty_four_hours_ago)

        return queryset

class HistoryProductsAdmin(admin.ModelAdmin):
    list_display = ('ean', 'qty', 'date')
    search_fields = ['ean']
    list_filter = (TimeFrameFilter,)

admin.site.register(HistoryProducts, HistoryProductsAdmin)