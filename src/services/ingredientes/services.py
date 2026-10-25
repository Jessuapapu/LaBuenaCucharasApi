from sqlmodel import select, Session
from datetime import datetime, timedelta
import math
from typing import Optional
from src.config.database import db_engine
from src.models.ingredientes.models import Ingredientes
from src.models.proveedores.models import RegistroDeAbastecimiento, DetallesRegistroIngredientes
from src.schemas.ingredientes import IngredienteCreateSchema, IngredienteUpdateSchema
import json
import os
from typing import Dict

JSON_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "perecederos_config.json")

def _cargar_json() -> Dict[str, dict]:
    # Crea el archivo y la carpeta si no existen
    if not os.path.exists(JSON_FILE_PATH):
        os.makedirs(os.path.dirname(JSON_FILE_PATH), exist_ok=True)
        with open(JSON_FILE_PATH, 'w') as f:
            json.dump({}, f)
        return {}
        
    try:
        with open(JSON_FILE_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al leer JSON: {e}")
        return {}

def _guardar_json(data: Dict[str, dict]):
    try:
        os.makedirs(os.path.dirname(JSON_FILE_PATH), exist_ok=True)
        with open(JSON_FILE_PATH, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error al guardar JSON: {e}")

def actualizar_configuracion_perecedero(id_ingrediente: int, vida_util: int, consumo_semanal: int):
    data = _cargar_json()
    data[str(id_ingrediente)] = {
        "vida_util_semanas": vida_util,
        "consumo_semanal": consumo_semanal
    }
    _guardar_json(data)

def obtener_toda_la_configuracion() -> dict:
    return _cargar_json()

def eliminar_configuracion_perecedero(id_ingrediente: int):
    data = _cargar_json()
    id_str = str(id_ingrediente)
    if id_str in data:
        del data[id_str]
        _guardar_json(data)

def obtener_configuracion_perecedero(id_ingrediente: int) -> dict | None:
    data = _cargar_json()
    return data.get(str(id_ingrediente))

# ------------------------------------------------------------------------------

def listar_ingredientes(pagina: int = 1, rows: int = 10, todo: int = 0):
    with Session(db_engine) as session:
        try:
            query = select(Ingredientes)
            if not todo:
                offset = (pagina - 1) * rows
                query = query.order_by(Ingredientes.IdIngrediente).offset(offset).limit(rows)
            resultados = session.exec(query).all()

            lista_enriquecida = []
            configuraciones = obtener_toda_la_configuracion()

            for ingrediente in resultados:
                ing_dict = ingrediente.dict()
                conf = configuraciones.get(str(ingrediente.IdIngrediente), {})
                ing_dict["VidaUtilSemanas"] = conf.get("vida_util_semanas")
                ing_dict["ConsumoSemanalAprox"] = conf.get("consumo_semanal")
                lista_enriquecida.append(ing_dict)

            return lista_enriquecida
        except Exception as e:
            print(f"Error al listar ingredientes: {e}")
            return None

def obtener_ingrediente_por_id(id_ingrediente: int):
    with Session(db_engine) as session:
        try:
            ingrediente = session.get(Ingredientes, id_ingrediente)
            if not ingrediente: return None
                
            ing_dict = ingrediente.dict()
            conf = obtener_configuracion_perecedero(id_ingrediente) or {}
            ing_dict["VidaUtilSemanas"] = conf.get("vida_util_semanas")
            ing_dict["ConsumoSemanalAprox"] = conf.get("consumo_semanal")
            
            return ing_dict
        except Exception as e:
            print(f"Error al obtener ingrediente: {e}")
            return None

def crear_ingrediente(payload: IngredienteCreateSchema, username: Optional[str] = None) -> bool:
    with Session(db_engine) as session:
        try:
            nuevo_ingrediente = Ingredientes(
                NombreIngrediente=payload.NombreIngrediente,
                StockIngredientes=payload.StockIngredientes
            )
            session.add(nuevo_ingrediente)
            session.flush() 
            
            actualizar_configuracion_perecedero(
                id_ingrediente=nuevo_ingrediente.IdIngrediente,
                vida_util=payload.VidaUtilSemanas,
                consumo_semanal=payload.ConsumoSemanalAprox
            )
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al crear ingrediente: {e}")
            return False

def actualizar_ingrediente(id_ingrediente: int, payload: IngredienteUpdateSchema, username: Optional[str] = None) -> bool:
    with Session(db_engine) as session:
        try:
            ingrediente = session.get(Ingredientes, id_ingrediente)
            if not ingrediente: return False
            
            if payload.NombreIngrediente is not None:
                ingrediente.NombreIngrediente = payload.NombreIngrediente
            if payload.StockIngredientes is not None:
                ingrediente.StockIngredientes = payload.StockIngredientes
                
            session.add(ingrediente)
            
            conf_actual = obtener_configuracion_perecedero(id_ingrediente) or {}
            nueva_vida = payload.VidaUtilSemanas if payload.VidaUtilSemanas is not None else conf_actual.get("vida_util_semanas", 1)
            nuevo_consumo = payload.ConsumoSemanalAprox if payload.ConsumoSemanalAprox is not None else conf_actual.get("consumo_semanal", 1)
            
            actualizar_configuracion_perecedero(id_ingrediente, nueva_vida, nuevo_consumo)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al actualizar ingrediente: {e}")
            return False

def eliminar_ingrediente(id_ingrediente: int, username: Optional[str] = None) -> bool:
    with Session(db_engine) as session:
        try:
            ingrediente = session.get(Ingredientes, id_ingrediente)
            if not ingrediente: return False
            
            session.delete(ingrediente)
            eliminar_configuracion_perecedero(id_ingrediente)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al eliminar ingrediente: {e}")
            return False

def analisis_inventario_perecederos(id_ingrediente: Optional[int] = None):
    with Session(db_engine) as session:
        try:
            ahora = datetime.now()
            configuraciones = obtener_toda_la_configuracion()
            reporte = []

            statement = (
                select(DetallesRegistroIngredientes, RegistroDeAbastecimiento.Fecha)
                .join(RegistroDeAbastecimiento)
                .order_by(RegistroDeAbastecimiento.Fecha.desc())
            )
            
            if id_ingrediente:
                statement = statement.where(DetallesRegistroIngredientes.IdIngrediente == id_ingrediente)
            
            resultados = session.exec(statement).all()
            
            ultimos_ingresos = {}
            for detalle, fecha_ingreso in resultados:
                if detalle.IdIngrediente not in ultimos_ingresos:
                    ultimos_ingresos[detalle.IdIngrediente] = {
                        "detalle": detalle,
                        "fecha": fecha_ingreso
                    }

            for id_ing, info in ultimos_ingresos.items():
                conf = configuraciones.get(str(id_ing))
                if not conf: continue
                    
                vida_util_semanas = conf.get("vida_util_semanas", 1)
                consumo_semanal = conf.get("consumo_semanal", 1)
                
                fecha_ingreso = info["fecha"]
                fecha_caducidad = fecha_ingreso + timedelta(weeks=vida_util_semanas)
                
                dias_desde_ingreso = (ahora - fecha_ingreso).days
                semanas_desde_ingreso = dias_desde_ingreso / 7.0
                cantidad_consumida_estimada = math.floor(semanas_desde_ingreso * consumo_semanal)
                
                stock_inicial_lote = info["detalle"].TotalIngresado
                stock_estimado_restante = max(0, stock_inicial_lote - cantidad_consumida_estimada)
                
                semanas_restantes_stock = stock_estimado_restante / consumo_semanal if consumo_semanal > 0 else 0
                dias_restantes_stock = math.floor(semanas_restantes_stock * 7)
                
                estado_caducidad = "VIGENTE"
                if ahora > fecha_caducidad:
                    estado_caducidad = "CADUCADO"
                elif (fecha_caducidad - ahora).days <= 3:
                    estado_caducidad = "POR_VENCER"
                    
                estado_stock = "NORMAL"
                if stock_estimado_restante <= 0:
                    estado_stock = "AGOTADO"
                elif semanas_restantes_stock <= 1:
                    estado_stock = "POR_ACABAR"

                reporte.append({
                    "IdIngrediente": id_ing,
                    "UltimoRegistroAbastecimiento": info["detalle"].IdRegistroAbastecimiento,
                    "FechaUltimoIngreso": fecha_ingreso,
                    "FechaEstimadaCaducidad": fecha_caducidad,
                    "StockIngresadoEnLote": stock_inicial_lote,
                    "StockEstimadoRestante": stock_estimado_restante,
                    "DiasEstimadosParaAgotar": dias_restantes_stock,
                    "EstadoCaducidad": estado_caducidad,
                    "EstadoStock": estado_stock
                })
                
            return reporte
        except Exception as e:
            print(f"Error en análisis de inventario: {e}")
            return None