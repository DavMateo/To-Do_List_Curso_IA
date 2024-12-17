# Importando las librerías necesarias
from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, Boolean
from config.db import meta, engine


# Creando la tabla de MySQL
tarea_todo = Table("tarea_todo", meta,
    Column("id", Integer, primary_key=True),
    Column("titulo", String(75), nullable=False, unique=True),
    Column("descripcion", String(255), nullable=False),
    Column("estado", Boolean, nullable=False)
)

meta.create_all(engine)