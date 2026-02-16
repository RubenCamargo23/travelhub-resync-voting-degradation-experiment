import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
    { path: 'experiments', loadChildren: () => import('./experiments/experiments.module').then(m => m.ExperimentsModule) },
    { path: '', redirectTo: 'experiments', pathMatch: 'full' }
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule { }
