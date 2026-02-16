#!/bin/bash

# Función para matar procesos hijos al salir
trap "kill 0" EXIT

echo "Iniciando Microservicios..."

# 1. API Gateway (5000)
cd api-gateway
python3 app.py &
cd ..
echo "API Gateway iniciado en puerto 5007"

# 2. Búsqueda (5001)
cd microservicio-busqueda
python3 app.py &
cd ..
echo "Microservicio Búsqueda iniciado en puerto 5001"

# 3. Reservas (5002)
cd microservicio-reservas
python3 app.py &
cd ..
echo "Microservicio Reservas iniciado en puerto 5002"

# 4. Pagos (5003)
cd microservicio-pagos
python3 app.py &
cd ..
echo "Microservicio Pagos iniciado en puerto 5003"

# 5. Inventario (5004)
cd microservicio-inventario
python3 app.py &
cd ..
echo "Microservicio Inventario iniciado en puerto 5004"

# 6. Análisis (5005)
cd microservicio-analisis
python3 app.py &
cd ..
echo "Microservicio Análisis iniciado en puerto 5005"

# 7. Monitor (5006)
cd microservicio-monitor
python3 app.py &
cd ..
echo "Microservicio Monitor iniciado en puerto 5006"

echo "Todos los servicios backend iniciados."
echo "Para iniciar el frontend, abre otra terminal, ve a 'frontend' y ejecuta 'ng serve'."
echo "Presiona Ctrl+C para detener todo."

wait
