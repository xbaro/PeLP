"""
    Feedback form definition for PeLP application
"""
from django.forms import ModelForm, CharField, ModelMultipleChoiceField, Form, MultipleChoiceField
from django.forms import ValidationError
from django.utils.translation import get_language, gettext as _
from django.conf import settings
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django_select2 import forms as s2forms

from .. import models


class TagsWidget(s2forms.ModelSelect2MultipleWidget):
    model = models.FaqTag
    search_fields = [
        "tag__icontains", "translatefaqtag__tag__icontains"
    ]


class LanguagesWidget(s2forms.Select2MultipleWidget):
    search_fields = [
        "tag__icontains",
    ]


class FaqForm(ModelForm):
    """
        Form used to edit FAQ entries
    """
    tags = ModelMultipleChoiceField(widget=TagsWidget(), required=False, queryset=models.FaqTag.objects)

    class Meta:
        model = models.Faq
        fields = ("tags", "public")

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
        self.fields['lang_{}_title'.format(self.default_language[0])] = CharField(
            label='Title ({})'.format(self.default_language[1]), required=True)
        self.fields['lang_{}_content'.format(self.default_language[0])] = CharField(
            widget=CKEditorWidget(), label='Content ({})'.format(self.default_language[1]), required=True)
        if self.instance is not None:
            try:
                translation = models.TranslateFaq.objects.get(faq=self.instance,
                                                              language=self.default_language[0])
                self.initial['lang_{}_title'.format(self.default_language[0])] = translation.title
                self.initial['lang_{}_content'.format(self.default_language[0])] = translation.content
            except models.TranslateFaq.DoesNotExist:
                pass

        for lang in self.additional_languages:
            self.fields['lang_{}_title'.format(lang[0])] = CharField(label='Title ({})'.format(lang[1]), required=False)
            self.fields['lang_{}_content'.format(lang[0])] = CharField(widget=CKEditorWidget(), label='Content ({})'.format(lang[1]), required=False)
            if self.instance is not None:
                try:
                    translation = models.TranslateFaq.objects.get(faq=self.instance,
                                                                  language=lang[0])
                    self.initial['lang_{}_title'.format(lang[0])] = translation.title
                    self.initial['lang_{}_content'.format(lang[0])] = translation.content
                except models.TranslateFaq.DoesNotExist:
                    pass

    @property
    def title(self):
        return self['lang_{}_title'.format(self.default_language[0])]

    @property
    def content(self):
        return self['lang_{}_content'.format(self.default_language[0])]

    def get_language_fields(self):
        for field_name in self.fields:
            if field_name.startswith('lang_'):
                yield self[field_name]

    def get_lang_field_element(self, language, element):
        return self['lang_{}_{}'.format(language, element)]

    def clean_content(self):
        data = self.cleaned_data['content']
        if len(data.strip()) == 0:
            data = None
        return data

    def clean(self):
        translations = {}
        for field_name in self.cleaned_data:
            if field_name.startswith('lang_'):
                lang_part = field_name[len('lang_'):]
                lang_code = None
                field = None
                if lang_part.endswith('_title'):
                    lang_code = lang_part[:-len('_title')]
                    field = 'title'
                elif lang_part.endswith('_content'):
                    lang_code = lang_part[:-len('_content')]
                    field = 'content'
                if lang_code is not None and field is not None:
                    if self.cleaned_data[field_name] is not None and len(self.cleaned_data[field_name].strip()) == 0:
                        self.cleaned_data[field_name] = None
                    if lang_code not in translations:
                        translations[lang_code] = {}
                    translations[lang_code][field] = self.cleaned_data[field_name]

        self.cleaned_data['translations'] = translations
        for lang in translations:
            title = self.cleaned_data['translations'][lang]['title']
            content = self.cleaned_data['translations'][lang]['content']
            if title is None and content is None:
                self.cleaned_data['translations'][lang]['delete'] = True
            elif title is None or content is None:
                if title is None:
                    self.add_error('lang_{}_title'.format(lang),
                                   ValidationError(_('This field is required'), code='invalid'))
                else:
                    self.add_error('lang_{}_title'.format(lang),
                                   ValidationError(_('This field is required'), code='invalid'))

    def save(self, commit=True):
        new_obj = super().save(commit)

        for lang in self.cleaned_data['translations']:
            try:
                translation = models.TranslateFaq.objects.get(faq=self.instance,
                                                              language=lang)
                if self.cleaned_data['translations'][lang].get('delete', False):
                    translation.delete()
                else:
                    translation.title = self.cleaned_data['translations'][lang]['title']
                    translation.content = self.cleaned_data['translations'][lang]['content']
                    translation.save()
            except models.TranslateFaq.DoesNotExist:
                if not self.cleaned_data['translations'][lang].get('delete', False):
                    models.TranslateFaq.objects.create(
                        faq=self.instance,
                        language=lang,
                        title=self.cleaned_data['translations'][lang]['title'],
                        content=self.cleaned_data['translations'][lang]['content']
                    )
        return new_obj


class FaqSearchForm(Form):
    """
        Form used to search FAQ entries
    """
    search = CharField(max_length=255, required=False)
    tags = ModelMultipleChoiceField(widget=TagsWidget(), required=False, queryset=models.FaqTag.objects)
    language = MultipleChoiceField(widget=LanguagesWidget(), choices=settings.LANGUAGES, required=False)

    def clean_search(self):
        if self.cleaned_data['search'] is None or len(self.cleaned_data['search'].strip()) == 0:
            return None
        return self.cleaned_data['search']
