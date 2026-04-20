from sqlmodel import Session, select, text
from src.config.database import db_engine
from sqlalchemy import select as sa_select, func, cast
import os

def main():

    NombreProcesos = []

    with Session(db_engine) as session:
        session.flush()
        statement = text(
        "SELECT name, create_date, modify_date FROM sys.procedures ORDER BY name;"             
        )
        resultado = session.exec(statement)

        for rows in resultado:
            for columna in rows:
                if type(columna) is str:
                    if 'sp_' in columna:
                        continue
                    NombreProcesos.append(columna)

        archivos = os.listdir('./PA')

        for archivo in archivos:
            if '.sql' in archivo:
                with open('./PA/' + archivo, 'r') as sql:
                    NombreProceso =  sql.readline()
                    if NombreProceso.replace('CREATE PROC','').strip() not in NombreProcesos:
                        print(F" EJECUTANDO PROCESO ALMACENADO {archivo}")
                        statement = text(str(NombreProceso + sql.read()))
                        session.exec(statement)
        session.commit()

    print('PROCESOS ALMACENADOS LISTOS ^_____^')



    

