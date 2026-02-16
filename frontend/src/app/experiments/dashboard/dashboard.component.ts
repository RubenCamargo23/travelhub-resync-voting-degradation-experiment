import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
    selector: 'app-dashboard',
    templateUrl: './dashboard.component.html',
    standalone: false
})
export class DashboardComponent {

    // URLs (assuming local dev with proxy or CORS enabled)
    // For simplicity using direct URLs assuming CORS is *
    RESERVAS_URL = 'http://127.0.0.1:5002';
    GATEWAY_URL = 'http://127.0.0.1:5007';

    h1Result: any;
    h2Result: any;
    h3Result: any;

    constructor(private http: HttpClient) { }

    testH1() {
        this.h1Result = "Creando reserva...";
        this.http.post(`${this.RESERVAS_URL}/reservas`, { cliente: "Tester", monto: 100 })
            .subscribe({
                next: (res) => this.h1Result = res,
                error: (err) => this.h1Result = err
            });
    }

    testH2() {
        this.h2Result = "Pagando con consenso...";
        // Asumimos ID reserva 1 para prueba rápida
        this.http.post(`${this.RESERVAS_URL}/reservas/1/pagar`, {})
            .subscribe({
                next: (res) => this.h2Result = res,
                error: (err) => this.h2Result = err
            });
    }

    testH3() {
        this.h3Result = "Buscando...";
        this.http.get(`${this.GATEWAY_URL}/search`)
            .subscribe({
                next: (res) => this.h3Result = res,
                error: (err) => this.h3Result = err
            });
    }
}
