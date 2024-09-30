import lti_toolbox.lti
import requests

from PIL import Image
from io import BytesIO

from typing import Optional
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from pelp.apps.web import models

from .base import BaseConsumer
from ..models import LTIConsumerProperties, LTIProfile, LTICourse, LTIGroup


class UOCConsumer(BaseConsumer):

    def __init__(self, properties: LTIConsumerProperties, lti_request: lti_toolbox.lti.LTI):
        super().__init__(properties, lti_request)

    def create_user(self, username: str, email: str) -> User:
        # Get user information
        first_name = self.get_param('custom_firstname')
        last_name = self.get_param('custom_surname')

        # Create the user
        return User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

    def create_user_profile(self, user: User) -> LTIProfile:

        picture = None
        if self.get_param('custom_photo'):
            response = requests.get(self.get_param('custom_photo'))
            try:
                picture = Image.open(BytesIO(response.content))
            except Exception:
                picture = None

        profile = LTIProfile.objects.create(
            consumer=self.properties.consumer,
            user=user,
            user_username=user.username,
            custom_photo=self.get_param('custom_photo'),
            custom_firstname=self.get_param('custom_firstname'),
            custom_surname=self.get_param('custom_surname'),
            custom_fullname=self.get_param('custom_fullname'),
            custom_username=self.get_param('custom_username'),
            custom_sessionid=self.get_param('custom_sessionid'),
        )

        usr_profile = models.Profile.objects.create(
            user=user
        )
        usr_profile.save()
        if picture is not None:
            filename = self.get_param('custom_photo').split('/')[-1]
            blob = BytesIO()
            picture.save(blob, 'JPEG')
            usr_profile.picture.save(filename, ContentFile(blob.getvalue()))
        return profile

    def update_user_profile(self, user: User) -> Optional[LTIProfile]:
        try:
            profile = LTIProfile.objects.get(consumer=self.properties.consumer, user=user)
        except LTIProfile.DoesNotExist:
            return None

        picture = None
        if self.get_param('custom_photo'):
            response = requests.get(self.get_param('custom_photo'))
            try:
                picture = Image.open(BytesIO(response.content))
            except Exception:
                picture = None

        profile.custom_photo = self.get_param('custom_photo')
        profile.custom_firstname = self.get_param('custom_firstname')
        profile.custom_surname = self.get_param('custom_surname')
        profile.custom_fullname = self.get_param('custom_fullname')
        profile.custom_username = self.get_param('custom_username')
        profile.custom_sessionid = self.get_param('custom_sessionid')
        profile.save()

        try:
            usr_profile = profile.user.profile
        except models.Profile.DoesNotExist:
            usr_profile = models.Profile.objects.create(
                user = profile.user
            )
        if picture is not None:
            filename = self.get_param('custom_photo').split('/')[-1]
            blob = BytesIO()
            picture.save(blob, 'JPEG')
            usr_profile.picture.save(filename, ContentFile(blob.getvalue()))

        return profile

    def create_course_profile(self, course: Optional[models.Course] = None) -> Optional[LTICourse]:
        course_code = self.get_param(self.properties.course_code_field)
        if course_code is None:
            return None

        course_profile = LTICourse.objects.create(
            consumer=self.properties.consumer,
            course=course,
            course_code=course_code,
            custom_domain_coditercers=self.get_param('custom_domain_coditercers'),
            custom_domain_year=self.get_param('custom_domain_year'),
            custom_domain_semester=self.get_param('custom_domain_semester'),
            custom_domain_pt_template=self.get_param('custom_domain_pt_template'),
            context_id=self.get_param('context_id'),
            context_title=self.get_param('context_title'),
            context_label=self.get_param('context_label'),
        )

        return course_profile

    def update_course_profile(self, course: Optional[models.Course] = None) -> Optional[LTICourse]:
        course_code = self.get_param(self.properties.course_code_field)
        if course_code is None:
            return None
        try:
            course_profile = LTICourse.objects.get(consumer=self.properties.consumer, course_code=course_code)

            if course is not None:
                course_profile.course = course
            course_profile.custom_domain_coditercers=self.get_param('custom_domain_coditercers')
            course_profile.custom_domain_year=self.get_param('custom_domain_year')
            course_profile.custom_domain_semester=self.get_param('custom_domain_semester')
            course_profile.custom_domain_pt_template=self.get_param('custom_domain_pt_template')
            course_profile.context_id=self.get_param('context_id')
            course_profile.context_title=self.get_param('context_title')
            course_profile.context_label=self.get_param('context_label')
            course_profile.save()
        except LTICourse.DoesNotExist:
            return None
        return course_profile

    def create_group_profile(self, group: Optional[models.CourseGroup] = None) -> Optional[LTIGroup]:
        group_code = self.get_param(self.properties.group_code_field)
        if group_code is None:
            return None

        group_profile = LTIGroup.objects.create(
            consumer=self.properties.consumer,
            group_code=group_code,
            group=group,
            context_id=self.get_param('context_id'),
            context_label=self.get_param('context_label'),
        )

        return group_profile

    def update_group_profile(self, group: Optional[models.CourseGroup] = None) -> Optional[LTIGroup]:
        group_code = self.get_param(self.properties.group_code_field)
        if group_code is None:
            return None
        try:
            group_profile = LTIGroup.objects.get(consumer=self.properties.consumer, group_code=group_code)

            if group is not None:
                group_profile.group = group

            group_profile.context_id = self.get_param('context_id')
            group_profile.context_title = self.get_param('context_title')
            group_profile.context_label = self.get_param('context_label')
            group_profile.save()
        except LTIGroup.DoesNotExist:
            return None
        return group_profile
