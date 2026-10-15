from sqlmodel import Session, select
from datetime import datetime, timedelta
import math
from typing import Optional
from src.config.database import get_session_context
from src.models.proveedores.models import Ingredientes, RegistroDeAbastecimiento, DetallesRegistroIngredientes
from src.schemas.ingredientes import IngredienteCreateSchema, IngredienteUpdateSchema



def analisis_inventario_perecederos(self, id_ingrediente: Optional[int] = None):
    with get_session_context() as session:
        try:
            ahora = datetime.now()
            configuraciones = obtener_toda_la_configuracion()
            reporte = []

            # 1. Obtener el ÚLTIMO ingreso de cada ingrediente (LIFO de abastecimiento)
            statement = (
                select(DetallesRegistroIngredientes, RegistroDeAbastecimiento.Fecha)
                .join(RegistroDeAbastecimiento)
                .order_by(RegistroDeAbastecimiento.Fecha.desc())
            )
            
            if id_ingrediente:
                statement = statement.where(DetallesRegistroIngredientes.IdIngrediente == id_ingrediente)
            
            resultados = session.exec(statement).all()
            
            # Filtramos en memoria para quedarnos solo con el más reciente
            ultimos_ingresos = {}
            for detalle, fecha_ingreso in resultados:
                if detalle.IdIngrediente not in ultimos_ingresos:
                    ultimos_ingresos[detalle.IdIngrediente] = {
                        "detalle": detalle,
                        "fecha": fecha_ingreso
                    }

            # 2. Calcular estado de caducidad y stock
            for id_ing, info in ultimos_ingresos.items():
                conf = configuraciones.get(str(id_ing))
                if not conf: continue # Si no está en el JSON, no lo analizamos
                    
                vida_util = conf.get("vida_util_semanas", 1)
                consumo_semana = conf.get("consumo_semanal", 1)
                fecha_ingreso = info["fecha"]
                
                # A. Matemáticas de Caducidad
                fecha_caducidad = fecha_ingreso + timedelta(weeks=vida_util)
                estado_caducidad = "VIGENTE"
                if ahora > fecha_caducidad:
                    estado_caducidad = "CADUCADO"
                elif (fecha_caducidad - ahora).days <= 3:
                    estado_caducidad = "POR_VENCER"
                
                # B. Matemáticas de Consumo (Stock estimado restante)
                semanas_desde_ingreso = (ahora - fecha_ingreso).days / 7.0
                consumido_estimado = math.floor(semanas_desde_ingreso * consumo_semana)
                
                stock_inicial_lote = info["detalle"].TotalIngresado
                stock_restante = max(0, stock_inicial_lote - consumido_estimado)
                
                semanas_restantes = stock_restante / consumo_semana if consumo_semana > 0 else 0
                
                estado_stock = "NORMAL"
                if stock_restante <= 0:
                    estado_stock = "AGOTADO"
                elif semanas_restantes <= 1:
                    estado_stock = "POR_ACABAR"

                reporte.append({
                    "IdIngrediente": id_ing,
                    "FechaUltimoIngreso": fecha_ingreso,
                    "FechaEstimadaCaducidad": fecha_caducidad,
                    "StockIngresadoEnLote": stock_inicial_lote,
                    "StockEstimadoRestante": stock_restante,
                    "DiasEstimadosParaAgotar": math.floor(semanas_restantes * 7),
                    "EstadoCaducidad": estado_caducidad,
                    "EstadoStock": estado_stock
                })
                
            return reporte
        except Exception as e:
            print(f"Error en análisis de inventario: {e}")
            return None