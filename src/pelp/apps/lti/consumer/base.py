import abc
import lti_toolbox.lti
import base64

from typing import Optional
from lti_toolbox.models import LTIPassport
from typing import Any
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from sentry_sdk import capture_message
from pelp.apps.web import models

from ..models import LTIConsumerProperties, LTIProfile, LTICourse, LTIGroup


class BaseConsumer():

    utf8_encoded = False
    base64_encoded = False

    def __init__(self, properties: LTIConsumerProperties, lti_request: lti_toolbox.lti.LTI):
        if not lti_request.is_valid:
            raise PermissionDenied()

        if lti_request.get_param('custom_lti_message_encoded_utf8') == '1':
            self.utf8_encoded = True
        if lti_request.get_param('custom_lti_message_encoded_base64') == '1':
            self.base64_encoded = True

        self.properties = properties
        self.request = lti_request

    def get_param(self, key, default=None):
        value = self.request.get_param(key, default)
        if value is not None and self.base64_encoded:
            try:
                value = base64.b64decode(value)
                if self.utf8_encoded:
                    value = value.decode('utf-8')
                else:
                    value = value.decode()
            except Exception:
                # If this field is not base64 encoded, just left it
                capture_message('Error decoding Base64: {}={}'.format(key, value))

        return value


    @staticmethod
    def get_consumer_properties(lti_request: lti_toolbox.lti.LTI) -> LTIConsumerProperties:
        # Get the consumer
        consumer_key = lti_request.get_param("oauth_consumer_key")
        if consumer_key is None:
            capture_message('Missing consumer key')
            raise PermissionDenied('Missing consumer key')
        try:
            consumer = LTIPassport.objects.get(oauth_consumer_key=consumer_key)
        except LTIPassport.DoesNotExist:
            capture_message('Invalid consumer key')
            raise PermissionDenied('Invalid consumer key')

        # Get consumer properties
        try:
            consumer_properties = LTIConsumerProperties.objects.get(consumer=consumer.consumer)
        except LTIConsumerProperties.DoesNotExist:
            if lti_request.get_param('tool_consumer_instance_description') == 'UOC':
                source = 0
                user_username_field = 'custom_username'
                course_code_field = 'custom_domain_pt_template'
                group_code_field = 'custom_domain_code'
            elif lti_request.get_param('tool_consumer_info_product_family_code') == 'moodle':
                source = 1
                user_username_field = 'ext_user_username'
                course_code_field = 'context_id'
                group_code_field = 'context_id'
            elif lti_request.get_param('tool_consumer_info_product_family_code') == 'canvas':
                source = 2
                user_username_field = 'custom_canvas_user_login_id'
                course_code_field = 'lis_course_offering_sourcedid'
                group_code_field = 'lis_course_offering_sourcedid'
            else:
                raise PermissionDenied("Cannot detect consumer type")

            consumer_properties = LTIConsumerProperties.objects.create(
                consumer=consumer.consumer,
                source=source,
                user_creation=False,
                instructor_creation=False,
                learner_creation=False,
                course_creation=False,
                group_creation=False,
                user_username_field=user_username_field,
                course_code_field=course_code_field,
                group_code_field=group_code_field,
            )
        return consumer_properties

    def get_user(self):
        # Get the user
        email = self.get_param("lis_person_contact_email_primary")
        username = self.get_param(self.properties.user_username_field)
        if email is None or username is None:
            capture_message('Missing user information')
            raise PermissionDenied('Missing user information')
        try:
            user = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            if self.properties.user_creation is False:
                capture_message('User not found')
                raise PermissionDenied('User not found')
            # Create a new user
            user = self.create_user(username, email)

        # Try to update the user LTI profile
        user_profile = self.update_user_profile(user)
        if user_profile is None:
            user_profile = self.create_user_profile(user)
        if user_profile is None:
            PermissionDenied('Cannot create user LTI profile')

        # Get the course
        course_profile = self.get_course_profile()
        if course_profile is None:
            course_profile = self.create_course_profile()
        if course_profile.course is None:
            # TODO: Try to create the course
            course = None

        # Get the group
        group_profile = self.get_group_profile()
        if group_profile is None:
            group_profile = self.create_group_profile()
        if group_profile.group is None:
            # TODO: Try to create the group
            group = None

        # Add corresponding object to learners or instructors depending on role
        if 'Instructor' in self.request.roles:
            try:
                instructor = models.Instructor.objects.get(user=user)
            except models.Instructor.DoesNotExist:
                try:
                    instructor = models.Instructor.objects.get(username=user.username)
                    instructor.user = user
                    instructor.save()
                except models.Instructor.DoesNotExist:
                    instructor = None
                    if self.properties.instructor_creation:
                        instructor = models.Instructor.objects.create(
                            user=user,
                            username=username,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            email=email
                        )
            if instructor is not None and group_profile.group is not None:
                instructor.groups.add(group_profile.group)
        else:
            try:
                learner = models.Learner.objects.get(user=user)
            except models.Learner.DoesNotExist:
                try:
                    learner = models.Learner.objects.get(username=user.username)
                    learner.user = user
                    learner.save()
                except models.Learner.DoesNotExist:
                    learner = None
                    if self.properties.learner_creation:
                        learner = models.Learner.objects.create(
                            user=user,
                            username=username,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            email=email
                        )
            if learner is not None and group_profile.group is not None:
                learner.groups.add(group_profile.group)

        return user

    @abc.abstractmethod
    def create_user(self, username: str, email: str) -> User:
        raise NotImplementedError()

    def get_user_profile(self, user: User) -> Optional[LTIProfile]:
        try:
            return LTIProfile.objects.get(consumer=self.properties.consumer, user=user)
        except LTIProfile.DoesNotExist:
            return None

    @abc.abstractmethod
    def create_user_profile(self, user: User) -> Optional[LTIProfile]:
        raise NotImplementedError()

    @abc.abstractmethod
    def update_user_profile(self, user: User) -> Optional[LTIProfile]:
        raise NotImplementedError()

    def get_course_profile(self) -> Optional[LTICourse]:
        course_code = self.get_param(self.properties.course_code_field)
        if course_code is None:
            return None
        try:
            course_profile = LTICourse.objects.get(consumer=self.properties.consumer, course_code=course_code)
        except LTICourse.DoesNotExist:
            return None

        return course_profile

    @abc.abstractmethod
    def create_course_profile(self, course: Optional[models.Course] = None) -> Optional[LTICourse]:
        raise NotImplementedError()

    @abc.abstractmethod
    def update_course_profile(self, course: Optional[models.Course] = None) -> Optional[LTICourse]:
        raise NotImplementedError()

    def get_group_profile(self) -> Optional[LTIGroup]:
        group_code = self.get_param(self.properties.group_code_field)
        if group_code is None:
            return None
        try:
            return LTIGroup.objects.get(consumer=self.properties.consumer, group_code=group_code)
        except LTIGroup.DoesNotExist:
            return None

    @abc.abstractmethod
    def create_group_profile(self, group: Optional[models.CourseGroup] = None) -> Optional[LTIGroup]:
        raise NotImplementedError()

    @abc.abstractmethod
    def update_group_profile(self, group: Optional[models.CourseGroup] = None) -> Optional[LTIGroup]:
        raise NotImplementedError()

