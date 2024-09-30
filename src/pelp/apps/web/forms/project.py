"""
    Activity project form definition for PeLP application
"""
from django.forms import ModelForm, HiddenInput, CharField
from .. import models


class ProjectForm(ModelForm):
    """
        Form used to define activity's project properties
    """
    src_form = CharField(widget=HiddenInput(), required=False, initial="project")

    class Meta:
        model = models.Project
        fields = ("type", "executable_name",
                  "anchor_file", "allowed_files_regex",
                  "image", "test_arguments",
                  "results_path", "progress_path",
                  "max_execution_time", "mem_limit",
                  "use_valgrind", "valgrind_report_path",
                  "repository_url", "repository_base_branch", "repository_test_branch",
                  "code_base_zip", "code_test_zip",
                  "repository", "activity", "id",
                  "src_form", "allow_base_failure")
        widgets = {
            'activity': HiddenInput(),
            'repository': HiddenInput(),
            'id': HiddenInput(),
        }
