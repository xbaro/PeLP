from django.contrib import admin

from .models import LTIConsumerProperties
from .models import LTICourse
from .models import LTIGroup
from .models import LTIProfile


@admin.register(LTIConsumerProperties)
class LTIConsumerPropertiesAdmin(admin.ModelAdmin):
    list_display = ('consumer', )


@admin.register(LTICourse)
class LTICourseAdmin(admin.ModelAdmin):
    list_display = ('consumer', 'course_code', 'course')


@admin.register(LTIGroup)
class LTIGroupAdmin(admin.ModelAdmin):
    list_display = ('consumer', 'group_code', 'group')


@admin.register(LTIProfile)
class LTIProfileAdmin(admin.ModelAdmin):
    list_display = ('consumer', 'consumer', 'user', 'user_username')
