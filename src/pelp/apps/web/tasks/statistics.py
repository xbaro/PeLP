""" Tasks related to statistics management """
from django.db.models import Q, F
from django.utils import timezone
from pelp import celery_app
from pelp.apps.web import lib
from pelp.apps.web import models


@celery_app.task
def update_activity_statistics():
    """
        Update statistics for active activities
    """
    # Active with no statistics or modified
    active_no_stats = models.Activity.objects.filter(
        Q(start__isnull=True) | Q(start__isnull=False, start__lte=timezone.now()),
        Q(end__isnull=True) | Q(end__isnull=False, end__gte=timezone.now()),
        Q(statisticsactivity__isnull=True) | Q(statisticsactivity__isnull=False,
                                               statisticsactivity__updated_at__lte=F('updated_at'))
    )
    # Activities with new submissions
    new_submissions = models.Activity.objects.filter(
        submission__submitted_at__gte=F('statisticsactivity__updated_at')
    )
    # Activities with new results
    new_results = models.Activity.objects.filter(
        learnerresult__last_submission__submitted_at__gte=F('statisticsactivity__updated_at')
    )
    # Activities with new feedback
    new_feedback = models.Activity.objects.filter(
        activityfeedback__updated_at__gte=F('statisticsactivity__updated_at')
    )

    activities = active_no_stats | new_submissions | new_results | new_feedback
    for activity in activities.distinct().all():
        lib.statistics.update_activity_statistics(activity)

    return None

