# -*- coding: utf-8 -*-
from django.core.management import BaseCommand, call_command
from django.db.utils import IntegrityError

from commercial.models import Username
from talent.models import Person


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for p in Person.objects.all():
            try:
                Username.objects.create(username=p.slug, person=p)
            except IntegrityError:
                pass
