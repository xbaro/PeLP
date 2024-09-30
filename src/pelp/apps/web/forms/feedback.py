"""
    Feedback form definition for PeLP application
"""
from django.forms import ModelForm, HiddenInput, CharField, IntegerField, widgets
from django.utils.translation import get_language, gettext as _
from ckeditor.widgets import CKEditorWidget
from .. import models


class FeedbackForm(ModelForm):
    """
        Form used to provide feedback
    """
    general = CharField(widget=CKEditorWidget(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        activity = None
        if self.instance is not None:
            try:
                activity = self.instance.activity
            except models.Activity.DoesNotExist:
                activity = None

        if activity is not None and activity.rubric is not None:
            # Add parent rubrics elements
            for element in activity.rubric.get_elements_recursive():
                self._add_rubric_element(activity, element)

    class Meta:
        model = models.ActivityFeedback
        fields = ("general", "score", "activity", "learner", "public", "is_np")
        widgets = {
            'activity': HiddenInput(),
            'learner': HiddenInput()
        }

    def clean_general(self):
        data = self.cleaned_data['general']
        if len(data.strip()) == 0:
            data = None
        return data

    def get_rubric_fields(self):
        for field_name in self.fields:
            if field_name.startswith('rubric_element_'):
                yield self[field_name]

    def clean(self):
        rubric_element_instances = []
        for field_name in self.cleaned_data:
            if field_name.startswith('rubric_element_'):
                rubric_element_id = int(field_name[len('rubric_element_'):])
                rubric_element_value_id = self.cleaned_data[field_name]
                if rubric_element_value_id >= 0:
                    rubric_element_instances.append(
                        {
                            'rubric_element_id': rubric_element_id,
                            'rubric_element_value_id': rubric_element_value_id
                        }
                    )
        self.cleaned_data['rubric_elements'] = rubric_element_instances
        if self.cleaned_data['is_np']:
            self.cleaned_data['score'] = None

    def save(self, commit=True):
        new_obj = super().save(commit)

        for rubric_value in self.cleaned_data['rubric_elements']:
            try:
                inst_val = models.RubricElementInstantiation.objects.get(activity=new_obj.activity,
                                                                         learner=new_obj.learner,
                                                                         rubric_element_id=rubric_value['rubric_element_id'])
                inst_val.value_id = rubric_value['rubric_element_value_id']
            except models.RubricElementInstantiation.DoesNotExist:
                models.RubricElementInstantiation.objects.create(activity=new_obj.activity,
                                                                 learner=new_obj.learner,
                                                                 rubric_element_id=rubric_value['rubric_element_id'],
                                                                 value_id=rubric_value['rubric_element_value_id']
                                                                 )
        return new_obj

    def _add_rubric_element(self, activity, element):
        sign = ''
        choices = []
        if element.type == 0:
            sign = '+'
            choices = [
                (option.id, '[%s%.2f] %s' % (
                    sign,
                    option.value*option.rubric_element.weight,
                    option.get_translated_description(get_language()))
                ) for option in element.rubricelementoption_set.order_by('-value', 'id').all()
            ]
        elif element.type == 1:
            sign = '-'
            choices = [
                (option.id, '[%s%.2f] %s' % (
                    sign,
                    option.value*option.rubric_element.weight,
                    option.get_translated_description(get_language()))
                ) for option in element.rubricelementoption_set.order_by('value', 'id').all()
            ]
        field_name = 'rubric_element_%05d' % element.id
        choices = [(-1, _('Select an option'))] + choices
        self.fields[field_name] = IntegerField(
            widget=widgets.Select(choices=choices),
            label=element.get_translated_description(get_language())
        )
        try:
            inst_val = models.RubricElementInstantiation.objects.get(activity=activity,
                                                                     learner=self.instance.learner,
                                                                     rubric_element=element)
            self.initial[field_name] = inst_val.value_id
        except models.RubricElementInstantiation.DoesNotExist:
            self.initial[field_name] = -1
