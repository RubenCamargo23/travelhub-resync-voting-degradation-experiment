#!/bin/bash

# Requiere que PostgreSQL esté iniciado

# echo "Verificando si PostgreSQL está instalado..."
# if ! command -v psql &> /dev/null
# then
#     echo "PostgreSQL no encontrado. Instalando con Homebrew..."
#     brew install postgresql@14
#     brew services start postgresql@14
#     echo "Instalado. Esperando arranque..."
#     sleep 5
# fi

echo "Creando bases de datos para experimentos..."

createdb bookings_db || echo "bookings_db ya existe"
createdb payments_db || echo "payments_db ya existe"
createdb inventory_db || echo "inventory_db ya existe"
createdb monitor_db || echo "monitor_db ya existe"

echo "Bases de datos creadas."
echo "'start_backend.sh' configurando conexiones."
