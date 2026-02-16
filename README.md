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
