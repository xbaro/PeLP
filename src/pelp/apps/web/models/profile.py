from django.db import models
from django.contrib.auth.models import User


def get_picture_upload_path(instance, filename):
    """
        Build the path where the user picture is stored

        :param instance: Profile instance
        :type instance: Profile
        :param filename: Name of the file
        :return: Path to store the file
    """
    return 'profiles/pictures/{}.jpeg'.format(
        instance.user.username.replace(' ', '_')
    )


class Profile(models.Model):
    """ Profile model. """
    picture = models.ImageField(null=True, blank=True, upload_to=get_picture_upload_path)
    user = models.OneToOneField(User, null=True, blank=True, default=None, on_delete=models.CASCADE)
