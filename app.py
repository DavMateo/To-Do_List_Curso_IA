# Importando las librerías necesarias
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routes.tareasCrud import tareas

app = FastAPI(
    title="To-Do List web App",
    description="Aplicación construida sobre Python bajo interfaz gráfica HTML5, CSS3 y JS Vanilla que consiste en una lista para la administración de deberes, útil para el día a día",
    version="0.0.1",
    openapi_tags=[{
        "name": "tareas",
        "description": "Grupo de administración de tareas"
    }]
)

# Montando los archivos estáticos del servidor (GUI)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ruta principal para la interfaz gráfica
@app.get("/")
async def server_index():
    return FileResponse("static/index.html")


app.include_router(tareas)