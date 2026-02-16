#!/bin/bash
echo "Instalando dependencias para API Gateway..."
pip3 install -r api-gateway/requirements.txt

echo "Instalando dependencias para Microservicio Búsqueda..."
pip3 install -r microservicio-busqueda/requirements.txt

echo "Instalando dependencias para Microservicio Reservas..."
pip3 install -r microservicio-reservas/requirements.txt

echo "Instalando dependencias para Microservicio Pagos..."
pip3 install -r microservicio-pagos/requirements.txt

echo "Instalando dependencias para Microservicio Inventario..."
pip3 install -r microservicio-inventario/requirements.txt

echo "Instalando dependencias para Microservicio Análisis..."
pip3 install -r microservicio-analisis/requirements.txt

echo "Instalando dependencias para Microservicio Monitor..."
pip3 install -r microservicio-monitor/requirements.txt

echo "Todas las dependencias instaladas."
