import json
from fastapi import APIRouter, File, Response, UploadFile, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from pymysql import IntegrityError
from models.tareas import tarea_todo
from schemas.tablasDB import Tarea
from schemas.exportarDB import TareaExportada
from config.db import conn
from starlette.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from sqlalchemy.orm import Session


# Definiendo el conjunto de APIs
tareas = APIRouter()


# Creando el endpoint GET '/tareas'
@tareas.get('/tareas', response_model=list[Tarea], tags=["tareas"])
def get_tareas():
    return conn.execute(tarea_todo.select()).fetchall()

# Creando el endpoint GET '/tareas/{id}'
@tareas.get('/tareas/{id}', response_model=Tarea, tags=["tareas"])
def get_tareas_por_id(id: str):
    return conn.execute(tarea_todo.select().where(tarea_todo.c.id == id)).first()

# Creando el endpoint POST '/tareas'
@tareas.post('/tareas', response_model=Tarea, tags=["tareas"])
def crear_tarea(tarea: Tarea):
    nueva_tarea = {
        "titulo": tarea.titulo,
        "descripcion": tarea.descripcion,
        "estado": tarea.estado
    }
    
    resultado = conn.execute(tarea_todo.insert().values(nueva_tarea))
    conn.commit()
    return conn.execute(tarea_todo.select().where(tarea_todo.c.id == resultado.lastrowid)).first()

# Creando el endpoint PUT '/tareas/{id}'
@tareas.put('/tareas/{id}', response_model=Tarea, tags=["tareas"])
def editar_tarea(id: str, tarea: Tarea):
    conn.execute(
        tarea_todo.update().values(
            titulo = tarea.titulo,
            descripcion = tarea.descripcion,
            estado = tarea.estado
        ).where(tarea_todo.c.id == id)
    )
    conn.commit()
    return conn.execute(tarea_todo.select().where(tarea_todo.c.id == id)).first()

# Creando el endpoint DELETE '/tareas/{id}'
@tareas.delete('/tareas/{id}', status_code=status.HTTP_204_NO_CONTENT, tags=["tareas"])
def eliminar_tarea(id: str):
    conn.execute(tarea_todo.delete().where(tarea_todo.c.id == id))
    conn.commit()
    return Response(status_code=HTTP_204_NO_CONTENT)



"""
==================================
=== EXPORTAR E IMPORTAR TAREAS ===
==================================
"""

# Exportar se usará con el get ya presente    

# Importar tareas
@tareas.post('/tareas/importar', tags=["tareas"])
async def importar_tareas(file: UploadFile = File(...)):
    try:
        # Leer el contenido del archivo
        contenido = await file.read()
        tareas_importadas = json.loads(contenido.decode("utf-8"))

        # Revisar las tareas de la importación
        for tarea in tareas_importadas:
            if not all(key in tarea for key in ("titulo", "descripcion", "estado")):
                raise HTTPException(status_code=400, detail=f"Tarea inválida: {tarea}")
            
            # Manejo de errores de duplicación caso de redundancia
            try:
                conn.execute(tarea_todo.insert().values(
                    id = tarea["id"],
                    titulo = tarea["titulo"],
                    descripcion = tarea["descripcion"],
                    estado = tarea["estado"]
                ))
                conn.commit()
            
            except IntegrityError:
                print(f"Tarea duplicada, será ignorada por el sistema: {tarea['titulo']}")
                continue
        
            except Exception as ex:
                raise HTTPException(status_code=400, detail=f"Error en los datos de la tarea: {tarea} - {ex}")
        
        return {"message": "Tareas importadas correctamente."}
    
    except json.JSONDecodeError as jsonErr:
        raise HTTPException(status_code=400, detail=f"El archivo no tiene un formato JSON válido: {jsonErr}")
    
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error al importar tareas: {str(ex)}")
