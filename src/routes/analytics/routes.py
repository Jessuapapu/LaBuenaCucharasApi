from fastapi import APIRouter, HTTPException, Query, Depends
from src.services.analytics.services import *

router = APIRouter()

@router.get('/ranking/comedor')
def obtener_ranking_comedor(FechaInicio: str = Query(description='Fecha de inicio del analisis', default=None), 
    fechaFinal: str = Query(description='Fecha final del analisis', default=None)):

    return obtener_plato_mas_vendido(FechaFinal=fechaFinal, FechaInicio=FechaInicio)

@router.get('/ranking/comedor/horas')
def obtener_ranking_comedor(FechaInicio: str = Query(description='Fecha de inicio del analisis', default=None), 
    fechaFinal: str = Query(description='Fecha final del analisis', default=None)):

    return obtener_horas_mas_vendidas(FechaFinal=fechaFinal, FechaInicio=FechaInicio)
