import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from pelp.apps.web import models


class ActivityEventConsumer(JsonWebsocketConsumer):

    @classmethod
    def get_activity_channel_name(cls, activity_id):
        return 'activity_%06d' % int(activity_id)

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

        if user.is_staff or activity.course.is_instructor(user):
            self.room_group_name = self.get_activity_channel_name(self.activity_id)

            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            self.accept()

            self.send(text_data=json.dumps({
                'event': 'INITIAL_STATUS',
                'message': activity.project.get_status_display()
            }))
            self.send(text_data=json.dumps({
                'event': 'INITIAL_WEIGHT',
                'message': activity.project.get_total_weight()
            }))
        else:
            self.close()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        response = json.loads(text_data)
        event = response.get("event", None)

        user = self.scope.get('user')
        if user is None or not user.is_authenticated :
            self.send(text_data=json.dumps({
                'event': 'ERROR',
                'message': 'Invalid user'
            }))
            self.close()
            return

        try:
            activity = models.Activity.objects.get(id=self.activity_id)
        except models.Activity.DoesNotExist:
            self.send(text_data=json.dumps({
                'event': 'ERROR',
                'message': 'Invalid activity'
            }))
            self.close()
            return

        if not user.is_staff and not activity.course.is_instructor(user):
            self.send(text_data=json.dumps({
                'event': 'ERROR',
                'message': 'Not allowed'
            }))
            self.close()
            return

        if event == 'VALIDATE_PROJECT':
            activity.project.status = 1
            activity.project.save()
        elif event == 'TEST_PROJECT':
            activity.project.status = 7
            activity.project.save()

    def send_message(self, res):
        """ Receive message from room group """
        # Send message to WebSocket
        self.send(text_data=json.dumps(res))
