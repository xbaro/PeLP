from bs4 import BeautifulSoup
from django.db.models import Sum, Count, Avg, Value, Q, F
from django.db.models.functions import TruncTime, TruncDate, TruncHour
from django.utils.translation import get_language, gettext as _
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from pelp.apps.web import models
from pelp.apps.web.models.utils import JSONField
from pelp.apps.web import lib


class ProfileSerializer(serializers.ModelSerializer):

    tokens = serializers.SerializerMethodField()
    username = serializers.CharField(read_only=True, source="user.username")
    first_name = serializers.CharField(read_only=True, source="user.first_name")
    last_name = serializers.CharField(read_only=True, source="user.last_name")
    email = serializers.CharField(read_only=True, source="user.email")
    class Meta:
        model = models.Profile
        fields = '__all__'

    def get_tokens(self, instance):
        tokens = RefreshToken.for_user(instance.user)
        return {"access": tokens.access_token.__str__(), "refresh": tokens.__str__()}


class SemesterSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Semester
        fields = '__all__'


class LearnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Learner
        fields = '__all__'


class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instructor
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = '__all__'


class ProjectModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectModule
        fields = '__all__'


class ProjectExtendedSerializer(serializers.ModelSerializer):
    modules = ProjectModuleSerializer(many=True, source='projectmodule_set')

    class Meta:
        model = models.Project
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Activity
        fields = '__all__'

    def validate(self, attrs):
        errors = {}
        year_built = attrs.get('year_built')
        year_rennovated = attrs.get('year_rennovated')

        if year_rennovated < year_built:
            errors['error'] = 'Invalid data TODO'
            raise serializers.ValidationError(errors)

        return attrs


class CourseSerializer(serializers.ModelSerializer):

    semester = SemesterSerializer(many=False)

    class Meta:
        model = models.Course
        fields = '__all__'


class CourseGroupSerializer(serializers.ModelSerializer):

    course = CourseSerializer(many=False)

    class Meta:
        model = models.CourseGroup
        fields = '__all__'


class ProjectFileSerializer(serializers.ModelSerializer):

    module = ProjectModuleSerializer(many=False)

    class Meta:
        model = models.ProjectFile
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    result = JSONField()
    is_mail_submission = serializers.BooleanField(read_only=True)
    is_instructor_submission = serializers.BooleanField(read_only=True)
    submitted_by = serializers.CharField(read_only=True)

    class Meta:
        model = models.Submission
        fields = '__all__'


class ProjectSubmissionSerializer(serializers.ModelSerializer):
    is_project_validation = serializers.SerializerMethodField()
    is_project_test = serializers.SerializerMethodField()
    is_test = serializers.BooleanField(read_only=True)

    class Meta:
        model = models.Submission
        fields = '__all__'

    @staticmethod
    def get_is_project_validation(instance):
        if instance.is_test:
            return instance.testsubmission.source == 0
        return False

    @staticmethod
    def get_is_project_test(instance):
        if instance.is_test:
            return instance.testsubmission.source == 1
        return False


class MySubmissionSerializer(serializers.ModelSerializer):
    result = JSONField()
    is_mail_submission = serializers.BooleanField(read_only=True)
    is_instructor_submission = serializers.BooleanField(read_only=True)
    submitted_by = serializers.CharField(read_only=True)
    status_desc = serializers.CharField(source='get_status_display')

    class Meta:
        model = models.Submission
        fields = '__all__'


class SubmissionFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SubmissionFile
        fields = '__all__'


class SubmissionErrorSerializer(serializers.ModelSerializer):

    file = SubmissionFileSerializer(many=False, read_only=True, required=False)

    class Meta:
        model = models.SubmissionError
        fields = '__all__'


class LearnerSubmissionSerializer(serializers.ModelSerializer):

    submissions = SubmissionSerializer(many=True)

    class Meta:
        model = models.Learner
        fields = '__all__'


class ProjectTestParentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectTest
        fields = '__all__'


class ProjectTestSerializer4(serializers.ModelSerializer):

    class Meta:
        model = models.ProjectTest
        fields = '__all__'


class ProjectTestSerializer3(serializers.ModelSerializer):
    children = ProjectTestSerializer4(many=True)

    class Meta:
        model = models.ProjectTest
        fields = '__all__'


class ProjectTestSerializer2(serializers.ModelSerializer):

    children = ProjectTestSerializer3(many=True)

    class Meta:
        model = models.ProjectTest
        fields = '__all__'


class ProjectTestSerializer(serializers.ModelSerializer):

    children = ProjectTestSerializer2(many=True)
    parent = ProjectTestParentSerializer(many=False)

    class Meta:
        model = models.ProjectTest
        fields = '__all__'


class SubmissionTestResultSerializer(serializers.ModelSerializer):

    test = ProjectTestSerializer(many=False)

    class Meta:
        model = models.SubmissionTestResult
        fields = '__all__'


class LearnerResultSerializer(serializers.ModelSerializer):

    status_desc = serializers.CharField(source='get_status_display', read_only=True)
    last_submission = SubmissionSerializer(many=False)
    learner = LearnerSerializer(many=False)
    submissions = serializers.SerializerMethodField()

    class Meta:
        model = models.LearnerResult
        fields = '__all__'

    def get_submissions(self, instance):
        return SubmissionSerializer(instance.learner.submission_set.filter(
            activity_id=instance.activity_id
        ).order_by('-submitted_at', '-id'), many=True).data

    def get_results_detail(self, instance):

        if instance.last_submission is None or instance.last_submission.status != 8:
            return None

        return SubmissionTestResultSerializer(
            instance.last_submission.submissiontestresult_set.order_by('test__code').all(),
            many=True
        ).data


class LearnerCourseActivitySubmissionSerializer(serializers.ModelSerializer):
    last_submission = serializers.SerializerMethodField()
    num_submissions = serializers.SerializerMethodField()
    submissions = serializers.SerializerMethodField()
    results_detail = serializers.SerializerMethodField()
    result_summary = serializers.SerializerMethodField()

    class Meta:
        model = models.Learner
        fields = '__all__'

    @property
    def activity_id(self):
        return self.context['request'].parser_context['kwargs']['parent_lookup_activity_id']

    def get_submissions(self, instance):
        return SubmissionSerializer(instance.submission_set.filter(
            activity_id=self.activity_id
        ).order_by('-submitted_at'), many=True).data

    def get_last_submission(self, instance):
        try:
            last_submission = instance.submission_set.filter(
                activity_id=self.activity_id,
                is_last=True).get()
            return SubmissionSerializer(last_submission, many=False).data
        except models.Submission.DoesNotExist:
            return None

    def get_num_submissions(self, instance):
        return instance.submission_set.filter(activity_id=self.activity_id).count()

    def get_results_detail(self, instance):
        last_submission = instance.submission_set.filter(
            activity_id=self.activity_id
        ).order_by('-submitted_at', '-id').first()
        if last_submission is None or last_submission.status != 8:
            return None

        return SubmissionTestResultSerializer(
            last_submission.submissiontestresult_set.order_by('test__code').all(),
            many=True
        ).data

    def get_result_summary(self, instance):
        try:
            learner_result = instance.learnerresult_set.filter(
                activity_id=self.activity_id
            ).get()
            return LearnerResultSerializer(learner_result, many=False).data
        except models.LearnerResult.DoesNotExist:
            return None


