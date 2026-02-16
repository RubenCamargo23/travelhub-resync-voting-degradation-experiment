import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ExperimentsRoutingModule } from './experiments-routing.module';
import { DashboardComponent } from './dashboard/dashboard.component';
import { HttpClientModule } from '@angular/common/http';

@NgModule({
    declarations: [
        DashboardComponent
    ],
    imports: [
        CommonModule,
        ExperimentsRoutingModule,
        HttpClientModule
    ]
})
export class ExperimentsModule { }
