from django.db.models import Q
import graphene
from graphene_django.types import DjangoObjectType, ObjectType
import graphene_django_optimizer as gql_optimizer
from api.talent.types import PersonType
from api.utils import get_current_person
from api.work.utils import get_right_task_status
from matching.models import CLAIM_TYPE_DONE
from talent.models import ProductPerson
from work.models import *


class TaskType(DjangoObjectType):
    id = graphene.Int()
    product = graphene.Field(lambda: ProductType)
    priority = graphene.String()
    can_edit = graphene.Boolean(user_id=graphene.Int())
    assigned_to = graphene.Field(PersonType)
    in_review = graphene.Boolean()
    stack = graphene.List(lambda: StackType)
    depend_on = graphene.List(lambda: TaskType)
    relatives = graphene.List(lambda: TaskType)
    status = graphene.Int()
    link = graphene.String()
    has_active_depends = graphene.Boolean()

    class Meta:
        model = Task
        convert_choices_to_enum = False

    def resolve_stack(self, _):
        return self.stack.all()

    def resolve_assigned_to(self, _):
        task_claim = self.taskclaim_set.filter(kind__in=[0, 1]).first()
        return task_claim.person if task_claim else None

    def resolve_in_review(self, _):
        return self.taskclaim_set.filter(kind=CLAIM_TYPE_DONE).count() > 0

    def resolve_priority(self, _):
        try:
            return Task.TASK_PRIORITY[self.priority][1]
        except:
            return None

    def resolve_can_edit(self, _, **kwargs):
        current_person = get_current_person(_, kwargs)
        try:
            if not current_person:
                return False

            return ProductPerson.objects.filter(
                product=ProductTask.objects.get(task_id=self.id).product,
                person=current_person,
                right__in=[1, 2, 4]
            ).exists()
        except (ProductPerson.DoesNotExist, ProductTask.DoesNotExist):
            return False

    def resolve_depend_on(self, _, **kwargs):
        try:
            return Task.objects.filter(taskdepend__task=self.id)
        except Task.DoesNotExist:
            return None

    def resolve_has_active_depends(self, info):
        return Task.objects.filter(taskdepend__task=self.id).exclude(status=Task.TASK_STATUS_DONE).exists()

    def resolve_relatives(self, _, **kwargs):
        try:
            relatives = list(map(lambda relative: relative.task_id, TaskDepend.objects.filter(depends_by=self.id)))

            return Task.objects.filter(pk__in=relatives)
        except Task.DoesNotExist:
            return None

    def resolve_status(self, _, **kwargs):
        return get_right_task_status(self.id, self)

    def resolve_link(self, _):
        return self.get_task_link(False)


class ProductTaskType(DjangoObjectType):
    class Meta:
        model = ProductTask
        convert_choices_to_enum = False


class TaskInput(graphene.InputObjectType):
    initiative = graphene.Int(required=False)
    capability = graphene.Int(required=False)
    title = graphene.String(required=True)
    short_description = graphene.String(required=False)
    description = graphene.String(required=True)
    status = graphene.Int(required=False)
    product_slug = graphene.String(required=True)
    tags = graphene.List(graphene.String, required=False)
    stacks = graphene.List(graphene.Int, required=False)
    depend_on = graphene.List(graphene.Int, required=False)
    reviewer = graphene.String(required=True)


class InitiativeType(DjangoObjectType):
    available_task_count = graphene.Int(source="get_available_tasks_count")
    completed_task_count = graphene.Int(source="get_completed_task_count")
    task_tags = graphene.List(lambda: TagType, source="get_task_tags")
    task_stacks = graphene.List(lambda: StackType, source="get_task_stacks")

    class Meta:
        model = Initiative
        convert_choices_to_enum = False


class InitiativeTaskType(graphene.ObjectType):
    initiative = graphene.Field(InitiativeType)
    tasks = graphene.List("api.work.types.TaskListingType")


class InitiativeInput(graphene.InputObjectType):
    name = graphene.String(
        description="Name of the initiative", required=True
    )
    product_slug = graphene.String(required=False)
    description = graphene.String(
        description="Description of the initiative", required=False
    )
    status = graphene.Int(
        description="Status of the initiative", required=False
    )


