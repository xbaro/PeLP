""" Tasks related to statistics management """
from pelp import celery_app
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Avg
from django.utils import timezone
from pelp.apps.web import models
from pelp.apps.web import metrics
from prometheus_client import CollectorRegistry, push_to_gateway

@celery_app.task
def update_metrics():
    """
        Update prometheus metrics
    """
    registry = CollectorRegistry()

    # Register user metrics
    registry.register(metrics.users_total)
    registry.register(metrics.users_learners)
    registry.register(metrics.users_instructors)
    registry.register(metrics.users_admins)

    # Register submission metrics
    registry.register(metrics.submissions_execution)
    registry.register(metrics.submissions_total)
    registry.register(metrics.submissions_learners)
    registry.register(metrics.submissions_status)
    registry.register(metrics.submissions_execution_limit)

    # Register activity metrics
    registry.register(metrics.activity_num_learners)
    registry.register(metrics.activity_num_learners_with_submissions)
    registry.register(metrics.activity_num_submissions)
    registry.register(metrics.activity_score_np)
    registry.register(metrics.activity_score_a)
    registry.register(metrics.activity_score_b)
    registry.register(metrics.activity_score_cp)
    registry.register(metrics.activity_score_cm)
    registry.register(metrics.activity_score_d)
    registry.register(metrics.activity_score)
    registry.register(metrics.activity_qualification_np)
    registry.register(metrics.activity_qualification_a)
    registry.register(metrics.activity_qualification_b)
    registry.register(metrics.activity_qualification_cp)
    registry.register(metrics.activity_qualification_cm)
    registry.register(metrics.activity_qualification_d)
    registry.register(metrics.activity_qualification_pending)
    registry.register(metrics.activity_qualification)

    # Register FAQ metrics
    registry.register(metrics.faq_total)
    registry.register(metrics.faq_public_total)
    registry.register(metrics.faq_rated_total)
    registry.register(metrics.faq_rated_total_avg)

    # Update users metrics
    metrics.users_total.set(User.objects.count())
    metrics.users_admins.set(User.objects.filter(is_staff=True).count())
    metrics.users_learners.set(models.Learner.objects.count())
    metrics.users_instructors.set(models.Instructor.objects.count())

    # Update submissions metrics
    metrics.submissions_execution.set(models.Execution.objects.filter(status=4).count())
    metrics.submissions_execution_limit.set(settings.MAX_PARALLEL_RUNS)
    metrics.submissions_total.set(models.Submission.objects.count())
    metrics.submissions_status.labels(status='Preparing').set(models.Submission.objects.filter(status__lt=5).count())
    metrics.submissions_status.labels(status='Waiting').set(models.Submission.objects.filter(status=5).count())
    metrics.submissions_status.labels(status='Executing').set(models.Submission.objects.filter(status__gt=5,
                                                                                              status__lte=7).count())
    metrics.submissions_status.labels(status='Processed').set(models.Submission.objects.filter(status=8).count())
    metrics.submissions_status.labels(status='Invalid').set(models.Submission.objects.filter(status=9).count())
    metrics.submissions_status.labels(status='Error').set(models.Submission.objects.filter(status=10).count())
    metrics.submissions_status.labels(status='Timeout').set(models.Submission.objects.filter(status=11).count())
    metrics.submissions_learners.set(models.Submission.objects.filter(learner_id__gte=0).count())

    # Update FAQ metrics
    metrics.faq_total.set(models.Faq.objects.count())
    metrics.faq_public_total.set(models.Faq.objects.filter(public=True).count())
    metrics.faq_rated_total.set(models.FaqRating.objects.count())
    metrics.faq_rated_total_avg.set(models.FaqRating.objects.aggregate(Avg('rating'))['rating__avg'] or 0)

    # Update activity metrics (including active activities and ended up to 20 days ago)
    days_before = timezone.now() - timezone.timedelta(days=20)
    for activity in models.Activity.objects.filter(start__lte=timezone.now(), end__gte=days_before):
        try:
            metrics.activity_num_learners.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code
            ).set(activity.statisticsactivity.learners)
            metrics.activity_num_learners_with_submissions.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code
            ).set(activity.statisticsactivity.learners_with_submissions)
            metrics.activity_num_submissions.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code
            ).set(activity.statisticsactivity.total_submissions)
            metrics.activity_score_np.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code
            ).set(activity.statisticsactivity.score_np)
            metrics.activity_score_a.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code
            ).set(activity.statisticsactivity.score_a)
            metrics.activity_score_b.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code
            ).set(activity.statisticsactivity.score_b)
            metrics.activity_score_cp.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code
            ).set(activity.statisticsactivity.score_cp)
            metrics.activity_score_cm.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code
            ).set(activity.statisticsactivity.score_cm)
            metrics.activity_score_d.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code
            ).set(activity.statisticsactivity.score_d)
            metrics.activity_qualification_np.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code
            ).set(activity.statisticsactivity.eval_np)
            metrics.activity_qualification_a.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code
            ).set(activity.statisticsactivity.eval_a)
            metrics.activity_qualification_b.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code
            ).set(activity.statisticsactivity.eval_b)
            metrics.activity_qualification_cp.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code
            ).set(activity.statisticsactivity.eval_cp)
            metrics.activity_qualification_cm.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code
            ).set(activity.statisticsactivity.eval_cm)
            metrics.activity_qualification_d.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code
            ).set(activity.statisticsactivity.eval_d)
            metrics.activity_qualification_pending.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code
            ).set(activity.statisticsactivity.eval_pending)

            metrics.activity_score.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code,
                score='NP'
            ).set(activity.statisticsactivity.score_np)
            metrics.activity_score.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code,
                score='A'
            ).set(activity.statisticsactivity.score_a)
            metrics.activity_score.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code,
                score='B'
            ).set(activity.statisticsactivity.score_b)
            metrics.activity_score.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code,
                score='C+'
            ).set(activity.statisticsactivity.score_cp)
            metrics.activity_score.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code,
                score='C-'
            ).set(activity.statisticsactivity.score_cm)
            metrics.activity_score.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code,
                score='D'
            ).set(activity.statisticsactivity.score_d)
            metrics.activity_qualification.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code,
                qualification='NP'
            ).set(activity.statisticsactivity.eval_np)
            metrics.activity_qualification.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code,
                qualification='A'
            ).set(activity.statisticsactivity.eval_a)
            metrics.activity_qualification.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code,
                qualification='B'
            ).set(activity.statisticsactivity.eval_b)
            metrics.activity_qualification.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code,
                qualification='C+'
            ).set(activity.statisticsactivity.eval_cp)
            metrics.activity_qualification.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code,
                qualification='C-'
            ).set(activity.statisticsactivity.eval_cm)
            metrics.activity_qualification.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code,
                qualification='D'
            ).set(activity.statisticsactivity.eval_d)
            metrics.activity_qualification.labels(
                semester=activity.course.semester.code, course=activity.course.code, activity=activity.code,
                qualification='Pending'
            ).set(activity.statisticsactivity.eval_pending)

        except models.StatisticsActivity.DoesNotExist:
            pass

    if settings.PROMETHEUS_METRICS_GW is not None:
        push_to_gateway(settings.PROMETHEUS_METRICS_GW, job='pelp', registry=registry)
