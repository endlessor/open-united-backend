# -*- coding: utf-8 -*-
from random import randrange

from django.contrib.auth.models import User
from django.core.management import BaseCommand

from commercial.models import Organisation, ProductOwner
from work.models import *
from talent.models import Person, ProductPerson, PersonProfile, Review
from matching.models import TaskClaim, TaskClaimRequest


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def create_products(self, product_owners):
        product0, status = Product.objects.get_or_create(name="AuthMachine",
                                                         short_description="Customer Identity & Access Management that"
                                                                           " puts you in control and \"just works\".",
                                                         website="https://authmachine.io",
                                                         video_url="https://www.youtube.com/watch?v=_J6LdVmnJYo",
                                                         owner=product_owners[0])

        product1, status = Product.objects.get_or_create(name="Hectic",
                                                         short_description="Modern Customer Support & Web Forms for "
                                                                           "teams, that just works.",
                                                         website="https://hectic.com",
                                                         video_url="https://www.youtube.com/watch?v=_J6LdVmnJYo",
                                                         owner=product_owners[1])

        product2, status = Product.objects.get_or_create(name="OpenUnited Product Factory",
                                                         short_description="Open-source software (OSS) has been one of "
                                                                           "the quietest revolutions in history.",
                                                         website="https://openunited.com",
                                                         video_url="https://www.youtube.com/watch?v=OWXVryhdoVA",
                                                         owner=product_owners[2])

        return [product0, product1, product2]

    def create_capabilities(self, products):
        capabilities = (
            (12, "Share Comments", ((1, "Post"),
                                    (2, "Task"),
                                    (3, "Reels"))),
            (13, "List Comments", ((4, "Showcase posts"),
                                   (5, "User reels"),
                                   (6, "Showcase tasks"))),
            (14, "Discover Comments", ((7, "Home Page"),
                                       (8, "Explore"))),
            (15, "Stay connected", ((9, "Find friends"),
                                    (10, "Connect with friends"),
                                    (11, "Message friends")))
        )

        index = 0
        for capability in capabilities:
            # Create parent category
            if not Capability.objects.filter(name=capability[1]).exists():
                parent = Capability.add_root(name=capability[1], product=products[index % len(products)])

                for sub_idx, sub_capability_name in capability[2]:
                    # Create parent category
                    parent.add_child(name=sub_capability_name,
                                     product=products[index % len(products)])
                index = index + 1

    def create_initiatives(self, product=None):
        initiative, status = Initiative.objects.get_or_create(
            name="Implement basic post sharing",
            product=product
        )
        return initiative

    def create_stacks(self):
        stack0, status = Stack.objects.get_or_create(
            name="Java"
        )
        stack1, status = Stack.objects.get_or_create(
            name="Python"
        )
        stack2, status = Stack.objects.get_or_create(
            name="Development"
        )
        return [stack0, stack1, stack2]

    def create_tasks(self, users, initiative=None, stacks=None):
        tasks = [
            {
                "title": "Take a picture",
                "description": "Description for task: Take a picture",
                "detail_url": "https://github.com/OpenUnited/product-factory/issues/7",
                "capability": "Post",
                "status": 0,
                "created_by": users[0],
                "updated_by": users[0]
            },
            {
                "title": "Take a video",
                "description": "Description for task: Take a video",
                "detail_url": "https://github.com/OpenUnited/product-factory/issues/8",
                "capability": "Post",
                "status": 1,
                "created_by": users[1],
                "updated_by": users[1]
            },
            {
                "title": "Select an existing media from the phone gallery",
                "description": "Description for task: Select an existing media from the phone gallery",
                "detail_url": "https://github.com/OpenUnited/product-factory/issues/4",
                "capability": "Post",
                "status": 2,
                "created_by": users[0],
                "updated_by": users[0]
            },
            {
                "title": "Apply a filter",
                "description": "Description for task: Apply a filter",
                "detail_url": "https://github.com/OpenUnited/product-factory/issues/7",
                "capability": "Post",
                "status": 3,
                "created_by": users[0],
                "updated_by": users[0]
            },
            {
                "title": "Trim a video",
                "description": "Description for task: Trim a video",
                "detail_url": "https://github.com/OpenUnited/product-factory/issues/8",
                "capability": "Post",
                "status": 0,
                "created_by": users[1],
                "updated_by": users[1]
            },
            {
                "title": "Take a picture",
                "description": "Description for task: Take a picture",
                "detail_url": "https://github.com/OpenUnited/product-factory/issues/4",
                "capability": "Post",
                "status": 1,
                "created_by": users[1],
                "updated_by": users[1]
            },
            {
                "title": "Crop an image",
                "description": "Description for task: Crop an image",
                "detail_url": "https://github.com/OpenUnited/product-factory/issues/7",
                "capability": "Post",
                "status": 2,
                "created_by": users[0],
                "updated_by": users[0]
            },
            {
                "title": "Select a cover for the video",
                "description": "Description for task: Select a cover for the video",
                "detail_url": "https://github.com/OpenUnited/product-factory/issues/8",
                "capability": "Post",
                "status": 3,
                "created_by": users[1],
                "updated_by": users[1]
            },
            {
                "title": "Write a caption",
                "description": "Description for task: Tag people",
                "detail_url": None,
                "capability": "Post",
                "status": 0,
                "created_by": users[1],
                "updated_by": users[1]
            }
        ]
        
        for task in tasks:
            try:
                capability = Capability.objects.get(name=task["capability"])
                task, created = Task.objects.get_or_create(title=task["title"],
                                                           description=task["description"],
                                                           initiative=initiative,
                                                           capability=capability,
                                                           status=Task.TASK_STATUS_AVAILABLE,
                                                           created_by=task["created_by"],
                                                           reviewer=users[0],
                                                           updated_by=task["updated_by"],
                                                           product=Product.objects.get(slug="authmachine"))
                ProductTask.objects.get_or_create(product=Product.objects.get(slug="authmachine"), task=task)
                if created and stacks:
                    task.stack.add(stacks[randrange(len(stacks))])
            except Exception as e:
                print("Errors when creating tasks: ", str(e))
                pass

    def create_users(self):
        person0_user, status = User.objects.get_or_create(email="matt.haddad@gmail.com", username="matt.haddad")
        person0, status = Person.objects.get_or_create(full_name="Matthew Haddad",
                                                       user=person0_user,
                                                       slug="matt.haddad",
                                                       username="matt.haddad",
                                                       email_address="matt.haddad@gmail.com",
                                                       test_user=True)

        person1_user, status = User.objects.get_or_create(email="jamesrese098@gmail.com", username="jamesrese098")
        person1, status = Person.objects.get_or_create(full_name="James Reese",
                                                       user=person1_user,
                                                       slug="jamesrese098",
                                                       username="jamesrese098",
                                                       email_address="jamesrese098@gmail.com",
                                                       test_user=True)

        organization0, status = Organisation.objects.get_or_create(name="John Smith Organization",
                                                                   username="john.smith.org")

        return [person0, person1, organization0]

    def create_product_owners(self, users):
        product_owner0, status = ProductOwner.objects.get_or_create(person=users[0])
        product_owner1, status = ProductOwner.objects.get_or_create(person=users[1])
        product_owner2, status = ProductOwner.objects.get_or_create(organisation=users[2])
        return [product_owner0, product_owner1, product_owner2]

    def create_matches(self, users):
        tasks = Task.objects.all()
        num_of_users = len(users) - 1
        index = 0

        for task in tasks:
            person = users[index % num_of_users]
            TaskClaimRequest.objects.get_or_create(task=task,
                                                   person=person,
                                                   kind=1)
            TaskClaim.objects.get_or_create(task=task,
                                            person=person,
                                            kind=TaskClaim.CLAIM_TYPE[index % 3][0])
            index = index + 1

    def create_product_persons(self, users, products):
        ProductPerson.objects.get_or_create(product=products[0],
                                            person=users[0],
                                            right=2)
        ProductPerson.objects.get_or_create(product=products[0],
                                            person=users[1],
                                            right=1)

        ProductPerson.objects.get_or_create(product=products[1],
                                            person=users[0],
                                            right=1)
        ProductPerson.objects.get_or_create(product=products[1],
                                            person=users[1],
                                            right=3)

        ProductPerson.objects.get_or_create(product=products[2],
                                            person=users[0],
                                            right=2)
        ProductPerson.objects.get_or_create(product=products[2],
                                            person=users[1],
                                            right=1)

    def create_person_profiles(self, users):
        PersonProfile.objects.get_or_create(
            person=users[0],
            overview="Hi, I am a designer with experience in creating digital interfaces, \
                    websites, and print design but I also have the ability to \
                    bring those concepts to life through creative front-end development for \
                    small projects."
        )

        PersonProfile.objects.get_or_create(
            person=users[1],
            overview="I am a responsible and autonomous person – I am capable of breaking down complex tasks, "
                     "providing reasonable estimates and updating status on them, with immediate notifying about "
                     "blockers. I am always available under discussed hours, and take remote work seriously."
        )

    def create_reviews(self, users, products):
        Review.objects.get_or_create(
            id=1,
            product=products[0],
            person=users[0],
            score=5,
            text="Hi! I am a software developer with main expertise in JavaScript (both frontend and Node.js) and some "
                 "Python. I have more than 6 years of experience working with modern JavaScript – I have created "
                 "several projects from scratch, fully architecting them. I write pragmatic, reliable code which "
                 "is covered by tests.",
            created_by=users[0]
        )
        Review.objects.get_or_create(
            id=3,
            product=products[0],
            person=users[0],
            score=4,
            text="I have been developing the projects from the scratch to the market ready app with strong skills "
                 "and time efficient manner. I work well with others and I look forward to gaining more experience "
                 "and learning more. I prefer a long-term relationship rather than money.",
            created_by=users[1]
        )
        Review.objects.get_or_create(
            id=4,
            product=products[0],
            person=users[1],
            score=4,
            text="I am fairly familiar with bot development and asynchronous tasks management. \
                I have developed slack, telegram and scraping bots that are integrated with 3rd party apps and APIs. \
                In terms of Asynchronous tasks and message brokers, I used celery and RabbitMQ.",
            created_by=users[1]
        )
        Review.objects.get_or_create(
            id=6,
            product=products[0],
            person=users[1],
            score=4,
            text="VATBox, a cloud-based solution that enables companies to reclaim potential value-added tax (VAT) "
                 "paid abroad. Its solution automatically tracks expenses, as well as produces detailed graphic "
                 "reports with projected VAT reclaims and information on rejected reclaims. The organisation’s "
                 "solution also integrates with various ERP platforms",
            created_by=users[1]
        )
        Review.objects.get_or_create(
            id=8,
            product=products[1],
            person=users[0],
            score=4,
            text="I'm well versed in all aspects of development including: front end development, user experience, "
                 "responsive web design, back end development, databases, source control, testing, and project "
                 "management.",
            created_by=users[0]
        )
        Review.objects.get_or_create(
            id=9,
            product=products[1],
            person=users[1],
            score=3,
            text="Please review the portfolio section of my person profile in order to see my latest work. "
                 "Don't hesitate to invite me to your project and to discuss whether I would be a good fit for it.",
            created_by=users[1]
        )
        Review.objects.get_or_create(
            id=11,
            product=products[2],
            person=users[0],
            score=4,
            text="My customers are always up-to-date during the development process and are made sure to be happy "
                 "with the results. Further I also provide any documentation and instructions necessary, to prevent "
                 "vendor lock-in.",
            created_by=users[0]
        )
        Review.objects.get_or_create(
            id=12,
            product=products[2],
            person=users[1],
            score=3,
            text="With most of my projects, I am responsible for everything from ground up. This, of course, "
                 "includes the code of the application, but also the automated pipelines, automated deployments, "
                 "version control, and Infrastructure-as-Code. I have vast experience with designing and developing "
                 "system architectures in Google Cloud and Amazon Web Services.",
            created_by=users[1]
        )

    def handle(self, *args, **options):
        # Create users
        users = self.create_users()
        product_owners = self.create_product_owners(users)

        # Create products & capabilities
        products = self.create_products(product_owners)
        self.create_capabilities(products)

        # Create a initiative for product1
        initiative = self.create_initiatives(products[0])

        # Create stacks
        stacks = self.create_stacks()

        # Create tasks
        self.create_tasks(users, initiative, stacks)

        # Create matches
        self.create_matches(users)

        # Create product person
        self.create_product_persons(users, products)

        # Create person profiles
        self.create_person_profiles(users)

        # Create reviews
        self.create_reviews(users, products)
