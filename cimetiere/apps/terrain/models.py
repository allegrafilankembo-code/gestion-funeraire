from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Zone(models.Model):
    """Zone du cimetière (section principale)"""
    name = models.CharField(max_length=100, verbose_name="Nom de la zone")
    description = models.TextField(blank=True, verbose_name="Description")
    area = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Superficie en m²",
        verbose_name="Superficie"
    )
    
    # Pour la cartographie sans PostGIS
    center_lat = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Latitude du centre de la zone",
        verbose_name="Latitude centre"
    )
    center_lng = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Longitude du centre de la zone",
        verbose_name="Longitude centre"
    )
    
    # Polygone simplifié (coordonnées des coins)
    polygon_coords = models.JSONField(
        default=list, 
        blank=True,
        help_text="Coordonnées du polygone: [[lat, lng], [lat, lng], ...]",
        verbose_name="Coordonnées du polygone"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Zone"
        verbose_name_plural = "Zones"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Bloc(models.Model):
    """Bloc à l'intérieur d'une zone"""
    zone = models.ForeignKey(
        Zone, 
        on_delete=models.CASCADE, 
        related_name='blocs',
        verbose_name="Zone"
    )
    name = models.CharField(max_length=50, verbose_name="Nom du bloc")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Dimensions standard des tombeaux dans ce bloc
    standard_width = models.FloatField(
        default=1.0, 
        help_text="Largeur standard en mètres",
        verbose_name="Largeur standard"
    )
    standard_length = models.FloatField(
        default=2.5, 
        help_text="Longueur standard en mètres",
        verbose_name="Longueur standard"
    )
    
    # Nombre de places totales
    total_places = models.IntegerField(
        default=0,
        help_text="Nombre total de places dans ce bloc",
        verbose_name="Total places"
    )
    
    is_exploitable = models.BooleanField(
        default=True, 
        verbose_name="Exploitable"
    )
    
    # Coordonnées du bloc
    center_lat = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="Latitude centre"
    )
    center_lng = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="Longitude centre"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Bloc"
        verbose_name_plural = "Blocs"
        ordering = ['zone', 'name']
        unique_together = ['zone', 'name']
    
    def __str__(self):
        return f"{self.zone.name} - {self.name}"
    
    def get_available_places(self):
        """Retourne le nombre de places disponibles"""
        return self.caveaux.filter(statut='DISPONIBLE').count()
    
    def get_occupancy_rate(self):
        """Retourne le taux d'occupation en pourcentage"""
        total = self.caveaux.count()
        if total == 0:
            return 0
        occupied = self.caveaux.filter(statut__in=['RESERVE', 'OCCUPE']).count()
        return round((occupied / total) * 100, 2)

class Caveau(models.Model):
    """Caveau individuel"""
    
    # Statuts avec codes couleur
    STATUS_CHOICES = [
        ('DISPONIBLE', 'Vert - Disponible'),
        ('RESERVE', 'Orange - Réservé'),
        ('OCCUPE', 'Rouge - Occupé'),
        ('NON_EXPLOITABLE', 'Gris - Non exploitable'),
    ]
    
    # Informations de base
    bloc = models.ForeignKey(
        Bloc, 
        on_delete=models.CASCADE, 
        related_name='caveaux',
        verbose_name="Bloc"
    )
    numero = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name="Numéro du caveau"
    )
    statut = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='DISPONIBLE',
        verbose_name="Statut"
    )
    
    # Dimensions
    largeur = models.FloatField(
        default=1.0,
        help_text="Largeur en mètres",
        verbose_name="Largeur"
    )
    longueur = models.FloatField(
        default=2.5,
        help_text="Longueur en mètres",
        verbose_name="Longueur"
    )
    superficie = models.FloatField(
        default=2.5,
        help_text="Superficie en m²",
        verbose_name="Superficie"
    )
    
    # Prix
    prix = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Prix"
    )
    
    # Coordonnées GPS (pour cartographie sans PostGIS)
    latitude = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Latitude GPS (ex: 14.7167)",
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        verbose_name="Latitude"
    )
    longitude = models.FloatField(
        null=True, 
        blank=True, 
        help_text="Longitude GPS (ex: -17.4677)",
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        verbose_name="Longitude"
    )
    
    # Coordonnées JSON (alternative)
    coordinates = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Coordonnées: {'lat': 14.7167, 'lng': -17.4677}",
        verbose_name="Coordonnées JSON"
    )
    
    # Métadonnées
    description = models.TextField(blank=True, verbose_name="Description")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Audit trail (qui a modifié le statut)
    last_status_change = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Dernier changement de statut"
    )
    status_changed_by = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='modified_caveaux',
        verbose_name="Modifié par"
    )
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Caveau"
        verbose_name_plural = "Caveaux"
        ordering = ['bloc', 'numero']
        unique_together = ['bloc', 'numero']
    
    def __str__(self):
        return f"{self.bloc.name} - {self.numero} ({self.get_statut_display()})"
    
    def get_color(self):
        """Retourne la couleur associée au statut"""
        colors = {
            'DISPONIBLE': '#28a745',  # Vert
            'RESERVE': '#fd7e14',     # Orange
            'OCCUPE': '#dc3545',      # Rouge
            'NON_EXPLOITABLE': '#6c757d',  # Gris
        }
        return colors.get(self.statut, '#6c757d')
    
    def get_coordinates(self):
        """Retourne les coordonnées sous forme de tuple"""
        if self.latitude and self.longitude:
            return (self.latitude, self.longitude)
        if self.coordinates:
            return (self.coordinates.get('lat'), self.coordinates.get('lng'))
        return None
    
    def set_coordinates(self, lat, lng):
        """Définit les coordonnées"""
        self.latitude = lat
        self.longitude = lng
        self.coordinates = {'lat': lat, 'lng': lng}
    
    def is_available(self):
        """Vérifie si le caveau est disponible"""
        return self.statut == 'DISPONIBLE'
    
    def is_reserved(self):
        """Vérifie si le caveau est réservé"""
        return self.statut == 'RESERVE'
    
    def is_occupied(self):
        """Vérifie si le caveau est occupé"""
        return self.statut == 'OCCUPE'
    
    def change_status(self, new_status, user=None):
        """Change le statut avec audit trail"""
        old_status = self.statut
        self.statut = new_status
        self.last_status_change = models.DateTimeField(auto_now=True)
        if user:
            self.status_changed_by = user
        self.save()
        return old_status

class Allée(models.Model):
    """Allée entre les blocs"""
    name = models.CharField(max_length=100, verbose_name="Nom de l'allée")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Coordonnées de l'allée (linestring simplifiée)
    path_coords = models.JSONField(
        default=list, 
        blank=True,
        help_text="Coordonnées du chemin: [[lat, lng], [lat, lng], ...]",
        verbose_name="Coordonnées du chemin"
    )
    
    # Largeur de l'allée
    width = models.FloatField(
        default=2.0,
        help_text="Largeur en mètres",
        verbose_name="Largeur"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Allée"
        verbose_name_plural = "Allées"
        ordering = ['name']
    
    def __str__(self):
        return self.name