import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from pelp.apps.web import models


class SubmissionEventConsumer(JsonWebsocketConsumer):

    @classmethod
    def get_activity_submissions_channel_name(cls, activity_id, user):
        return 'activity_%06d__user_%06d' % (int(activity_id), int(user.id))

    def connect(self):
        self.activity_id = self.scope['url_route']['kwargs'].get('activity_id', None)

        user = self.scope.get('user')
        if user is None or not user.is_authenticated:
            self.close()
            return

        if self.activity_id is None:
            self.close()
            return

        try:
            activity = models.Activity.objects.get(id=self.activity_id)
        except models.Activity.DoesNotExist:
            self.close()
            return

        if user.is_staff or activity.course.is_instructor(user) or activity.course.is_learner(user):
            self.room_group_name = self.get_activity_submissions_channel_name(self.activity_id, user)

            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            self.accept()
        else:
            self.close()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def send_message(self, res):
        """ Receive message from room group """
        # Send message to WebSocket
        self.send(text_data=json.dumps(res))
