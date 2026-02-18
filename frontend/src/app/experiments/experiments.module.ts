import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ExperimentsRoutingModule } from './experiments-routing.module';
import { DashboardComponent } from './dashboard/dashboard.component';
import { HttpClientModule } from '@angular/common/http';
import { ServiceCardComponent } from '../components/service-card/service-card.component';

@NgModule({
    declarations: [
        DashboardComponent,
        ServiceCardComponent
    ],
    imports: [
        CommonModule,
        ExperimentsRoutingModule,
        HttpClientModule
    ],
})
export class ExperimentsModule { }
