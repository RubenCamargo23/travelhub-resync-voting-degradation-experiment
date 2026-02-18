
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export interface ActivityItem {
    id: number;
    message: string;
    source: string;
    timestamp: Date;
    type: 'info' | 'success' | 'error' | 'warning';
}

@Injectable({
    providedIn: 'root'
})
export class ActivityService {
    private activitiesSubject = new BehaviorSubject<ActivityItem[]>([]);
    activities$ = this.activitiesSubject.asObservable();

    constructor() {
        // Initial mock data
        this.addActivity('System initialized.', 'System', 'info');
        this.addActivity('Microservices discovery completed.', 'Discovery', 'success');
    }

    addActivity(message: string, source: string, type: 'info' | 'success' | 'error' | 'warning' = 'info') {
        const current = this.activitiesSubject.value;
        const newItem: ActivityItem = {
            id: Date.now(),
            message,
            source,
            timestamp: new Date(),
            type
        };
        this.activitiesSubject.next([newItem, ...current]);
    }
}
