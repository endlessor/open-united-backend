# -*- coding: utf-8 -*-
from django.core.management import BaseCommand
from django.db.utils import IntegrityError

from commercial.models import Username
from talent.models import Person, PersonProfile


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        persons = Person.objects.all()
        for person in persons.iterator():
            obj, created = PersonProfile.objects.get_or_create(
                person=person,
                overview=""
            )
            if created:
                print(f"Profile for person: {person.full_name} was created")
