"""
    Activity form definition for PeLP application
"""
from django.conf import settings
from django.forms import ModelForm, HiddenInput, CharField, DateField, DateInput
from ckeditor.widgets import CKEditorWidget
from .. import models


class ActivityForm(ModelForm):
    """
        Form used to define activity properties
    """
    description = CharField(widget=CKEditorWidget(), required=False)
    src_form = CharField(widget=HiddenInput(), required=False, initial="activity")
    start = DateField(
        input_formats=[
            "%Y-%m-%d",
        ],
        widget=DateInput(attrs={
            'type': 'date'
        },
        format="%Y-%m-%d")
    )
    end = DateField(
        input_formats=[
            "%Y-%m-%d",
        ],
        widget=DateInput(attrs={
            'type': 'date'
        },
        format="%Y-%m-%d")
    )

    class Meta:
        model = models.Activity
        fields = ("id", "code", "name", "description", "start", "end", "course", "src_form", "rubric",
                  "enabled", "max_submissions", "max_submissions_day", "historic_code", "self_evaluation",
                  "include_report", "report_name")
        widgets = {
            'id': HiddenInput(),
            'course': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        default_language_code = settings.LANGUAGE_CODE.split('_')[0].split('-')[0]

        self.additional_languages = [
            l for l in settings.LANGUAGES if l[0].split('_')[0].split('-')[0] != default_language_code
        ]
        self.default_language = [
            l for l in settings.LANGUAGES if l[0].split('_')[0].split('-')[0] == default_language_code
        ][0]

        self.lang_elements = {}
        for lang in self.additional_languages:
            self.fields['lang_{}_name'.format(lang[0])] = CharField(label='Name ({})'.format(lang[1]), required=False)
            self.fields['lang_{}_description'.format(lang[0])] = CharField(widget=CKEditorWidget(), label='Description ({})'.format(lang[1]), required=False)
            if self.instance is not None:
                try:
                    translation = models.TranslateActivity.objects.get(activity=self.instance,
                                                                       language=lang[0])
                    self.initial['lang_{}_name'.format(lang[0])] = translation.name
                    self.initial['lang_{}_description'.format(lang[0])] = translation.description
                except models.TranslateActivity.DoesNotExist:
                    pass

    def get_language_fields(self):
        for field_name in self.fields:
            if field_name.startswith('lang_'):
                yield self[field_name]

    def get_lang_field_element(self, language, element):
        return self['lang_{}_{}'.format(language, element)]

    def clean_description(self):
        data = self.cleaned_data['description']
        if data is None or len(data.strip()) == 0:
            data = None
        return data

    def clean_report_name(self):
        data = self.cleaned_data['report_name']
        if data is None or len(data.strip()) == 0:
            data = None
        return data

    def clean(self):
        translations = {}
        for field_name in self.cleaned_data:
            if field_name.startswith('lang_'):
                lang_part = field_name[len('lang_'):]
                lang_code = None
                field = None
                if lang_part.endswith('_name'):
                    lang_code = lang_part[:-len('_name')]
                    field = 'name'
                elif lang_part.endswith('_description'):
                    lang_code = lang_part[:-len('_description')]
                    field = 'description'
                if lang_code is not None and field is not None:
                    if lang_code not in translations:
                        translations[lang_code] = {}
                    translations[lang_code][field] = self.cleaned_data[field_name]
                    if self.cleaned_data[field_name] is not None and len(self.cleaned_data[field_name].strip()) == 0:
                        self.cleaned_data[field_name] = None
        self.cleaned_data['translations'] = translations

    def save(self, commit=True):
        new_obj = super().save(commit)

        for lang in self.cleaned_data['translations']:
            try:
                translation = models.TranslateActivity.objects.get(activity=self.instance,
                                                                   language=lang)
                translation.name = self.cleaned_data['translations'][lang]['name']
                translation.description = self.cleaned_data['translations'][lang]['description']
                translation.save()
            except models.TranslateActivity.DoesNotExist:
                models.TranslateActivity.objects.create(
                    activity=self.instance,
                    language=lang,
                    name=self.cleaned_data['translations'][lang]['name'],
                    description=self.cleaned_data['translations'][lang]['description']
                )
        return new_obj