class ProductType(DjangoObjectType):
    available_task_num = graphene.Int()
    total_task_num = graphene.Int()
    owner = graphene.String()

    class Meta:
        model = Product

    def resolve_available_task_num(self, _):
        return Task.objects.filter(initiative__product=self, status=2).count()

    def resolve_total_task_num(self, _):
        if self is not None:
            return Task.objects.filter(
                Q(capability__product=self) | Q(initiative__product=self)
            ).count()
        return None

    def resolve_owner(self, _):
        return self.owner.get_username() if self.owner else None


class ProductInput(graphene.InputObjectType):
    slug = graphene.String(required=False)
    name = graphene.String(required=True)
    short_description = graphene.String(required=True)
    full_description = graphene.String(required=False)
    website = graphene.String(required=True)
    video_url = graphene.String(required=False)
    is_private = graphene.Boolean(required=False)


class BreadcrumbType(ObjectType):
    id = graphene.Int()
    name = graphene.String()


class BreadcrumbObject:
    def __init__(self, id, name):
        self.id = id
        self.name = name


def get_hitask(obj, hitask):
    if obj is not None:
        newObject = BreadcrumbObject(obj.id, obj.name)
        hitask.append(newObject)
        return get_hitask(obj.parent, hitask)
    return hitask


class AttachmentType(DjangoObjectType):
    class Meta:
        model = Attachment


class TagType(DjangoObjectType):
    class Meta:
        model = Tag


class StackType(DjangoObjectType):
    class Meta:
        model = Stack


class CapabilityType(DjangoObjectType):
    id = graphene.Int()
    product = graphene.Field(ProductType)
    stacks = graphene.List(StackType)
    tasks = graphene.List(TaskType)
    attachments = graphene.List(AttachmentType)

    class Meta:
        model = Capability

    def resolve_product(self, _):
        if self is not None:
            return Product.objects.get(capability_start_id=self.get_root().id)
        return None

    def resolve_stacks(self, _):
        return Stack.objects.filter(capabilitystack__capability=self.id)

    def resolve_tasks(self, _):
        if self is not None:
            return Task.objects.filter(capability=self)
        return None

    def resolve_attachments(self, _):
        return Attachment.objects.filter(capabilityattachment__capability=self)


class CapabilityTaskType(graphene.ObjectType):
    capability = graphene.Field(CapabilityType)
    tasks = graphene.List("api.work.types.TaskListingType")


class CapabilityInput(graphene.InputObjectType):
    node_id = graphene.Int(required=False)
    product_slug = graphene.String(required=False)
    name = graphene.String(required=True)
    description = graphene.String(required=True)
    stacks = graphene.List(graphene.Int, required=False)
    video_link = graphene.String(required=False)
    attachments = graphene.List(graphene.Int, required=False)


class CodeRepositoryType(DjangoObjectType):
    class Meta:
        model = CodeRepository


class CodeRepositoryInput(graphene.InputObjectType):
    product_slug = graphene.String(required=True)
    repository = graphene.String(required=False)
    access_token = graphene.String(required=True)


class AttachmentInput(graphene.InputObjectType):
    task_id = graphene.Int(required=False)
    capability_id = graphene.Int(required=False)
    name = graphene.String(required=False)
    path = graphene.String(required=True)
    file_type = graphene.String(required=False)


class InitiativeDictType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    status = graphene.Int()
    description = graphene.String()


class ProductDictType(graphene.ObjectType):
    name = graphene.String()
    slug = graphene.String()
    owner = graphene.String()


class PersonJSONData(graphene.ObjectType):
    username = graphene.String()
    full_name = graphene.String()


class TaskListingType(DjangoObjectType):
    id = graphene.Int()
    priority = graphene.String()
    in_review = graphene.Boolean()
    status = graphene.Int()
    initiative = graphene.Field(InitiativeDictType)
    product = graphene.Field(ProductDictType)
    tags = graphene.List(graphene.String)
    stacks = graphene.List(graphene.String)
    assigned_to = graphene.Field(PersonJSONData)
    reviewer = graphene.Field(PersonJSONData)

    class Meta:
        model = TaskListing
        convert_choices_to_enum = False

    def resolve_product(self, info):
        return self.product_data

    def resolve_priority(self, _):
        try:
            return Task.TASK_PRIORITY[self.priority][1]
        except:
            return None
