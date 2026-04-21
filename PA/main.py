from sqlmodel import Session, select, text
from src.config.database import db_engine
from sqlalchemy import select as sa_select, func, cast
import os

import time
from watchdog.observers import Observer
from logs import logsApp
import json

log = logsApp.Logs()
ARCHIVO_ESTADO = './JsonTimeStamp/estado_archivos.json'

def main():
    Nuevos = validarNuevosArchivos()
    validarTimeStamp()
    print('PROCESOS ALMACENADOS LISTOS ^_____^')
    log.add_log("PROCESOS CARGADOS Y LISTOS",'DEBUG')


    

def guardar_estado(estado):
    with open(ARCHIVO_ESTADO, 'wa') as f:
        json.dump(estado, f, indent=4)

def validarTimeStamp():
    EstadoAnterior = None 
    if os.path.exists(ARCHIVO_ESTADO):
        with open(ARCHIVO_ESTADO, 'r') as f:
            EstadoAnterior = json.load(f)
            archivos = os.listdir('./PA/SQL/')
        log.add_log(f"Lista de archivos SQL {archivos}","DEBUG")

        # uno por uno se valida si esta, si no esta, se obtiene y se ejecuta
        for archivo in archivos:
            if '.sql' in archivo:
                ruta_completa = './PA/' + archivo
                with open(ruta_completa, 'r') as sql:
                    modificacion_actual = os.path.getmtime(ruta_completa)
                    
                    if modificacion_actual > EstadoAnterior[archivo]:
                        print(f"modificado detectado: {archivo}")
                        aplicarCambiosABD(ruta_completa)


def aplicarCambiosABD(ruta):
    with Session(db_engine) as session:
        with open(ruta, 'r') as sql:
            
            # El nombre se obtiene directamente desde el contenido del archivo y no del nombre para evitar inconsistencias 
            ArchivoSql = sql.read()
            NombreProceso =  sql.readline().replace('CREATE PROC','').strip()

            log.add_log(F" EJECUTANDO CAMBIOS A PROCESO ALMACENADO {NombreProceso}","DEBUG")

            try:
                session.flush()

                statement = text(ArchivoSql.replace('CREATE','ALTER'))
                session.exec(statement)
                session.commit()

                log.add_log(f"CAMBIOS A PROCESO {NombreProceso} EJECUTADOS CORRECTAMENTE", "INFO")

            except ValueError:
                log.add_log(f"ERROR AL CARGAR LOS CAMBIOS DEL PROCESO { NombreProceso }", "CRITICAL")


def validarNuevosArchivos():
    NombreProcesos = []
    ProcesosEjecutados = 0

    with Session(db_engine) as session:
        

        # Obtenemos los procesos almacenados desde la base
        statement = text("SELECT name, create_date, modify_date FROM sys.procedures ORDER BY name;")
        resultado = session.exec(statement)

        # filtramos los nombres
        for rows in resultado:
            for columna in rows:
                if type(columna) is str:
                    if 'sp_' in columna:
                        continue
                    NombreProcesos.append(columna)
        log.add_log(f"Lista de procesos almacenados: {NombreProcesos}","DEBUG")

        # Obtenemos los archivos desde la carpeta
        archivos = os.listdir('./PA/SQL/')
        log.add_log(f"Lista de archivos SQL {archivos}","DEBUG")

        # uno por uno se valida si esta, si no esta, se obtiene y se ejecuta
        for archivo in archivos:
            if '.sql' in archivo:

                with open('./PA/SQL/' + archivo, 'r') as sql:
                    
                    # El nombre se obtiene directamente desde el contenido del archivo y no del nombre para evitar inconsistencias 
                    NombreProceso =  sql.readline()
                    log.add_log(f"Validando -> {NombreProceso.replace('CREATE PROC','')}", "DEBUG")
                    if NombreProceso.replace('CREATE PROC','').strip() not in NombreProcesos:
                        log.add_log(F" EJECUTANDO PROCESO ALMACENADO {archivo}","DEBUG")

                        try:
                            session.flush()

                            statement = text(str(NombreProceso + sql.read()))
                            session.exec(statement)

                            session.commit()

                            log.add_log(f"PROCESO { NombreProceso.replace('CREATE PROC','').strip()} EJECUTADO CORRECTAMENTE", "INFO")
                            ProcesosEjecutados += 1
                        except ValueError:
                            log.add_log(f"ERROR AL CARGAR EL PROCESO { NombreProceso.replace('CREATE PROC','').strip()}", "CRITICAL")

    return ProcesosEjecutados

       
