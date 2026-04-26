from sqlmodel import Session, text
from src.config.database import db_engine
import os
from logs import logsApp
import json

log = logsApp.Logs()
ARCHIVO_ESTADO = './PA/JsonTimeStamp/estado_archivos.json'


def main():
    validarNuevosArchivos()
    if validarJson():
        validarTimeStamp()

    print('PROCESOS ALMACENADOS LISTOS ^_____^')
    log.add_log("PROCESOS CARGADOS Y LISTOS",'INFO')


def validarJson():

    if not os.path.exists(ARCHIVO_ESTADO):
        print('ARCHIVO DE ESTADO NO ENCONTRADO O NO EXISTE, CREANDO UNO')
        log.add_log('ARCHIVO DE ESTADO NO ENCONTRADO O NO EXISTE, CREANDO UNO','INFO')
        guardar_estado()
        
        return False
    
    return True
    


def guardar_estado():
    timeStamp = {}
    with open(ARCHIVO_ESTADO, 'w') as f:
        archivos = os.listdir('./PA/SQL/')
        for archivo in archivos:
            if '.sql' in archivo:
                ruta_completa = './PA/SQL/' + archivo
                timeStamp[archivo] = os.path.getmtime(ruta_completa)
        
        json.dump(timeStamp,f,indent=4)

def validarTimeStamp():
    EstadoAnterior = None 

    print("VALIDADON CAMBIOPS EN LOS PA")
    with open(ARCHIVO_ESTADO, 'r') as f:
        try:        
            EstadoAnterior = json.load(f)
        except:
            guardar_estado()
            return

        archivos = os.listdir('./PA/SQL/')

    log.add_log(f"Lista de archivos SQL {archivos} ","DEBUG")

    for archivo in archivos:
        if '.sql' in archivo:
            ruta_completa = './PA/SQL/' + archivo

            with open(ruta_completa, 'r') as sql:
                modificacion_actual = os.path.getmtime(ruta_completa)
                
                if archivo not in EstadoAnterior.keys():
                    print(f"ERROR AL CARGAR ARCHIVO EN ESTADO ANTERIOR: {archivo}")
                    log.add_log(f"ERROR AL CARGAR ARCHIVO EN ESTADO ANTERIOR: {archivo}","ERROR")
                    continue
                    
                if modificacion_actual > EstadoAnterior[archivo]:
                    print(f"modificado detectado: {archivo}")
                    log.add_log(f"modificado detectado: {archivo}", "INFO")
                    aplicarCambiosABD(ruta_completa)
                    guardar_estado()
                

def aplicarCambiosABD(ruta):
    with Session(db_engine) as session:
        with open(ruta, 'r') as sql:
            
            # El nombre se obtiene directamente desde el contenido del archivo y no del nombre para evitar inconsistencias 
            ArchivoSql = sql.read()
            NombreProceso =  sql.readline().replace('CREATE PROC','').strip()

            log.add_log(F"EJECUTANDO CAMBIOS A PROCESO ALMACENADO {NombreProceso}", "INFO")

            try:
                session.flush()

                statement = text(ArchivoSql.replace('CREATE','ALTER'))
                session.exec(statement)
                session.commit()

                log.add_log(f"CAMBIOS A PROCESO {NombreProceso} EJECUTADOS CORRECTAMENTE", "INFO")

            except ValueError:
                log.add_log(f"ERROR AL CARGAR LOS CAMBIOS DEL PROCESO { NombreProceso }", "CRITICAL")
                return


def validarNuevosArchivos():
    NombreProcesos = []

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
                        log.add_log(F"EJECUTANDO PROCESO ALMACENADO {archivo}","DEBUG")

                        try:
                            session.flush()

                            statement = text(str(NombreProceso + sql.read()))
                            session.exec(statement)

                            session.commit()

                            log.add_log(f"PROCESO { NombreProceso.replace('CREATE PROC','').strip()} EJECUTADO CORRECTAMENTE", "INFO")
                        except ValueError:
                            log.add_log(f"ERROR AL CARGAR EL PROCESO { NombreProceso.replace('CREATE PROC','').strip()}", "CRITICAL")

       