from django.conf import settings
from django.db import models, transaction
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import model_to_dict
from django.utils.text import slugify
from django_lifecycle import LifecycleModelMixin, hook, BEFORE_SAVE
from django_lifecycle.hooks import BEFORE_CREATE
from model_utils import FieldTracker
from treebeard.mp_tree import MP_Node
from backend.mixins import TimeStampMixin, UUIDMixin
from backend.utils import send_email
from talent.models import Person, ProductPerson
from work.utils import get_person_data


class Tag(TimeStampMixin):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Stack(TimeStampMixin, UUIDMixin):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Capability(MP_Node):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=1000, default='')
    video_link = models.CharField(max_length=255, blank=True)
    comments_start = models.ForeignKey(to='comments.capabilitycomment',
                                       on_delete=models.SET_NULL,
                                       null=True, editable=False)

    class Meta:
        db_table = 'capability'

    def __str__(self):
        return self.name


@receiver(post_save, sender=Capability)
def save_capability(sender, instance, created, **kwargs):
    if not created:
        # update tasklisting when capability info is updated
        TaskListing.objects.filter(capability=instance).update(capability_data=model_to_dict(instance))


class CapabilityStack(models.Model):
    capability = models.ForeignKey(to=Capability, on_delete=models.CASCADE)
    stack = models.ForeignKey(to=Stack, on_delete=models.CASCADE)

    class Meta:
        db_table = 'capability_stack'


class Attachment(models.Model):
    name = models.CharField(max_length=512)
    path = models.URLField()
    file_type = models.CharField(max_length=5, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CapabilityAttachment(models.Model):
    capability = models.ForeignKey(Capability, on_delete=models.CASCADE)
    attachment = models.ForeignKey(Attachment, on_delete=models.CASCADE)

    class Meta:
        db_table = 'capability_attachment'


class Product(LifecycleModelMixin, TimeStampMixin, UUIDMixin):
    photo = models.URLField(blank=True, null=True, default=None)
    name = models.TextField()
    short_description = models.TextField()
    full_description = models.TextField(blank=True, null=True)
    website = models.CharField(max_length=512)
    detail_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    attachment = models.ManyToManyField(Attachment, related_name="product_attachements", blank=True)
    slug = models.SlugField(unique=True)
    capability_start = models.ForeignKey(Capability, on_delete=models.CASCADE, null=True, editable=False)
    owner = models.ForeignKey('commercial.ProductOwner', on_delete=models.CASCADE, null=True)
    is_private = models.BooleanField(default=False)

    @hook(BEFORE_CREATE)
    @hook(BEFORE_SAVE, when="name", has_changed=True)
    def update_slug(self, *args, **kwargs):
        self.slug = slugify(self.name)

    def get_members_emails(self):
        return self.productperson_set.all().values_list("person__email_address", flat=True)

    def is_product_member(self, person):
        return self.productperson_set.filter(person=person).exists()

    def get_product_owner(self):
        product_owner = self.owner
        return product_owner.organisation if product_owner.organisation else product_owner.person

    def __str__(self):
        return self.name


@receiver(post_save, sender=Product)
def save_product(sender, instance, created, **kwargs):
    if not created:
        # update tasklisting when product info is updated
        TaskListing.objects.filter(product=instance).update(
            product_data=dict(
                name=instance.name,
                slug=instance.slug,
                owner=instance.get_product_owner().username
            )
        )


class Initiative(TimeStampMixin, UUIDMixin):
    INITIATIVE_STATUS = (
        (1, "Active"),
        (2, "Completed")
    )
    name = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices=INITIATIVE_STATUS, default=1)

    def __str__(self):
        return self.name

    def get_available_tasks_count(self):
        return self.task_set.filter(status=Task.TASK_STATUS_AVAILABLE).count()

    def get_completed_task_count(self):
        return self.task_set.filter(status=Task.TASK_STATUS_DONE).count()

    def get_task_tags(self):
        return Tag.objects.filter(task_tags__initiative=self).distinct("id").all()

    def get_task_stacks(self):
        return Stack.objects.filter(task_stacks__initiative=self).distinct("id").all()

    @staticmethod
    def get_filtered_data(input_data, filter_data=None, exclude_data=None):
        if filter_data is None:
            filter_data = {}
        if not filter_data:
            filter_data = dict()

        if not input_data:
            input_data = dict()

        statuses = input_data.get("statuses", [])
        tags = input_data.get("tags", [])
        stacks = input_data.get("stacks", [])

        if statuses:
            filter_data["status__in"] = statuses

        if tags:
            filter_data["task__tag__in"] = tags

        if stacks:
            filter_data["task__stack__in"] = stacks

        queryset = Initiative.objects.filter(**filter_data)
        if exclude_data:
            queryset = queryset.exclude(**exclude_data)

        return queryset.distinct("id").all()


