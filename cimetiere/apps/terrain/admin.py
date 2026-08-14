from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import Zone, Bloc, Caveau, Allée

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'area', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'description', 'area')
        }),
        ('Coordonnées', {
            'fields': ('center_lat', 'center_lng', 'polygon_coords'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Bloc)
class BlocAdmin(admin.ModelAdmin):
    list_display = ['name', 'zone', 'total_places', 'is_exploitable', 'get_occupancy_rate']
    list_filter = ['zone', 'is_exploitable', 'created_at']
    search_fields = ['name', 'zone__name', 'description']
    fieldsets = (
        ('Informations générales', {
            'fields': ('zone', 'name', 'description', 'is_exploitable')
        }),
        ('Dimensions', {
            'fields': ('standard_width', 'standard_length', 'total_places')
        }),
        ('Coordonnées', {
            'fields': ('center_lat', 'center_lng'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def get_occupancy_rate(self, obj):
        return f"{obj.get_occupancy_rate()}%"
    get_occupancy_rate.short_description = "Taux d'occupation"

@admin.register(Caveau)
class CaveauAdmin(admin.ModelAdmin):
    list_display = ['numero', 'bloc', 'statut', 'prix', 'get_color_display', 'get_coordinates_display']
    list_filter = ['statut', 'bloc', 'bloc__zone', 'created_at']
    search_fields = ['numero', 'bloc__name', 'bloc__zone__name']
    list_editable = ['statut', 'prix']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('bloc', 'numero', 'statut', 'description')
        }),
        ('Dimensions et prix', {
            'fields': ('largeur', 'longueur', 'superficie', 'prix')
        }),
        ('Coordonnées GPS', {
            'fields': ('latitude', 'longitude', 'coordinates'),
            'classes': ('wide',)
        }),
        ('Audit', {
            'fields': ('last_status_change', 'status_changed_by'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at', 'last_status_change', 'status_changed_by']
    
    def get_color_display(self, obj):
        color = obj.get_color()
        return f'<span style="background-color:{color}; padding:5px 10px; border-radius:3px; color:white;">{obj.get_statut_display()}</span>'
    get_color_display.allow_html = True
    get_color_display.short_description = "Statut (couleur)"
    
    def get_coordinates_display(self, obj):
        coords = obj.get_coordinates()
        if coords:
            return f"({coords[0]}, {coords[1]})"
        return "Non défini"
    get_coordinates_display.short_description = "Coordonnées"
    
    def save_model(self, request, obj, form, change):
        if 'statut' in form.changed_data:
            obj.last_status_change = models.DateTimeField(auto_now=True)
            obj.status_changed_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Allée)
class AlléeAdmin(admin.ModelAdmin):
    list_display = ['name', 'width', 'created_at']
    search_fields = ['name', 'description']