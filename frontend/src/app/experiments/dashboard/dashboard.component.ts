
import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivityService } from '../../services/activity.service';

interface ServiceStatus {
    id: string;
    name: string;
    status: 'online' | 'offline' | 'degraded' | 'maintenance';
    description: string;
    detailedInfo?: string; // HTML content
    tags: string[];
    lastUpdated: string;
    url?: string;
}

@Component({
    selector: 'app-dashboard',
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.css'],
    standalone: false
})
export class DashboardComponent {

    // URLs
    RESERVAS_URL = 'http://127.0.0.1:5002';
    GATEWAY_URL = 'http://127.0.0.1:5007';

    services: ServiceStatus[] = [
        {
            id: 'reservas',
            name: 'Microservicio Reservas',
            status: 'online',
            description: 'Gestiona la creación y administración de reservas.',
            detailedInfo: `
                <h3>Hipótesis 1: Si un microservicio cae y vuelve, puede resincronizar su estado automáticamente</h3>
                <p>Crea una reserva y verifica que el Inventario (logs) procese el evento.</p>
                <h3>Tácticas de Arquitectura:</h3>
                <ul>
                    <li>
                        <strong>State Recovery Manager:</strong> Reconstrucción del estado del servicio a partir del Event Log.
                        <br><em>Implementación:</em> Tabla <code>reservation_events</code> persiste todos los cambios. Inventario consulta esta tabla al iniciar para sincronizarse sin depender de Reservas.
                    </li>
                    <li>
                        <strong>Comunicación Asíncrona:</strong> Reducción del acoplamiento temporal mediante propagación de eventos.
                        <br><em>Implementación:</em> Patrón <strong>Outbox</strong>. Reservas guarda el evento localmente y responde inmediatamente. Un <strong>Polling Consumer</strong> en Inventario procesa los eventos pendientes asíncronamente.
                    </li>
                </ul>
            `,
            tags: ['Core', 'Base de Datos'],
            lastUpdated: 'Recién'
        },
        {
            id: 'pagos',
            name: 'Microservicio Pagos',
            status: 'online',
            description: 'Procesa pagos y consenso entre réplicas.',
            detailedInfo: `
                <h3>Hipótesis 2: Un sistema de votación con 5 réplicas puede detectar una réplica defectuosa mediante consenso</h3>
                <p>Intenta pagar una reserva usando 5 réplicas (una fallará).</p>
                <h3>Tácticas de Arquitectura:</h3>
                <ul>
                    <li>
                        <strong>Replicación de Servicios (Active-Active):</strong> Redundancia mediante múltiples instancias activas.
                        <br><em>Implementación:</em> <code>ThreadPoolExecutor</code> lanza 5 peticiones HTTP paralelas a instancias (<code>replica_id=1..5</code>) del servicio de Pagos.
                    </li>
                    <li>
                        <strong>Votación (Voting) / Consenso:</strong> Comparación de resultados para enmascarar fallos bizantinos.
                        <br><em>Implementación:</em> Algoritmo de mayoría simple (>=3) usando <code>Counter</code>. Valida si la respuesta más común es correcta y descarta la minoría errónea.
                    </li>
                </ul>
            `,
            tags: ['Finanzas', 'Seguridad'],
            lastUpdated: 'Hace 1 min'
        },
        {
            id: 'inventario',
            name: 'Microservicio Inventario',
            status: 'online',
            description: 'Gestiona la disponibilidad de productos.',
            detailedInfo: '<p>Servicio encargado del stock. Se sincroniza con Reservas mediante eventos asíncronos.</p>',
            tags: ['Logística'],
            lastUpdated: 'Hace 5 min'
        },
        {
            id: 'monitor',
            name: 'Microservicio Monitor',
            status: 'degraded',
            description: 'Monitoreo de salud del sistema.',
            detailedInfo: '<p>Monitorea la salud de los servicios y alerta sobre degradaciones o fallos.</p>',
            tags: ['Infraestructura'],
            lastUpdated: 'Hace 10 min'
        },
        {
            id: 'busqueda',
            name: 'Microservicio Búsqueda',
            status: 'online',
            description: 'Funcionalidad de búsqueda vía Gateway.',
            detailedInfo: `
                <h3>Hipótesis 3: Un Circuit Breaker puede degradar funcionalidad automáticamente sin que el usuario perciba error</h3>
                <p>Busca a través del Gateway. Si Busqueda cae, verás respuesta fallback.</p>
                <h3>Tácticas de Arquitectura:</h3>
                <ul>
                    <li>
                        <strong>Circuit Breaker:</strong> Detección y aislamiento de fallos para evitar cascadas.
                        <br><em>Implementación:</em> Lógica en <strong>API Gateway</strong> cuenta fallos consecutivos (Threshold=3). Si se supera, bloquea tráfico hacia Busqueda por 30s (Open State).
                    </li>
                    <li>
                        <strong>Degradación Funcional (Functional Degradation):</strong> Ofrecer funcionalidad reducida en lugar de fallar completamente.
                        <br><em>Implementación:</em> El Gateway retorna un JSON <em>fallback</em> (datos estáticos/vacíos) cuando el circuito está abierto, evitando error 500 al cliente.
                    </li>
                </ul>
            `,
            tags: ['Gateway', 'Búsqueda'],
            lastUpdated: 'Recién'
        }
    ];

