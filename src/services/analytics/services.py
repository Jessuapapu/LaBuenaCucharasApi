from datetime import datetime, timedelta, date
from sqlmodel import Session, text
import calendar
from src.config.database import db_engine


def obtener_rango_semana(fecha_texto):
    # Convertir el texto a un objeto datetime
    fecha = datetime.strptime(fecha_texto, "%Y-%m-%d")
    
    # .weekday() devuelve: 0=Lunes, 1=Martes, ..., 6=Domingo
    dia_semana = fecha.weekday()
    
    # Restar los días pasados para volver al Lunes
    inicio_semana = fecha - timedelta(days=dia_semana)
    
    # Sumar los días restantes para llegar al Domingo
    fin_semana = inicio_semana + timedelta(days=6)
    
    return str(inicio_semana.date()), str(fin_semana.date())

def obtener_mes():
    fecha = datetime.now()
    dias_maximos = calendar.monthrange(fecha.year, fecha.month)[1]

    return (dias_maximos,fecha.month,fecha.year)
    

def obtener_plato_mas_vendido(FechaInicio: datetime | None = None, FechaFinal: datetime | None = None):
    with Session(db_engine) as session:
        try:
            query = text("""
                EXEC pa_Analitica_Platillos_Comedor
                    @FechaInicio = :fecha_inicio,
                    @FechaFin = :fecha_fin
            """)

            if not FechaInicio and not FechaFinal:
                FechaInicio, FechaFinal = obtener_rango_semana(str(datetime.now().date()))

            valores = {
                "fecha_inicio": FechaInicio,
                "fecha_fin": str(datetime.now().date()),          
            }
            resultados = session.exec(query, params=valores).mappings().all()

            listaPlatillos = []
            for row in resultados:
                listaPlatillos.append({
                    'id_platillo': row.IdPlatillo,
                    'nombre_platillo': row.NombrePlatillo,
                    'unidades_vendidas': row.UnidadesVendidas,
                    'ingreso_total_generado': row.IngresoTotalGenerado,
                    'precio_promedio_venta': row.PrecioPromedioVenta
                })


        except:
            return None

        return listaPlatillos
    
def obtener_horas_mas_vendidas(FechaInicio: datetime | None = None, FechaFinal: datetime | None = None):
    with Session(db_engine) as session:
        try:
            query = text("""
                EXEC pa_Analitica_Top5_Horas_Comedor
                    @FechaInicio = :fecha_inicio,
                    @FechaFin = :fecha_fin
            """)
            if not FechaInicio and not FechaFinal:
                dias_maximos, mes, año = obtener_mes()
                print(dias_maximos,mes,año, date(año,mes,dias_maximos))

                FechaInicio, FechaFinal = (date(año,mes,1), date(año,mes,dias_maximos))

            elif FechaInicio and not FechaFinal:
                FechaFinal = datetime.now()

            valores = {
                "fecha_inicio": FechaInicio,
                "fecha_fin": FechaFinal,          
            }

            resultados = session.exec(query, params=valores).mappings().all()
            listaHoras = []
            for row in resultados:
                listaHoras.append({
                    'hora': row.HoraDelDia,
                    'TotalOrdenes': row.TotalOrdenesHistoricas,
                    'DiasLaborados': row.DiasLaboradosEnEsaHora,
                    'PromedioOrdenes': row.PromedioOrdenesPorDia
                })


        except:
           return None

        return listaHoras