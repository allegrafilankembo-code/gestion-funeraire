from ninja import Schema
from typing import Optional, List, Dict, Any
from datetime import datetime

class ZoneSchema(Schema):
    id: Optional[int] = None
    name: str
    description: Optional[str] = ""
    area: Optional[float] = None
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None
    polygon_coords: Optional[List[List[float]]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class BlocSchema(Schema):
    id: Optional[int] = None
    zone: Optional[ZoneSchema] = None
    zone_id: int
    name: str
    description: Optional[str] = ""
    standard_width: float = 1.0
    standard_length: float = 2.5
    total_places: int = 0
    is_exploitable: bool = True
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    available_places: Optional[int] = None
    occupancy_rate: Optional[float] = None

class CaveauSchema(Schema):
    id: Optional[int] = None
    bloc: Optional[BlocSchema] = None
    bloc_id: int
    numero: str
    statut: str
    statut_display: Optional[str] = None
    color: Optional[str] = None
    largeur: float = 1.0
    longueur: float = 2.5
    superficie: float = 2.5
    prix: float = 0.0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    coordinates: Optional[Dict[str, float]] = {}
    description: Optional[str] = ""
    notes: Optional[str] = ""
    last_status_change: Optional[datetime] = None
    status_changed_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @staticmethod
    def resolve_statut_display(obj):
        return obj.get_statut_display()
    
    @staticmethod
    def resolve_color(obj):
        return obj.get_color()
    
    @staticmethod
    def resolve_coordinates(obj):
        coords = obj.get_coordinates()
        if coords:
            return {'lat': coords[0], 'lng': coords[1]}
        return {}

class CaveauStatusUpdateSchema(Schema):
    statut: str
    notes: Optional[str] = ""

class CaveauFilterSchema(Schema):
    bloc_id: Optional[int] = None
    zone_id: Optional[int] = None
    statut: Optional[str] = None
    disponible: Optional[bool] = None
    prix_min: Optional[float] = None
    prix_max: Optional[float] = None