#!/bin/bash

# Obtener el directorio del script (¡SOLUCIÓN A LA RUTA!)
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Directorio del proyecto: $PROJECT_DIR"

# Obtener la distribución
DISTRO=$(lsb_release -i -s 2>/dev/null || cat /etc/os-release | grep ^ID= | cut -d= -f2 | tr -d '"')
echo "Distribución: $DISTRO"

# Funciones para instalar Python y MySQL (más organizado y legible)
install_python() {
  echo "Intentando instalar Python 3.12..."
  case "$DISTRO" in
    "arch") sudo pacman -S --noconfirm python python-pip ;;
    "debian"|"ubuntu"|"linuxmint") sudo apt update && sudo apt install software-properties-common -y && sudo add-apt-repository ppa:deadsnakes/ppa -y && sudo apt update && sudo apt install python3.12 python3.12-venv python3.12-dev -y ;;
    "fedora"|"centos"|"rhel") sudo dnf install epel-release -y && sudo dnf install python3.12 python3.12-devel python3.12-venv -y ;;
    "opensuse-tumbleweed"|"opensuse-leap") sudo zypper install python312 python312-devel python312-venv -y ;;
    *) echo "Instalación automática de Python no soportada para $DISTRO. Instale Python 3.12 manualmente."; return 1 ;;
  esac
  if ! command -v python3.12 &>/dev/null; then echo "Error en la instalación de Python. Revise los mensajes anteriores."; return 1; fi
  echo "Python 3.12 instalado correctamente."
  return 0
}

install_mysql() {
    echo "Intentando instalar MySQL..."
    case "$DISTRO" in
      "arch") echo "En Arch Linux, se recomienda instalar MySQL desde AUR (ej: \`yay -S mysql\`)."; return 1 ;;
      "debian"|"ubuntu"|"linuxmint") sudo apt update && sudo apt install mysql-server -y ;;
      "fedora"|"centos"|"rhel") sudo dnf install mysql-server -y && sudo mysql_secure_installation ;;
      "opensuse-tumbleweed"|"opensuse-leap") sudo zypper install mysql-community-server -y ;;
      *) echo "Instalación automática de MySQL no soportada para $DISTRO. Instale MySQL manualmente."; return 1 ;;
    esac
    if ! command -v mysql &>/dev/null; then echo "Error en la instalación de MySQL. Revise los mensajes anteriores."; return 1; fi
    echo "MySQL instalado correctamente."
    return 0
}

# Verificar e instalar Python (con mensaje más claro si se omite la instalación)
if ! command -v python3.12 &>/dev/null; then
  read -r -p "Desea instalar Python 3.12? (s/n): " install_python_prompt
  [[ "$install_python_prompt" == "s" ]] && install_python || { echo "Python 3.12 es necesario para continuar. Saliendo."; exit 1; }
fi

if python3.12 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" &>/dev/null; then
    echo "Python version compatible (3.10 or greater) is installed."
else
    echo "Python 3.12 está instalado pero es una versión inferior a la 3.10, actualice su version de Python."
    exit 1
fi

# Verificar e instalar MySQL (con mensaje más claro si se omite la instalación)
if ! command -v mysql &>/dev/null; then
  read -r -p "Desea instalar MySQL? (s/n): " install_mysql_prompt
  [[ "$install_mysql_prompt" == "s" ]] && install_mysql || echo "Se recomienda MySQL para el funcionamiento óptimo."
fi

# Gestionar entorno virtual (con mensajes más informativos)
VENV_DIR="./venv"
if [[ -d "$VENV_DIR" ]]; then
    echo "Entorno virtual existente."
else
    echo "Creando entorno virtual..."
    python3.12 -m venv "$VENV_DIR" || { echo "Error al crear el entorno virtual. Asegúrate de tener los paquetes de desarrollo de Python instalados (python3.12-dev o python3.12-devel)."; exit 1; }
    echo "Entorno virtual creado."
fi

case "$OSTYPE" in
    "darwin"*|"linux-gnu"*|"linux-musl"*|"cygwin"*) source "$VENV_DIR/bin/activate" ;;
    "msys"*) source "$VENV_DIR/Scripts/activate" ;;
    *) echo "Activación de venv no soportada para $OSTYPE"; exit 1 ;;
esac

# Instalar dependencias
if [[ -f "requirements.txt" ]]; then
  echo "Instalando dependencias desde requirements.txt..."
  pip install --upgrade pip # Actualizar pip antes de instalar las dependencias.
  pip install -r requeriments.txt || { echo "Error al instalar las dependencias. Revise el archivo requirements.txt."; exit 1; }
  echo "Dependencias instaladas."
else
    echo "Archivo requeriments.txt no encontrado. Continuando sin instalar dependencias."
fi

# Gestionar .env (con validación de entradas y mensajes más claros)
if [[ -f ".env" ]]; then
  echo "Eliminando archivo .env existente..."
  rm .env
fi
echo "Creando archivo .env..."
touch .env

while true; do
    read -r -p "DATABASE_USER: " DATABASE_USER
    read -r -p "DATABASE_PASSWORD: " DATABASE_PASSWORD
    read -r -p "DATABASE_HOST: " DATABASE_HOST
    read -r -p "DATABASE_PORT: " DATABASE_PORT
    read -r -p "DATABASE_NAME: " DATABASE_NAME

    if [[ -z "$DATABASE_USER" || -z "$DATABASE_PASSWORD" || -z "$DATABASE_HOST" || -z "$DATABASE_PORT" || -z "$DATABASE_NAME" ]]; then
        echo "Por favor, complete todos los campos. No pueden estar vacíos."
    else
        break
    fi
done

echo "Escribiendo variables en .env..."
echo "DATABASE_USER=$DATABASE_USER" >> .env
echo "DATABASE_PASSWORD=$DATABASE_PASSWORD" >> .env
echo "DATABASE_HOST=$DATABASE_HOST" >> .env
echo "DATABASE_PORT=$DATABASE_PORT" >> .env
echo "DATABASE_NAME=$DATABASE_NAME" >> .env

echo ".env creado con éxito."

# Ejecutar la aplicación (DENTRO DEL ENTORNO VIRTUAL)
echo "Iniciando la aplicación..."
uvicorn app:app --host 0.0.0.0 --port 8000 --reload --log-level debug

echo "Configuración completada. Acceda a la aplicación en http://127.0.0.1:8000/"
