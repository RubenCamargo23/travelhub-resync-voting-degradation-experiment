
import { Component, Input } from '@angular/core';

@Component({
    selector: 'app-service-card',
    templateUrl: './service-card.component.html',
    styleUrls: ['./service-card.component.css'],
    standalone: false
})
export class ServiceCardComponent {
    @Input() serviceName: string = '';
    @Input() status: 'online' | 'offline' | 'degraded' | 'maintenance' = 'online';
    @Input() description: string = '';
    @Input() detailedInfo: string = '';
    @Input() tags: string[] = [];
    @Input() lastUpdated: string = '';
}
