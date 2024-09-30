import argparse
from django.core.management.base import BaseCommand, CommandError
from pelp.apps.web.models import Submission
from pelp.apps.web.lib.utils import compute_diff


class Command(BaseCommand):
    help = 'Compute submission differences'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Recompute differences for all submissions',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Restrict the number of submissions to be processed',
        )
        parser.add_argument(
            '--activity',
            type=int,
            default=None,
            help='Restrict the submissions of given activity',
        )
        parser.add_argument(
            '--submission',
            type=int,
            default=None,
            help='Restrict to given submission',
        )

    def handle(self, *args, **options):
        qs = Submission.objects
        if not options['force']:
            qs = qs.filter(diff_report__isnull=True)
        if options['activity'] is not None:
            qs = qs.filter(activity_id=options['activity'])
        if options['submission'] is not None:
            qs = qs.filter(id=options['submission'])
        qs = qs.all()
        if options['limit'] is not None:
            qs = qs[:options['limit']]

        for submission in qs:
            try:
                compute_diff(submission)
            except Exception as ex:
                self.stdout.write(
                    self.style.ERROR('Error computing differences for submission "%s": %s' % (submission.id, ex.__str__())))

            self.stdout.write(self.style.SUCCESS('Successfully computed differences for submission "%s"' % submission.id))
