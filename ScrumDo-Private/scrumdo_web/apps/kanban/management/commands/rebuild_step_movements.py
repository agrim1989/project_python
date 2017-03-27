#!/usr/bin/env python

from apps.projects.models import Project, Story
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from apps.kanban.models import RebuildMovementJob
from apps.kanban.tasks import rebuildStepMovements
import logging

import apps.kanban.managers as kanban_managers
from apps.kanban.tasks import scheduleRebuildStepMovements

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option('--project', '-p', dest='project_slug',  help='Help for the long options'),
            make_option('--all', action='store_true', dest='all', default=False, help='Rebuild all projects'),        
        )
    args = "project"
    def handle(self, *args, **options):
        allProjects = options["all"]
        if allProjects:
            projects = Project.objects.filter(abandoned=False, active=True, project_type__in=[Project.PROJECT_TYPE_KANBAN, Project.PROJECT_TYPE_PORTFOLIO])
        else:
            slug = options["project_slug"]
            try:
                projects = [Project.objects.get(slug=slug)]
            except Project.DoesNotExist:
                print "Could not find project."
                return

        for project in projects:
            # scheduleRebuildStepMovements(project)
            job = RebuildMovementJob(project=project, initiator=None)
            job.save()
            rebuildStepMovements(job.id)



