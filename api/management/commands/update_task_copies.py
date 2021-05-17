# -*- coding: utf-8 -*-
from django.core.management import BaseCommand, call_command
from django.db.utils import IntegrityError
from django.forms.models import model_to_dict
from work.models import Task, TaskListing
from work.utils import get_person_data


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        tasks = Task.objects.all()
        for task in tasks.iterator():
            try:
                tasklisting = TaskListing.objects.get(task=task)
                tasklisting.in_review = task.taskclaim_set.filter(kind=0).exists()
                tasklisting.save()
            except TaskListing.DoesNotExist:
                pass

        print("update task copies is finished!")
