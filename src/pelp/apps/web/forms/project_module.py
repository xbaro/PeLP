"""
    Activity project module form definition for PeLP application
"""
from django.forms import ModelForm, HiddenInput, CharField
from .. import models


class ProjectModuleForm(ModelForm):
    """
        Form used to define activity's project module properties
    """
    src_form = CharField(widget=HiddenInput(), required=False, initial="project_module")

    class Meta:
        model = models.ProjectModule
        fields = ("type", "name", "base_path", "allowed_files_regex",
                  "project", "id", "src_form")
        widgets = {
            'project': HiddenInput(),
            'id': HiddenInput(),
        }
