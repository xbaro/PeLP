""" Module implementing submission management features """
from typing import List, Union, Optional, Literal
from django.db.models import Value, Count, Avg, F, Sum
from pelp.apps.web import models

from . import utils


def get_activity_score_group_summary(activity: models.Activity) -> list:
    return utils.get_activity_score_group_summary(activity)


def get_activity_qualification_group_summary(activity: models.Activity) -> list:
    return utils.get_activity_qualification_group_summary(activity)


def get_activity_score_summary(activity: models.Activity) -> list:
    return utils.get_activity_score_summary(activity)


def get_activity_qualification_summary(activity: models.Activity) -> list:
    return utils.get_activity_qualification_summary(activity)

def _initialize_values(stats_object: Union[models.StatisticsGroup, models.StatisticsActivity]):
    stats_object.score_a = 0
    stats_object.score_b = 0
    stats_object.score_cp = 0
    stats_object.score_cm = 0
    stats_object.score_d = 0
    stats_object.score_np = 0
    stats_object.eval_a = 0
    stats_object.eval_b = 0
    stats_object.eval_cp = 0
    stats_object.eval_cm = 0
    stats_object.eval_d = 0
    stats_object.eval_np = 0
    stats_object.eval_pending = 0

    return stats_object

def _set_score_values(stats_object: Union[models.StatisticsGroup, models.StatisticsActivity],
                      values: dict):
    stats_object.score_a = values['A']
    stats_object.score_b = values['B']
    stats_object.score_cp = values['C+']
    stats_object.score_cm = values['C-']
    stats_object.score_d = values['D']
    stats_object.score_np = values['NP']

    return stats_object

def _set_eval_values(stats_object: Union[models.StatisticsGroup, models.StatisticsActivity],
                      values: dict):
    stats_object.eval_a = values['A']
    stats_object.eval_b = values['B']
    stats_object.eval_cp = values['C+']
    stats_object.eval_cm = values['C-']
    stats_object.eval_d = values['D']
    stats_object.eval_np = values['NP']
    stats_object.eval_pending = values['Pending']

    return stats_object


def update_activity_statistics(activity: models.Activity):

    stats = utils.get_activity_statistics(activity)

    try:
        act_stats = models.StatisticsActivity.objects.get(activity=activity)
    except models.StatisticsActivity.DoesNotExist:
        act_stats = models.StatisticsActivity.objects.create(
            activity=activity,
            learners=activity.course.learners.count()
        )

    act_stats.learners = activity.course.learners.count()
    act_stats.learners_with_submissions = activity.course.learners.filter(
        learnerresult__activity=activity
    ).distinct().count()
    num_submissions_learner = activity.course.learners.filter(
        learnerresult__activity=activity).distinct().aggregate(
        avg=Avg('learnerresult__num_submissions'),
        total=Sum('learnerresult__num_submissions')
    )
    act_stats.mean_submissions_learner = num_submissions_learner['avg'] or 0.0
    act_stats.total_submissions = num_submissions_learner['total'] or 0
    act_stats.has_evaluation = not activity.self_evaluation
    _initialize_values(act_stats)
    act_stats = _set_score_values(act_stats, stats['global']['score'])
    if act_stats.has_evaluation:
        act_stats = _set_eval_values(act_stats, stats['global']['qualification'])
    act_stats.save()

    for group in activity.course.coursegroup_set.all():
        try:
            group_stats = models.StatisticsGroup.objects.get(activity=activity, group=group)
        except models.StatisticsGroup.DoesNotExist:
            group_stats = models.StatisticsGroup.objects.create(
                activity=activity,
                group=group,
                learners=0
            )
        group_stats.locale = group.locale
        group_stats.learners = group.num_learners
        group_stats.learners_with_submissions = group.learner_set.filter(
            learnerresult__activity=activity
        ).distinct().count()
        num_submissions_learner = group.learner_set.filter(
            learnerresult__activity=activity).distinct().aggregate(
            avg=Avg('learnerresult__num_submissions'),
            total=Sum('learnerresult__num_submissions')
        )
        group_stats.mean_submissions_learner = num_submissions_learner['avg'] or 0.0
        group_stats.total_submissions = num_submissions_learner['total'] or 0
        group_stats.instructors = ', '.join(
            [instructor.user.get_full_name() for instructor in group.instructor_set.all()]
        )
        group_stats.has_evaluation = not activity.self_evaluation
        _initialize_values(group_stats)
        if group.id in stats['groups']:
            group_stats = _set_score_values(group_stats, stats['groups'][group.id]['score'])
            if group_stats.has_evaluation:
                group_stats = _set_eval_values(group_stats, stats['groups'][group.id]['qualification'])
        group_stats.save()
