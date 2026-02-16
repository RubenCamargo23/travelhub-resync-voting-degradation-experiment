# TravelHub: Resync, Voting & Degradation Experiment

Este repositorio contiene un banco de pruebas integral (**Frontend Angular** + **Microservicios Flask**) diseñado para validar tácticas de disponibilidad y resiliencia en arquitecturas ágiles. El sistema simula una plataforma de reservas de viajes desplegada en **Heroku**.

## Integrantes
* Diego Rojas
* David Rojas
* Brian Martinez
* Ruben Camargo

## Hipótesis del Experimento

El proyecto busca validar tres comportamientos críticos ante fallas:

1. **Resincronización de Estado (Event Polling):** Si un microservicio cae y vuelve, puede recuperar su consistencia automáticamente consultando el `Event Log` en PostgreSQL al reincorporarse.
2. **Consenso por Votación (BFT):** Un sistema de votación con 5 réplicas puede detectar una réplica defectuosa mediante consenso (mayoría), asegurando que el usuario no perciba errores de cálculo.
3. **Degradación Funcional (Circuit Breaker):** Un Circuit Breaker puede degradar funcionalidad automáticamente sin que el usuario perciba un error 5xx, protegiendo la estabilidad del sistema.

---

## Listado de Componentes (Microservicios)

| Microservicio | Propósito y Comportamiento Esperado | Tecnología Asociada |
| :--- | :--- | :--- |
| **Frontend Web** | Interfaz de usuario para búsquedas y reservas. | Angular (Web Dyno) |
| **API Gateway** | Punto de entrada único con **Circuit Breaker**. Abre el circuito tras 5 fallas consecutivas. | Python 3.11, Flask 3.0, `circuitbreaker 1.4` |
| **M. Búsqueda** | Gestión de ofertas con **Redis Cache** (5ms latencia vs 50ms en DB). | Flask, Redis 5.0.1, PostgreSQL |
| **M. Reservas** | Orquestador de flujo; genera el log de `reservation_events` para consistencia. | Flask, SQLAlchemy 2.0, PostgreSQL |
| **M. Pagos** | Procesamiento con **Votación** (5 réplicas en paralelo). Detecta fallas en < 2 min. | Flask, `concurrent.futures`, PostgreSQL |
| **M. Inventario** | Gestión de stock con **Polling cada 10s** para resincronizar eventos. | Flask, `APScheduler 3.10`, PostgreSQL |
| **M. Monitor** | **Detección Dual**: Compara Ping/Echo (5 min) vs Heartbeat (cada 30s). | Flask, `requests 2.31`, MonitorDB |
| **M. Análisis** | Analytics aislado; su caída NO afecta la operación normal del sistema. | Flask, `APScheduler`, AnalyticsDB |

---

## Infraestructura y Conectores
* **Bases de Datos:** PostgreSQL 15 para persistencia y Redis para caché de alta velocidad.
* **Mensajería:** Comunicación síncrona vía HTTP/REST y asíncrona mediante Polling/Event Log en DB.
* **Monitoreo:** Mecanismo de Heartbeat donde los servicios escriben cada 30s y el monitor valida cada minuto.

---

## Instalación y Ejecución Desde Cero

### 1. Prerrequisitos
*   **Python 3.10+**
*   **Node.js 18+ (LTS)**
*   **Angular CLI 15+** (`npm install -g @angular/cli`)
*   **PostgreSQL 14+**

#### Instalación en macOS (Homebrew)
La forma más sencilla es usar Homebrew.
```bash
brew install postgresql@16
brew services start postgresql@16
```
*Por defecto no configura contraseña, lo cual es ideal para desarrollo local.*