class ActivityFeedbackSerializer(serializers.ModelSerializer):

    txt_summary = serializers.SerializerMethodField()
    html_summary = serializers.SerializerMethodField()

    class Meta:
        model = models.ActivityFeedback
        fields = '__all__'

    def get_txt_summary(self, instance):
        rubric_elements = instance.activity.rubricelementinstantiation_set.filter(learner=instance.learner)

        el_summary = []

        for element in rubric_elements.all().order_by('rubric_element_id'):
            el_txt = '- {}: {}'.format(
                element.rubric_element.get_translated_description(get_language()),
                element.value.get_translated_description(get_language())
            )
            el_summary.append(el_txt)

        if len(el_summary) == 0 and instance.general is None:
            return None

        summary = []
        if len(el_summary) > 0:
            summary.append(_('General Aspects') + '\n\n' + '\n'.join(el_summary))

        if instance.general is not None:
            if len(summary) > 0:
                summary.append('\n')
            summary.append(_('Observations') + '\n\n' + BeautifulSoup(instance.general).get_text())

        return '\n'.join(summary)

    def get_html_summary(self, instance):
        rubric_elements = instance.activity.rubricelementinstantiation_set.filter(learner=instance.learner)

        el_summary = []

        for element in rubric_elements.all().order_by('rubric_element_id'):
            el_summary.append('<div class="feedback rubric-element-title"><strong>{}</strong></div>'.format(
                element.rubric_element.get_translated_description(get_language()),
            ))
            el_summary.append('<ul><li class="feedback rubric-element-option">{}</li></ul>'.format(
                element.value.get_translated_description(get_language())
            ))

        if len(el_summary) == 0 and instance.general is None:
            return None

        summary = ['<div class="feedback">']
        if len(el_summary) > 0:
            summary.append('<div class="feedback general-aspects-title h2">' + _('General Aspects') + '</div>')
            summary += el_summary

        if instance.general is not None:
            summary.append('<div class="feedback observations-title h2">' + _('Observations') + '</div>')
            summary.append('<div class="feedback observations">' + instance.general + '</div>')
        summary.append('</div>')

        return '\n'.join(summary)


class LearnerCourseActivityFeedbackSerializer(serializers.ModelSerializer):
    feedback = serializers.SerializerMethodField()

    class Meta:
        model = models.Learner
        fields = '__all__'

    @property
    def activity_id(self):
        return self.context['request'].parser_context['kwargs']['parent_lookup_activity_id']

    def get_feedback(self, instance):
        try:
            return ActivityFeedbackSerializer(instance.activityfeedback_set.filter(
                activity_id=self.activity_id
            ).get(), many=False).data
        except models.ActivityFeedback.DoesNotExist:
            return None


class ImportSessionSerializer(serializers.ModelSerializer):

    course_group = CourseGroupSerializer(many=False)
    activity = ActivitySerializer(many=False)

    class Meta:
        model = models.ImportSession
        fields = '__all__'


class ImportSessionEntrySerializer(serializers.ModelSerializer):

    data = JSONField()

    class Meta:
        model = models.ImportSessionEntry
        fields = '__all__'


class FilePathBodySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SubmissionFile
        fields = '__all__'


class TestResultSerializer(serializers.Serializer):
    code = serializers.CharField(source='test__code')
    count = serializers.IntegerField(source='total')
    passed = serializers.FloatField(source='average')


class TestScoreSerializer(serializers.Serializer):
    score = serializers.FloatField(source='test_score')
    count = serializers.IntegerField()


class SubmissionResultSerializer(serializers.Serializer):
    built = serializers.FloatField()
    correct_execution = serializers.FloatField()
    tests_passed = serializers.FloatField()


class SubmissionByDaySerializer(serializers.Serializer):
    day = serializers.DateField()
    count = serializers.IntegerField()


class SubmissionByTimeSerializer(serializers.Serializer):
    time = serializers.TimeField(format='%H:%M')
    count = serializers.IntegerField()


class QualificationByGroupSerializer(serializers.Serializer):
    groups = CourseGroupSerializer(many=False)
    qualification = serializers.CharField()
    count = serializers.IntegerField()


