# Importando las librerías necesarias
import os
from dotenv import load_dotenv

load_dotenv()


# Definiendo función para traer la información con las variables de entorno
def obtener_credenciales():
    try:
        dict_credenciales = {
            "user": os.getenv("DATABASE_USER"),
            "password": os.getenv("DATABASE_PASSWORD"),
            "host": os.getenv("DATABASE_HOST"),
            "port": os.getenv("DATABASE_PORT"),
            "database": os.getenv("DATABASE_NAME")
        }
        
        # Validar el almacenamiento de información
        for clave, valor in dict_credenciales.items():
            if not valor:
                raise ValueError(f"La variable de entorno '{clave}' no está definida o está vacía")
            
        return dict_credenciales
    
    except OSError as e:
        raise OSError("Error al obtener la información solicitada", e)
    
    except Exception as ex:
        raise Exception("Ha ocurrido un error inesperado. Inténtelo de nuevo", ex)