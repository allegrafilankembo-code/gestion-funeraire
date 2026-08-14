from ninja import Router, Query
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from django.db.models import Q
from typing import List, Optional
from .models import Zone, Bloc, Caveau, Allée
from .serializers import (
    ZoneSchema, BlocSchema, CaveauSchema, 
    CaveauStatusUpdateSchema, CaveauFilterSchema
)
from apps.core.permissions import AdminPermission, AgentPermission
from apps.core.middleware import audit_log

router = Router(tags=["Gestion du Terrain"])

# ============ ZONES ============
@router.get("/zones", response=List[ZoneSchema])
def list_zones(request):
    """Liste toutes les zones"""
    return Zone.objects.all()

@router.get("/zones/{zone_id}", response=ZoneSchema)
def get_zone(request, zone_id: int):
    """Détails d'une zone"""
    return get_object_or_404(Zone, id=zone_id)

@router.post("/zones", response=ZoneSchema, auth=AdminPermission())
def create_zone(request, payload: ZoneSchema):
    """Crée une nouvelle zone (Admin uniquement)"""
    zone = Zone.objects.create(**payload.dict())
    return zone

@router.put("/zones/{zone_id}", response=ZoneSchema, auth=AdminPermission())
def update_zone(request, zone_id: int, payload: ZoneSchema):
    """Met à jour une zone (Admin uniquement)"""
    zone = get_object_or_404(Zone, id=zone_id)
    for key, value in payload.dict().items():
        setattr(zone, key, value)
    zone.save()
    return zone

@router.delete("/zones/{zone_id}", auth=AdminPermission())
def delete_zone(request, zone_id: int):
    """Supprime une zone (Admin uniquement)"""
    zone = get_object_or_404(Zone, id=zone_id)
    zone.delete()
    return {"success": True}

# ============ BLOCS ============
@router.get("/blocs", response=List[BlocSchema])
def list_blocs(request, zone_id: Optional[int] = None):
    """Liste les blocs (optionnellement filtrés par zone)"""
    queryset = Bloc.objects.select_related('zone')
    if zone_id:
        queryset = queryset.filter(zone_id=zone_id)
    return queryset

@router.get("/blocs/{bloc_id}", response=BlocSchema)
def get_bloc(request, bloc_id: int):
    """Détails d'un bloc"""
    return get_object_or_404(Bloc.objects.select_related('zone'), id=bloc_id)

@router.post("/blocs", response=BlocSchema, auth=AdminPermission())
def create_bloc(request, payload: BlocSchema):
    """Crée un nouveau bloc (Admin uniquement)"""
    bloc = Bloc.objects.create(**payload.dict())
    return bloc

# ============ CAVEAUX ============
@router.get("/caveaux", response=List[CaveauSchema])
@paginate
def list_caveaux(request, filters: CaveauFilterSchema = Query(...)):
    """Liste les caveaux avec filtres"""
    queryset = Caveau.objects.select_related('bloc', 'bloc__zone')
    
    if filters.bloc_id:
        queryset = queryset.filter(bloc_id=filters.bloc_id)
    if filters.zone_id:
        queryset = queryset.filter(bloc__zone_id=filters.zone_id)
    if filters.statut:
        queryset = queryset.filter(statut=filters.statut)
    if filters.disponible is not None:
        if filters.disponible:
            queryset = queryset.filter(statut='DISPONIBLE')
        else:
            queryset = queryset.exclude(statut='DISPONIBLE')
    if filters.prix_min is not None:
        queryset = queryset.filter(prix__gte=filters.prix_min)
    if filters.prix_max is not None:
        queryset = queryset.filter(prix__lte=filters.prix_max)
    
    return queryset

@router.get("/caveaux/{caveau_id}", response=CaveauSchema)
def get_caveau(request, caveau_id: int):
    """Détails d'un caveau"""
    return get_object_or_404(Caveau.objects.select_related('bloc', 'bloc__zone'), id=caveau_id)

@router.post("/caveaux", response=CaveauSchema, auth=AdminPermission())
def create_caveau(request, payload: CaveauSchema):
    """Crée un nouveau caveau (Admin uniquement)"""
    caveau = Caveau.objects.create(**payload.dict())
    audit_log(request.user, "CREATE", "Caveau", caveau.id, f"Création du caveau {caveau.numero}")
    return caveau

@router.put("/caveaux/{caveau_id}", response=CaveauSchema, auth=AdminPermission())
def update_caveau(request, caveau_id: int, payload: CaveauSchema):
    """Met à jour un caveau (Admin uniquement)"""
    caveau = get_object_or_404(Caveau, id=caveau_id)
    old_status = caveau.statut
    for key, value in payload.dict().items():
        setattr(caveau, key, value)
    caveau.save()
    
    if old_status != caveau.statut:
        audit_log(
            request.user, 
            "STATUS_CHANGE", 
            "Caveau", 
            caveau.id, 
            f"Statut changé de {old_status} à {caveau.statut}"
        )
    
    return caveau

@router.patch("/caveaux/{caveau_id}/status", response=CaveauSchema, auth=AgentPermission())
def update_caveau_status(request, caveau_id: int, payload: CaveauStatusUpdateSchema):
    """Change le statut d'un caveau"""
    caveau = get_object_or_404(Caveau, id=caveau_id)
    old_status = caveau.statut
    new_status = payload.statut
    
    # Vérifier les transitions autorisées
    allowed_transitions = {
        'DISPONIBLE': ['RESERVE'],
        'RESERVE': ['OCCUPE', 'DISPONIBLE'],
        'OCCUPE': ['DISPONIBLE'],
        'NON_EXPLOITABLE': ['DISPONIBLE'],
    }
    
    if new_status not in allowed_transitions.get(old_status, []):
        return {"error": f"Transition non autorisée: {old_status} -> {new_status}"}
    
    caveau.change_status(new_status, request.user)
    
    if payload.notes:
        caveau.notes += f"\n[{request.user.email}] {payload.notes}"
        caveau.save()
    
    audit_log(
        request.user, 
        "STATUS_CHANGE", 
        "Caveau", 
        caveau.id, 
        f"Statut changé de {old_status} à {new_status}"
    )
    
    return caveau

@router.get("/caveaux/stats/summary")
def get_caveaux_stats(request):
    """Résumé des statistiques des caveaux"""
    total = Caveau.objects.count()
    disponibles = Caveau.objects.filter(statut='DISPONIBLE').count()
    reserves = Caveau.objects.filter(statut='RESERVE').count()
    occupes = Caveau.objects.filter(statut='OCCUPE').count()
    non_exploitables = Caveau.objects.filter(statut='NON_EXPLOITABLE').count()
    
    return {
        "total": total,
        "disponibles": disponibles,
        "reserves": reserves,
        "occupes": occupes,
        "non_exploitables": non_exploitables,
        "taux_occupation": round(((reserves + occupes) / total * 100), 2) if total > 0 else 0,
        "taux_disponibilite": round((disponibles / total * 100), 2) if total > 0 else 0,
    }

# ============ ALLÉES ============
@router.get("/allees", response=List[dict])
def list_allees(request):
    """Liste toutes les allées"""
    return Allée.objects.all().values('id', 'name', 'description', 'width', 'path_coords')

@router.post("/allees", auth=AdminPermission())
def create_allee(request, payload: dict):
    """Crée une nouvelle allée (Admin uniquement)"""
    allee = Allée.objects.create(**payload)
    return {"success": True, "id": allee.id}