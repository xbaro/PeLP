"""
    PeLP Views package
"""
from .index import index_view

from .activity import (
    activity_detail,
    activity_report,
    activity_statistics,
    activity_configuration,
    activity_report_detail,
)
from .course import (
    courses,
    course_detail,
    course_learners,
)

from .faq import (
    faq,
    faq_view,
    faq_edit,
    faq_delete,
)

from .feedback import (
    activity_evaluation,
    activity_evaluation_group,
)

from .submission import (
    submissions,
    submission_detail,
)

from .import_session import (
    import_sessions,
    import_session_detail,
)

from .project import (
    projects,
    project_details,
)

__all__ = [
    "index_view",
    # Activity views
    "activity_detail",
    "activity_report",
    "activity_statistics",
    "activity_configuration",
    "activity_report_detail",
    # Course views
    "courses",
    "course_detail",
    "course_learners",
    # FAQ
    "faq",
    "faq_view",
    "faq_edit",
    "faq_delete",
    # Course Activity Feedback
    "activity_evaluation",
    "activity_evaluation_group",
    # Course Activity Submissions
    "submissions",
    "submission_detail",
    # Import Sessions
    "import_sessions",
    "import_session_detail",
    # Projects
    "projects",
    "project_details",
]