@receiver(post_save, sender=Initiative)
def save_initiative(sender, instance, created, **kwargs):
    if not created:
        # update tasklisting when initiative info is updated
        TaskListing.objects.filter(initiative=instance).update(initiative_data=model_to_dict(instance))


class Task(TimeStampMixin, UUIDMixin):
    TASK_STATUS_DRAFT = 0
    TASK_STATUS_BLOCKED = 1
    TASK_STATUS_AVAILABLE = 2
    TASK_STATUS_CLAIMED = 3
    TASK_STATUS_DONE = 4

    TASK_STATUS = (
        (TASK_STATUS_DRAFT, "Draft"),
        (TASK_STATUS_BLOCKED, "Blocked"),
        (TASK_STATUS_AVAILABLE, "Available"),
        (TASK_STATUS_CLAIMED, "Claimed"),
        (TASK_STATUS_DONE, "Done")
    )
    TASK_PRIORITY = (
        (0, 'High'),
        (1, 'Medium'),
        (2, 'Low')
    )
    initiative = models.ForeignKey(Initiative, on_delete=models.SET_NULL, blank=True, null=True)
    capability = models.ForeignKey(Capability, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.TextField()
    description = models.TextField()
    short_description = models.TextField(max_length=256)
    status = models.IntegerField(choices=TASK_STATUS, default=0)
    attachment = models.ManyToManyField(Attachment, related_name="task_attachements", blank=True)
    tag = models.ManyToManyField(Tag, related_name="task_tags", blank=True)
    stack = models.ManyToManyField(Stack, related_name="task_stacks", blank=True, verbose_name="Skills Required")
    blocked = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    priority = models.IntegerField(choices=TASK_PRIORITY, default=1)
    published_id = models.IntegerField(default=0, blank=True, editable=False)
    auto_approve_task_claims = models.BooleanField(default=True)
    created_by = models.ForeignKey('talent.Person', on_delete=models.CASCADE, blank=True, null=True,
                                   related_name="created_by")
    updated_by = models.ForeignKey('talent.Person', on_delete=models.CASCADE, blank=True, null=True,
                                   related_name="updated_by")
    tracker = FieldTracker()
    comments_start = models.ForeignKey(to='comments.taskcomment', on_delete=models.SET_NULL, null=True, editable=False)
    reviewer = models.ForeignKey('talent.Person', on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name_plural = "Tasks"

    def __str__(self):
        return self.title

    @staticmethod
    def get_filtered_data(input_data, filter_data=None, exclude_data=None):
        if filter_data is None:
            filter_data = {}
        if not filter_data:
            filter_data = dict()

        if not input_data:
            input_data = dict()

        sorted_by = input_data.get("sorted_by", "title")
        statuses = input_data.get("statuses", [])
        tags = input_data.get("tags", [])
        priority = input_data.get("priority", [])
        assignee = input_data.get("assignee", [])
        stacks = input_data.get("stacks", [])
        task_creator = input_data.get("task_creator", [])

        if statuses:
            filter_data["status__in"] = statuses

        if tags:
            filter_data["tag__in"] = tags

        if stacks:
            filter_data["stack__in"] = stacks

        if priority:
            filter_data["priority__in"] = priority

        if task_creator:
            filter_data["created_by__in"] = task_creator

        if assignee:
            filter_data["taskclaim__kind__in"] = [0, 1]
            filter_data["taskclaim__person_id__in"] = assignee

        queryset = Task.objects.filter(**filter_data)
        if exclude_data:
            queryset = queryset.exclude(**exclude_data)

        return queryset.order_by(sorted_by).all()

    def get_task_link(self, show_domain_name=True):
        try:
            product = self.producttask_set.first().product
            product_owner = product.get_product_owner()
            domain_name = settings.FRONT_END_SERVER if show_domain_name else ""
            return f"{domain_name}/{product_owner.username}/{product.slug}/tasks/{self.published_id}"
        except ProductTask.DoesNotExist:
            return None


@receiver(post_save, sender=Task)
def save_task(sender, instance, created, **kwargs):
    # If task changed status to available/claimed/done
    try:
        reviewer = instance.reviewer
        if instance.tracker.previous('status') and instance.tracker.previous('status') != instance.status and \
                (
                        instance.status == Task.TASK_STATUS_AVAILABLE or instance.status == Task.TASK_STATUS_CLAIMED or
                        instance.status == Task.TASK_STATUS_DONE
                ):
            status = ''
            if instance.status == Task.TASK_STATUS_AVAILABLE:
                status = 'available'
            elif instance.status == Task.TASK_STATUS_CLAIMED:
                status = 'claimed'
            elif instance.status == Task.TASK_STATUS_DONE:
                status = 'done'

            if reviewer:
                send_email(
                    to_emails=reviewer.email_address,
                    subject='Task status changed',
                    content=f"""
                        The task {instance.title} is {status} now.
                        You can see the task here: {instance.get_task_link()}
                    """
                )

        # set contributor role for user if task is done
        if instance.status == Task.TASK_STATUS_DONE and instance.tracker.previous('status') != Task.TASK_STATUS_DONE:
            try:
                task_claim = instance.taskclaim_set.filter(kind=0).first()
                if task_claim:
                    product_person_data = dict(
                        product_id=instance.product.id,
                        person_id=task_claim.person.id
                    )
                    if not ProductPerson.objects.filter(**product_person_data,
                                                        right__in=[ProductPerson.PERSON_TYPE_CONTRIBUTOR,
                                                                   ProductPerson.PERSON_TYPE_PRODUCT_ADMIN,
                                                                   ProductPerson.PERSON_TYPE_PRODUCT_MANAGER]).exists():
                        with transaction.atomic():
                            ProductPerson.objects.create(**product_person_data,
                                                         right=ProductPerson.PERSON_TYPE_CONTRIBUTOR)
            except Exception as e:
                print("Failed to change a user role", e, flush=True)

        if instance.tracker.previous('status') != instance.status \
                and instance.status == Task.TASK_STATUS_CLAIMED \
                and reviewer:
            send_email(
                to_emails=reviewer.email_address,
                subject='Task status changed',
                content=f"""
                    The task {instance.title} is claimed now.
                    You can see the task here: {instance.get_task_link()}
                """
            )
    except Person.DoesNotExist:
        pass

    task_listing_data = dict(
        title=instance.title,
        description=instance.description,
        short_description=instance.short_description,
        status=instance.status,
        stacks=list(instance.stack.all().values_list('name', flat=True)),
        tags=list(instance.tag.all().values_list('name', flat=True)),
        blocked=instance.blocked,
        featured=instance.featured,
        priority=instance.priority,
        published_id=instance.published_id,
        auto_approve_task_claims=instance.auto_approve_task_claims,
        creator=instance.created_by,
        created_by=get_person_data(instance.created_by),
        updated_by=get_person_data(instance.updated_by),
        reviewer=get_person_data(instance.reviewer) if instance.reviewer else None,
        product_data={
            "name": instance.product.name,
            "slug": instance.product.slug,
            "owner": instance.product.get_product_owner().username
        } if instance.product else None,
        product=instance.product,
        has_active_depends=Task.objects.filter(taskdepend__task=instance.id).exclude(status=Task.TASK_STATUS_DONE).exists(),
        initiative=instance.initiative,
        initiative_data=model_to_dict(instance.initiative) if instance.initiative else None,
        capability=instance.capability,
        capability_data=model_to_dict(instance.capability) if instance.capability else None,
        in_review=instance.taskclaim_set.filter(kind=0).count() > 0
    )

    task_claim = instance.taskclaim_set.filter(kind__in=[0, 1]).first()

    if task_claim:
        task_listing_data["task_claim"] = model_to_dict(task_claim)
        task_listing_data["assigned_to_data"] = get_person_data(task_claim.person)
        task_listing_data["assigned_to"] = task_claim.person
    else:
        task_listing_data["task_claim"] = None
        task_listing_data["assigned_to_data"] = None
        task_listing_data["assigned_to"] = None

    if created:
        product = instance.producttask_set.first()
        last_product_task = None
        if product:
            last_product_task = Task.objects \
                .filter(producttask__product=instance.producttask_set.first().product) \
                .order_by('-published_id').last()
        published_id = last_product_task.published_id + 1 if last_product_task else 1
        instance.published_id = published_id
        instance.save()

        task_listing_data["published_id"] = published_id

    # create TaskListing object
    tasklisting_exist = TaskListing.objects.filter(task=instance).exists()

    if tasklisting_exist:
        TaskListing.objects.filter(task=instance).update(**task_listing_data)
    else:
        TaskListing.objects.create(
            task=instance,
            **task_listing_data
        )


class TaskListing(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, unique=True)
    title = models.TextField()
    description = models.TextField()
    short_description = models.TextField(max_length=256)
    status = models.IntegerField(choices=Task.TASK_STATUS, default=0)
    tags = ArrayField(ArrayField(models.CharField(max_length=254)))
    stacks = ArrayField(ArrayField(models.CharField(max_length=254)))
    blocked = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    priority = models.IntegerField(choices=Task.TASK_PRIORITY, default=1)
    published_id = models.IntegerField(default=0, blank=True, editable=False)
    auto_approve_task_claims = models.BooleanField(default=True)
    creator = models.ForeignKey(Person, on_delete=models.SET_NULL, related_name="creator", null=True)
    created_by = models.JSONField()
    updated_by = models.JSONField()
    reviewer = models.JSONField(null=True)
    product_data = models.JSONField(null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)

    task_claim = models.JSONField(null=True)
    assigned_to_data = models.JSONField(null=True)
    assigned_to = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, related_name="assigned_to")
    has_active_depends = models.BooleanField(default=False)
    initiative = models.ForeignKey(Initiative, on_delete=models.SET_NULL, null=True)
    initiative_data = models.JSONField(null=True)
    capability = models.ForeignKey(Capability, on_delete=models.SET_NULL, null=True)
    capability_data = models.JSONField(null=True)

    in_review = models.BooleanField(default=False)

    @staticmethod
    def get_filtered_data(input_data, filter_data=None, exclude_data=None):
        if filter_data is None:
            filter_data = {}
        if not filter_data:
            filter_data = dict()

        if not input_data:
            input_data = dict()

        sorted_by = input_data.get("sorted_by", "title")
        statuses = input_data.get("statuses", [])
        tags = input_data.get("tags", [])
        priority = input_data.get("priority", [])
        assignee = input_data.get("assignee", [])
        stacks = input_data.get("stacks", [])
        task_creator = input_data.get("task_creator", [])

        if statuses:
            filter_data["status__in"] = statuses

        if tags:
            filter_data["tags__contains"] = tags

        if stacks:
            filter_data["stacks__contains"] = stacks

        if priority:
            filter_data["priority__in"] = priority

        if task_creator:
            filter_data["creator_id__in"] = task_creator

        if assignee:
            filter_data["assigned_to_id__in"] = assignee

        queryset = TaskListing.objects.filter(**filter_data)
        if exclude_data:
            queryset = queryset.exclude(**exclude_data)

        return queryset.order_by(sorted_by).all()


class TaskDepend(models.Model):
    task = models.ForeignKey(to=Task, on_delete=models.CASCADE, related_name='Task')
    depends_by = models.ForeignKey(to=Task, on_delete=models.CASCADE)

    class Meta:
        db_table = 'work_task_depend'


class ProductTask(TimeStampMixin, UUIDMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)


@receiver(post_save, sender=ProductTask)
def save_product_task(sender, instance, created, **kwargs):
    if created:
        task = instance.task
        last_product_task = Task.objects \
            .filter(producttask__product=instance.product) \
            .order_by('-published_id').first()
        task.published_id = last_product_task.published_id + 1 if last_product_task else 1
        task.save()


class CodeRepository(TimeStampMixin, UUIDMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    # task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=True, null=True)
    repository = models.URLField(blank=True, null=True)
    git_owner = models.CharField(max_length=255)
    git_access_token = models.CharField(max_length=65)

    class Meta:
        verbose_name_plural = "CodeRepositories"

    def __str__(self):
        return f"{self.product.name} - {self.repository}"
