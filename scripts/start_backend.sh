#!/bin/bash

# Función para matar procesos hijos al salir
trap "kill 0" EXIT

# Configuración de Bases de Datos (PostgreSQL Local)
# Asume que el usuario actual tiene acceso sin contraseña o configurada en .pgpass
export DB_HOST="localhost"
# Si necesitas usuario/pass: export DATABASE_URL="postgresql://user:pass@localhost/dbname"

echo "Iniciando Microservicios con PostgreSQL..."

# 1. API Gateway (5007)
cd api-gateway
# No requiere persistencia fuerte, pero por consistencia:
export DATABASE_URL="postgresql://$DB_HOST/monitor_db"
python3 app.py &
cd ..
echo "API Gateway iniciado en puerto 5007"

# 2. Búsqueda (5001)
cd microservicio-busqueda
export Redis_HOST="localhost"
python3 app.py &
cd ..
echo "Microservicio Búsqueda iniciado en puerto 5001"

# 3. Reservas (5002) - CRÍTICO H1/H2
cd microservicio-reservas
export DATABASE_URL="postgresql://$DB_HOST/bookings_db"
python3 app.py &
cd ..
echo "Microservicio Reservas iniciado en puerto 5002"

# 4. Pagos (5003) - CRÍTICO H2
cd microservicio-pagos
export DATABASE_URL="postgresql://$DB_HOST/payments_db"
python3 app.py &
cd ..
echo "Microservicio Pagos iniciado en puerto 5003"

# 5. Inventario (5004) - CRÍTICO H1 (Polling)
cd microservicio-inventario
export DATABASE_URL="postgresql://$DB_HOST/inventory_db"
# Esta variable habilita el Polling a la DB de Reservas (Cross-Database Read)
export RESERVAS_DB_URL="postgresql://$DB_HOST/bookings_db"
python3 app.py &
cd ..
echo "Microservicio Inventario iniciado en puerto 5004"

# 6. Análisis (5005)
cd microservicio-analisis
export DATABASE_URL="postgresql://$DB_HOST/monitor_db"
python3 app.py &
cd ..
echo "Microservicio Análisis iniciado en puerto 5005"

# 7. Monitor (5006)
cd microservicio-monitor
export DATABASE_URL="postgresql://$DB_HOST/monitor_db"
python3 app.py &
cd ..
echo "Microservicio Monitor iniciado en puerto 5006"

echo "Todos los servicios backend iniciados (Modo PostgreSQL)."
echo "Para iniciar el frontend, abre otra terminal, ve a 'frontend' y ejecuta 'ng serve'."
echo "Presiona Ctrl+C para detener todo."

wait
