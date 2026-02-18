import { Component, OnInit } from '@angular/core';
import { ActivityService, ActivityItem } from '../../services/activity.service';

@Component({
    selector: 'app-activity-feed',
    templateUrl: './activity-feed.component.html',
    styleUrls: ['./activity-feed.component.css'],
    standalone: false
})
export class ActivityFeedComponent implements OnInit {
    activities: ActivityItem[] = [];

    constructor(private activityService: ActivityService) { }

    ngOnInit(): void {
        this.activityService.activities$.subscribe(items => {
            this.activities = items;
        });
    }
}
