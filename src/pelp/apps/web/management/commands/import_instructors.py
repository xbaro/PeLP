import argparse
import typing

from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from pelp.apps.web.models import Course, Semester
from pelp.apps.web.lib.lms.canvas import LMSCanvas


class Command(BaseCommand):
    help = 'Import Course Instructors'

    def add_arguments(self, parser):
        parser.add_argument(
            'course',
            type=str,
            default=None,
            help='Course code',
        )
        parser.add_argument(
            '--semester',
            type=str,
            default=None,
            help='Semester code',
        )

    def handle(self, *args, **options):

        self.stdout.write(
            "Accessing course instructors"
        )

        semester: typing.Optional[Semester] = None
        if options['semester'] is None:
            # Get current semester
            active_semesters = Semester.objects.filter(start__lte=timezone.now(), end__gte=timezone.now())
            if len(active_semesters) == 0:
                self.stdout.write(
                    self.style.ERROR(
                        'There is no active semester. Please provide semester code.'
                    )
                )
            elif len(active_semesters) > 1:
                self.stdout.write(
                    self.style.ERROR(
                        'Multiple active semesters. Please provide semester code.'
                    )
                )
            else:
                semester = active_semesters[0]
        else:
            try:
                semester = Semester.objects.get(code__iexact=options['semester'])
            except Semester.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        'Invalid semester code.'
                    )
                )

        if semester is None:
            self.stdout.write(
                self.style.ERROR(
                    'Cannot continue.'
                )
            )
            return

        try:
            course = Course.objects.get(code__icontains=options['course'], semester=semester)
        except Course.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f'Cannot find a course with such code in semester {semester.code}.'
                )
            )
            return

        lms = LMSCanvas()
        result = lms.update_course_instructors(course)

        if result.valid:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {result.num_total} instructors. Created: {result.num_created}, Assigned: {result.num_assigned}'))
        else:
            self.stdout.write(
                self.style.ERROR('Error importing instructors. Exceptions:'))
            for exception in result.exceptions:
                self.stdout.write(
                    self.style.ERROR(exception.__str__()))

