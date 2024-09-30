from django.contrib import admin

from .models import Activity
from .models import Course
from .models import CourseGroup
from .models import CourseTemplate
from .models import CourseTemplateLanguage
from .models import GitRepository
from .models import HistoricActivity
from .models import ImportSession
from .models import Instructor
from .models import Learner
from .models import Project
from .models import ProjectModule
from .models import Semester
from .models import MailInbox
from .models import Rubric
from .models import RubricElement
from .models import RubricElementOption
from .models import TranslateCourse
from .models import TranslateRubricElement
from .models import TranslateRubricElementOption
from .models import FaqTag
from .models import TranslateFaqTag


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('code', 'start', 'end')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'semester', 'description')

@admin.register(CourseGroup)
class CourseGroupAdmin(admin.ModelAdmin):
    list_display = ('code', 'course')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('code', 'course', 'name', 'start', 'end')


@admin.register(GitRepository)
class GitRepositoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_url')


@admin.register(ImportSession)
class ImportSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'created_at', 'course_group')
    exclude = ('created_at', 'error',)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')

@admin.register(Learner)
class LearnerAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('status', 'activity', 'executable_name')
    exclude = ('error', 'code_test_result', 'code_base_result')

    def clean_repository(self):
        if self.cleaned_data["repository"]:
            return None
        return self.cleaned_data["name"]


@admin.register(ProjectModule)
class ProjectModuleAdmin(admin.ModelAdmin):
    list_display = ('project', 'name')


@admin.register(MailInbox)
class MailInboxAdmin(admin.ModelAdmin):
    list_display = ('name', 'activity')


@admin.register(Rubric)
class RubricAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')


@admin.register(RubricElement)
class RubricElementAdmin(admin.ModelAdmin):
    list_display = ('rubric', 'type', 'description', 'weight')


@admin.register(RubricElementOption)
class RubricElementOptionAdmin(admin.ModelAdmin):
    list_display = ('rubric_element', 'value', 'description')


@admin.register(TranslateCourse)
class TranslateCourseAdmin(admin.ModelAdmin):
    list_display = ('language', 'name', 'description')


@admin.register(TranslateRubricElement)
class TranslateRubricElementAdmin(admin.ModelAdmin):
    list_display = ('language', 'description')


@admin.register(TranslateRubricElementOption)
class TranslateRubricElementOptionAdmin(admin.ModelAdmin):
    list_display = ('language', 'description')


@admin.register(HistoricActivity)
class HistoricActivityAdmin(admin.ModelAdmin):
    list_display = ('code', )


@admin.register(FaqTag)
class FaqTagAdmin(admin.ModelAdmin):
    list_display = ('tag', )


@admin.register(TranslateFaqTag)
class TranslateFaqTagAdmin(admin.ModelAdmin):
    list_display = ('faqtag', 'tag', )


@admin.register(CourseTemplate)
class CourseTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'description' )


@admin.register(CourseTemplateLanguage)
class CourseTemplateLanguageAdmin(admin.ModelAdmin):
    list_display = ('template_id', 'code', 'language', 'name', 'is_lab')
