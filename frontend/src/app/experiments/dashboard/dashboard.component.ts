import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivityService } from '../../services/activity.service';

interface ServiceStatus {
    id: string;
    name: string;
    status: 'online' | 'offline' | 'degraded' | 'maintenance';
    description: string;
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
            description: 'Handles booking creation and management.',
            tags: ['Core', 'Database'],
            lastUpdated: 'Just now',
            url: this.RESERVAS_URL
        },
        {
            id: 'pagos',
            name: 'Microservicio Pagos',
            status: 'online',
            description: 'Processes payments and consensus.',
            tags: ['Finance', 'Secure'],
            lastUpdated: '1 min ago'
        },
        {
            id: 'inventario',
            name: 'Microservicio Inventario',
            status: 'online',
            description: 'Manages product availability.',
            tags: ['Logistics'],
            lastUpdated: '5 mins ago'
        },
        {
            id: 'monitor',
            name: 'Microservicio Monitor',
            status: 'degraded',
            description: 'System health monitoring.',
            tags: ['Infra'],
            lastUpdated: '10 mins ago'
        },
        {
            id: 'busqueda',
            name: 'Microservicio Búsqueda',
            status: 'online',
            description: 'Search functionality via Gateway.',
            tags: ['Gateway', 'Search'],
            lastUpdated: 'Just now'
        }
    ];

    constructor(private http: HttpClient, private activityService: ActivityService) { }

    testH1() {
        this.activityService.addActivity('Initiating reservation creation test...', 'Frontend', 'info');
        this.http.post(`${this.RESERVAS_URL}/reservas`, { cliente: "Tester", monto: 100 })
            .subscribe({
                next: (res: any) => {
                    const msg = `Reserva created: ID ${res.id || 'N/A'}`;
                    this.activityService.addActivity(msg, 'Reservas Service', 'success');
                },
                error: (err) => {
                    this.activityService.addActivity(`Error creating reservation: ${err.message}`, 'Reservas Service', 'error');
                }
            });
    }

    testH2() {
        this.activityService.addActivity('Initiating payment consensus test...', 'Frontend', 'info');
        // Asumimos ID reserva 1 para prueba rápida
        this.http.post(`${this.RESERVAS_URL}/reservas/1/pagar`, {})
            .subscribe({
                next: (res: any) => {
                    this.activityService.addActivity('Payment processed successfully.', 'Pagos Service', 'success');
                },
                error: (err) => {
                    this.activityService.addActivity(`Payment failed: ${err.message}`, 'Pagos Service', 'error');
                }
            });
    }

    testH3() {
        this.activityService.addActivity('Initiating search test...', 'Frontend', 'info');
        this.http.get(`${this.GATEWAY_URL}/search`)
            .subscribe({
                next: (res: any) => {
                    this.activityService.addActivity('Search completed successfully.', 'Gateway', 'success');
                },
                error: (err) => {
                    this.activityService.addActivity(`Search failed: ${err.message}`, 'Gateway', 'error');
                }
            });
    }
}
