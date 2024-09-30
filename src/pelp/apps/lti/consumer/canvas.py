import lti_toolbox.lti

from typing import Optional
from django.contrib.auth.models import User
from pelp.apps.web import models

from .base import BaseConsumer
from ..models import LTIConsumerProperties, LTIProfile, LTICourse, LTIGroup


class CanvasConsumer(BaseConsumer):

    def __init__(self, properties: LTIConsumerProperties, lti_request: lti_toolbox.lti.LTI):
        super().__init__(properties, lti_request)

    def create_user(self, username: str, email: str) -> User:
        # Get user information
        first_name = self.get_param('lis_person_name_given')
        last_name = self.get_param('lis_person_name_family')

        # Create the user
        return User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

    def create_user_profile(self, user: User):
        profile = LTIProfile.objects.create(
            consumer=self.properties.consumer,
            user=user,
            user_username=user.username,
            ext_user_username=self.request.get_param('custom_canvas_user_login_id'),
            lis_person_name_given=self.request.get_param('lis_person_name_given'),
            lis_person_name_family=self.request.get_param('lis_person_name_family'),
            lis_person_name_full=self.request.get_param('lis_person_name_full'),
            lis_person_contact_email_primary=self.request.get_param('lis_person_contact_email_primary'),
        )
        return profile

    def update_user_profile(self, user: User):
        try:
            profile = LTIProfile.objects.get(consumer=self.properties.consumer, user=user)
        except LTIProfile.DoesNotExist:
            return None

        profile.ext_user_username = self.request.get_param('custom_canvas_user_login_id')
        profile.lis_person_name_given = self.request.get_param('lis_person_name_given')
        profile.lis_person_name_family = self.request.get_param('lis_person_name_family')
        profile.lis_person_name_full = self.request.get_param('lis_person_name_full')
        profile.lis_person_contact_email_primary = self.request.get_param('lis_person_contact_email_primary')
        profile.save()

        return profile

    def create_course_profile(self, course: Optional[models.Course] = None) -> Optional[LTICourse]:
        course_code = self.request.get_param(self.properties.course_code_field)
        if course_code is None:
            return None

        course_profile = LTICourse.objects.create(
            consumer=self.properties.consumer,
            course=course,
            course_code=course_code,
            context_id=self.request.get_param('context_id'),
            context_title=self.request.get_param('context_title'),
            # tool_consumer_instance_name=self.request.get_param('tool_consumer_instance_name'),
            # tool_consumer_instance_description=self.request.get_param('tool_consumer_instance_description'),
        )

        return course_profile

    def update_course_profile(self, course: Optional[models.Course] = None) -> Optional[LTICourse]:
        course_code = self.request.get_param(self.properties.course_code_field)
        if course_code is None:
            return None
        try:
            course_profile = LTICourse.objects.get(consumer=self.properties.consumer, course_code=course_code)

            if course is not None:
                course_profile.course = course
            course_profile.course_code = course_code
            course_profile.context_id = self.request.get_param('context_id')
            course_profile.context_title = self.request.get_param('context_title')
            # course_profile.tool_consumer_instance_name = self.request.get_param('tool_consumer_instance_name')
            # course_profile.tool_consumer_instance_description = self.request.get_param(
            #    'tool_consumer_instance_description'
            # )
            course_profile.save()
        except LTICourse.DoesNotExist:
            return None
        return course_profile

    def create_group_profile(self, group: Optional[models.CourseGroup] = None) -> Optional[LTIGroup]:
        group_code = self.request.get_param(self.properties.group_code_field)
        if group_code is None:
            return None

        group_profile = LTIGroup.objects.create(
            consumer=self.properties.consumer,
            group_code=group_code,
            group=group,
            context_id=self.request.get_param('context_id'),
            context_title=self.request.get_param('context_title'),
            context_label=self.request.get_param('context_label'),
        )

        return group_profile

    def update_group_profile(self, group: Optional[models.CourseGroup] = None) -> Optional[LTIGroup]:
        group_code = self.request.get_param(self.properties.group_code_field)
        if group_code is None:
            return None
        try:
            group_profile = LTIGroup.objects.get(consumer=self.properties.consumer, group_code=group_code)

            if group is not None:
                group_profile.group = group

            group_profile.context_id = self.request.get_param('context_id')
            group_profile.context_title = self.request.get_param('context_title')
            group_profile.context_label = self.request.get_param('context_label')
            group_profile.save()
        except LTIGroup.DoesNotExist:
            return None
        return group_profile
