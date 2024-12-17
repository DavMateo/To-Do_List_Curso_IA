# Importando las librerías necesarias
from sqlalchemy import create_engine, MetaData
from sqlalchemy_utils import database_exists, create_database
from urllib.parse import quote
from utils.envKeys import obtener_credenciales

# Realizando la conexión a la base de datos
try:
    # Obtener credenciales
    credenciales = obtener_credenciales()
    
    # Creando la creación DB y conexión automática a la base de datos correspondiente
    str_conexion_url = f"mysql+pymysql://{credenciales['user']}:{quote(credenciales['password'])}@{credenciales['host']}:{credenciales['port']}/{credenciales['database']}"
    engine = create_engine(str_conexion_url)
    
    if not database_exists(engine.url):
        create_database(engine.url)
    
    # Obteniendo el objeto de conexión
    conn = engine.connect()
    meta = MetaData()
    

except KeyError as e:
    print(f"Error: Falta una clave en las credenciales: {e}")
    engine = None
    meta = None

except Exception as ex:
    print(f"Error al configurar la base de datos: {ex}")
    engine = None
    meta = None