class ActivityStatisticsSerializer(serializers.Serializer):
    num_submissions = serializers.SerializerMethodField()
    submissions_waiting = serializers.SerializerMethodField()
    submissions_running = serializers.SerializerMethodField()
    submissions_processed = serializers.SerializerMethodField()
    submissions_error = serializers.SerializerMethodField()
    submissions_invalid = serializers.SerializerMethodField()
    submissions_timeout = serializers.SerializerMethodField()
    results = serializers.SerializerMethodField()
    final_status = serializers.SerializerMethodField()
    scores = serializers.SerializerMethodField()
    submissions_date = serializers.SerializerMethodField()
    submissions_time = serializers.SerializerMethodField()
    qualification_summary = serializers.SerializerMethodField()
    score_summary = serializers.SerializerMethodField()

    @staticmethod
    def get_num_submissions(instance):
        stats = {}
        for activity in instance:
            stats[activity.code] = activity.submission_set.filter(learner_id__gte=0).count()
        return stats

    @staticmethod
    def get_submissions_waiting(instance):
        stats = {}
        for activity in instance:
            stats[activity.code] = activity.submission_set.filter(status__lte=6, learner_id__gte=0).count()
        return stats

    @staticmethod
    def get_submissions_running(instance):
        stats = {}
        for activity in instance:
            stats[activity.code] = activity.submission_set.filter(status=7, learner_id__gte=0).count()
        return stats

    @staticmethod
    def get_submissions_processed(instance):
        stats = {}
        for activity in instance:
            stats[activity.code] = activity.submission_set.filter(status=8, learner_id__gte=0).count()
        return stats

    @staticmethod
    def get_submissions_error(instance):
        stats = {}
        for activity in instance:
            stats[activity.code] = activity.submission_set.filter(status=10, learner_id__gte=0).count()
        return stats

    @staticmethod
    def get_submissions_invalid(instance):
        stats = {}
        for activity in instance:
            stats[activity.code] = activity.submission_set.filter(status=9, learner_id__gte=0).count()
        return stats

    @staticmethod
    def get_submissions_timeout(instance):
        stats = {}
        for activity in instance:
            stats[activity.code] = activity.submission_set.filter(status=11, learner_id__gte=0).count()
        return stats

    @staticmethod
    def get_results(instance):
        stats = {}
        for activity in instance:
            results = models.SubmissionTestResult.objects.filter(
                submission__activity=activity,
                submission__is_last=True,
                test__grouping_node=False,
                submission__learner_id__gte=0
            ).values('test__code').annotate(
                total=Sum('passed'), average=Avg('passed')
            ).order_by('test__code')
            stats[activity.code] = TestResultSerializer(results, many=True).data
        return stats

    @staticmethod
    def get_final_status(instance):
        stats = {}
        for activity in instance:
            results = models.Submission.objects.filter(
                activity=activity,
                is_last=True,
                learner_id__gte=0
            ).aggregate(built=Avg('built'), correct_execution=Avg('correct_execution'), tests_passed=Avg('test_passed'))
            stats[activity.code] = SubmissionResultSerializer(results, many=False).data
        return stats

    @staticmethod
    def get_scores(instance):
        stats = {}
        for activity in instance:
            results = models.Submission.objects.filter(
                activity=activity,
                is_last=True,
                learner_id__gte=0
            ).values('test_score').annotate(count=Count('test_score')).order_by('test_score')
            stats[activity.code] = TestScoreSerializer(results, many=True).data
        return stats

    @staticmethod
    def get_submissions_date(instance):
        stats = {}
        for activity in instance:
            results = models.Submission.objects.filter(
                activity=activity,
                learner_id__gte=0
            ).annotate(day=TruncDate('submitted_at')).values('day').annotate(count=Count('day')).order_by('day')
            stats[activity.code] = SubmissionByDaySerializer(results, many=True).data
        return stats

    @staticmethod
    def get_submissions_time(instance):
        stats = {}
        for activity in instance:
            results = models.Submission.objects.filter(
                activity=activity,
                learner_id__gte=0
            ).annotate(
                time=TruncTime(TruncHour('submitted_at'))
            ).values('time').annotate(count=Count('time')).order_by('time')
            stats[activity.code] = SubmissionByTimeSerializer(results, many=True).data
        return stats

    @staticmethod
    def get_qualification_summary(instance):
        stats = {}
        for activity in instance:
            stats[activity.code] = {
                'active': activity.is_active,
                'self_evaluation': activity.self_evaluation,
                'data': lib.statistics.get_activity_qualification_group_summary(activity)
            }
        return stats

    @staticmethod
    def get_score_summary(instance):
        stats = {}
        for activity in instance:
            stats[activity.code] = {
                'active': activity.is_active,
                'self_evaluation': activity.self_evaluation,
                'data': lib.statistics.get_activity_score_group_summary(activity)
            }
            stats2 = lib.statistics.get_activity_qualification_summary(activity)
        return stats


class FaqSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Faq
        fields = '__all__'


class FaqRateSerializer(serializers.Serializer):
    rate = serializers.IntegerField(allow_null=False, min_value=0, max_value=5)