    constructor(private http: HttpClient, private activityService: ActivityService) { }

    private pollingInterval: any;
    MONITOR_URL = 'http://127.0.0.1:5006';

    ngOnInit() {
        this.startPolling();
    }

    ngOnDestroy() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
    }

    startPolling() {
        // Initial fetch
        this.checkServicesStatus();

        // Poll every 5 seconds
        this.pollingInterval = setInterval(() => {
            this.checkServicesStatus();
        }, 5000);
    }

    checkServicesStatus() {
        this.http.get<any>(`${this.MONITOR_URL}/health-check`)
            .subscribe({
                next: (statusReport) => {
                    this.updateServiceStatus(statusReport);
                },
                error: (err) => {
                    console.error('Error polling monitor:', err);
                    // If monitor is down, mark all as potentially unknown or handle gracefully
                    // For now, we assume monitor might be down if we can't reach it
                }
            });
    }

    updateServiceStatus(report: any) {
        this.services.forEach(service => {
            const newStatus = report[service.id];
            if (newStatus) {
                // Map 'online'/'offline' to ServiceStatus type
                // If service was 'degraded' logic might be complex, but for now map simplest
                if (service.id === 'monitor') return; // Skip monitor self-update optimization if needed

                // Keep 'degraded' if backend reports it (not implemented yet, backend only says online/offline)
                // Or override. Let's simple override.

                if (service.status !== newStatus) {
                    service.status = newStatus;
                    service.lastUpdated = 'Ahora';
                }
            }
        });
    }

    testH1() {
        this.activityService.addActivity('Iniciando prueba de creación de reserva...', 'Frontend', 'info');
        this.http.post(`${this.RESERVAS_URL}/reservas`, { cliente: "Tester", monto: 100 })
            .subscribe({
                next: (res: any) => {
                    const msg = `Reserva creada: ID ${res.id || 'N/A'}`;
                    this.activityService.addActivity(msg, 'Servicio Reservas', 'success');
                },
                error: (err) => {
                    this.activityService.addActivity(`Error al crear reserva: ${err.message}`, 'Servicio Reservas', 'error');
                }
            });
    }

    testH2() {
        this.activityService.addActivity('Iniciando prueba de pago con consenso...', 'Frontend', 'info');
        this.http.post(`${this.RESERVAS_URL}/reservas/1/pagar`, {})
            .subscribe({
                next: (res: any) => {
                    this.activityService.addActivity('Pago procesado exitosamente.', 'Servicio Pagos', 'success');
                },
                error: (err) => {
                    this.activityService.addActivity(`Pago falló: ${err.message}`, 'Servicio Pagos', 'error');
                }
            });
    }

    testH3() {
        this.activityService.addActivity('Iniciando prueba de búsqueda...', 'Frontend', 'info');
        this.http.get(`${this.GATEWAY_URL}/search`)
            .subscribe({
                next: (res: any) => {
                    this.activityService.addActivity('Búsqueda completada exitosamente.', 'Gateway', 'success');
                },
                error: (err) => {
                    this.activityService.addActivity(`Búsqueda falló: ${err.message}`, 'Gateway', 'error');
                }
            });
    }
}
