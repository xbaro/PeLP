from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.db import models

from .project import Project


class ProjectTest(models.Model):
    """ Project Test model. """
    project = models.ForeignKey(Project, null=False, on_delete=models.CASCADE)
    code = models.CharField(max_length=30, null=False, blank=False)
    internal_code = models.CharField(max_length=30, null=True, blank=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    grouping_node = models.BooleanField(null=False, blank=False, default=False)
    parent = models.ForeignKey('ProjectTest', related_name='children', null=True,
                               blank=True, default=None, on_delete=models.CASCADE)
    weight = models.FloatField(null=False, blank=False, default=1.0)

    class Meta:
        unique_together = ['project', 'code']

    def __str__(self):
        return "[{} - {} - {}] {}".format(self.project.activity.course.semester, self.project.activity.course.code,
                                          self.project.activity.code, self.code)

@receiver(post_save, sender=ProjectTest)
def _projectTest_post_save(sender, instance, *args, **kwargs):
    # if kwargs[]
    try:
        from pelp.apps.web.consumers.activity import ActivityEventConsumer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            ActivityEventConsumer.get_activity_channel_name(instance.project.activity.id),
            {
                'type': 'send_message',
                'message': instance.project.get_total_weight(),
                "event": 'WEIGHT_CHANGE'
        })
    except Exception:
        # Avoid failing due to messging error
        pass
