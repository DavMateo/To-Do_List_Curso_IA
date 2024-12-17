# Importando las librerías necesarias
from typing import Optional
from pydantic import BaseModel

class Tarea(BaseModel):
    id: Optional[int] = None
    titulo: str
    descripcion: str
    estado: bool