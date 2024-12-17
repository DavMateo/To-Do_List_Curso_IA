from pydantic import BaseModel
from typing import List

class TareaExportada(BaseModel):
    id: int
    titulo: str
    descripcion: str
    estado: bool