#### Instalación en Windows
1.  Descarga el instalador desde [postgresql.org/download/windows](https://www.postgresql.org/download/windows/).
2.  Ejecuta el instalador. Mantén el puerto `5432` por defecto.
3.  **Importante:** Te pedirá una contraseña para el superusuario `postgres`. Anótala (ej: `admin`).
4.  Al finalizar, abre **pgAdmin** o la terminal SQL Shell (psql).
5.  **Configuración del Proyecto:**
    *   En Windows, deberás editar el archivo `scripts/start_backend.sh` (o ejecutar manualmente) para incluir tu contraseña:
    *   `export DATABASE_URL="postgresql://postgres:admin@localhost/bookings_db"`

### 2. Configuración del Backend (Python)
Se recomienda crear un entorno virtual para aislar las dependencias:

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias de cada microservicio
pip install -r api-gateway/requirements.txt
pip install -r microservicio-reservas/requirements.txt
pip install -r microservicio-busqueda/requirements.txt
pip install -r microservicio-pagos/requirements.txt
pip install -r microservicio-inventario/requirements.txt
pip install -r microservicio-analisis/requirements.txt
pip install -r microservicio-monitor/requirements.txt
```

### 3. Configuración del Frontend (Angular)
```bash
cd frontend
npm install
```

### 4. Ejecución del Sistema

#### Opción A: Automática (Script Helper)
Hemos creado un script que levanta todos los microservicios backend en segundo plano.

```bash
# Desde la raíz del proyecto
chmod +x scripts/start_backend.sh
./scripts/start_backend.sh
```

Luego, en **otra terminal**, levanta el frontend:
```bash
cd frontend
ng serve
```
Accede a: [http://localhost:4200](http://localhost:4200)

#### Opción B: Manual (Microservicio por Microservicio)
Si prefieres controlar cada proceso individualmente (útil para debugging), abre una terminal por servicio:

1.  **API Gateway (Puerto 5007):**
    ```bash
    cd api-gateway && python app.py
    ```
2.  **Búsqueda (Puerto 5001):**
    ```bash
    cd microservicio-busqueda && python app.py
    ```
3.  **Reservas (Puerto 5002):**
    ```bash
    cd microservicio-reservas && python app.py
    ```
4.  **Pagos (Puerto 5003):**
    ```bash
    cd microservicio-pagos && python app.py
    ```
5.  **Inventario (Puerto 5004):**
    ```bash
    cd microservicio-inventario && python app.py
    ```
6.  **Análisis (Puerto 5005):**
    ```bash
    cd microservicio-analisis && python app.py
    ```
7.  **Monitor (Puerto 5006):**
    ```bash
    cd microservicio-monitor && python app.py
    ```
8.  **Frontend:**
    ```bash
    cd frontend && ng serve
    ```

---

## Guía de Pruebas (Validación de Hipótesis)

El proyecto incluye un **Dashboard de Experimentos** en el Frontend (`http://localhost:4200`) para validar las 3 hipótesis de forma interactiva. A continuación se detalla cómo probar cada una.

### 1. Hipótesis 1: Resincronización y Comunicación Asíncrona (State Recovery)
**Objetivo:** Verificar que el sistema no falla si un componente (Inventario) cae, y que se recupera automáticamente.
*   **Prueba:**
    1.  Detener el proceso de `microservicio-inventario`.
    2.  Crear una reserva desde el Frontend (recibirás confirmación inmediata gracs al patrón **Outbox**).
    3.  Reiniciar `microservicio-inventario`.
    4.  Observar en los logs cómo detecta los eventos pendientes y actualiza su stock.

### 2. Hipótesis 2: Votación y Consenso Mayoría (Fault Tolerance)
**Objetivo:** Verificar que el sistema detecta y aisla una réplica corrupta.
*   **Prueba:**
    1.  El sistema simula 5 réplicas de Pagos. La réplica #5 está programada para fallar (retorna monto x10).
    2.  Ejecutar "Pagar Reserva (Consenso)" desde el Frontend.
    3.  El sistema realizará un **Fan-Out** a las 5 réplicas.
    4.  Verificar que el resultado es "Exitoso" y que el json muestra `votos: 4` (valor correcto) vs `1` (valor corrupto), confirmando que el algoritmo de mayoría funcionó.

### 3. Hipótesis 3: Circuit Breaker y Degradación Funcional (Resilience)
**Objetivo:** Verificar que el Gateway deja de saturar un servicio caído y ofrece una respuesta degradada.
*   **Prueba:**
    1.  Detener el proceso de `microservicio-busqueda` (puerto 5001).
    2.  Intentar "Buscar" desde el Frontend 3 veces (verás errores 500/Timeout).
    3.  Al 4to intento, el **Circuit Breaker** se abre.
    4.  Verificar que recibes una respuesta **inmediata** (sin timeout) con origen `"Fallback"`. Esto confirma que el sistema se degradó funcionalmente para protegerse.
    5.  (Opcional) Reiniciar el servicio y esperar 30s para que el circuito se cierre.

---

## Conexión a Base de Datos (PostgreSQL)

Para inspeccionar los datos generados por los microservicios, puedes usar cualquier cliente SQL (como **TablePlus**, **DBeaver**, **pgAdmin** o la terminal `psql`).

**Parámetros de Conexión (Instalación Homebrew por defecto):**

*   **Host:** `localhost`
*   **Port:** `5432`
*   **User:** tu usuario de mac (`rubencamargoortegon`) o `postgres`
*   **Password:** (dejar vacío)
*   **Databases:**
    *   `bookings_db` (Reservas)
    *   `payments_db` (Votos de Pagos)
    *   `inventory_db` (Stock)
    *   `monitor_db` (Logs de Monitor/Análisis)

**Ejemplo por Terminal:**

```bash
# ----- CONSULTA DE RESERVAS -----
# Conectarse a la DB de reservas
psql bookings_db
# Ver las reservas creadas
SELECT * FROM reservas;
# Ver los eventos de Outbox pendientes o procesados
SELECT * FROM reservation_events;

# ----- CONSULTA DE INVENTARIO -----
# Conectarse a la DB de inventario
psql inventory_db
# Ver si el stock bajó (cantidad inicial 100)
SELECT * FROM inventario;

# ----- CONSULTA DE PAGOS -----
# Conectarse a la DB de pagos
psql payments_db
# Ver los votos de cada réplica
SELECT * FROM payment_votes ORDER BY timestamp DESC;
```
