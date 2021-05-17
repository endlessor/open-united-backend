import graphene
from graphene_django.types import DjangoObjectType
from matching.models import TaskClaim, TaskClaimRequest


class TaskClaimType(DjangoObjectType):
    class Meta:
        model = TaskClaim
        convert_choices_to_enum = False


class TaskClaimInput(graphene.InputObjectType):
    id = graphene.Int(
        description="Product Id, which is used for product update",
        required=False
    )
    task = graphene.Int(
        description="Foreign key to Task", required=True
    )
    person = graphene.Int(
        description="Foreign key to Person", required=True
    )
    kind = graphene.Int(
        description="match type", required=True
    )


class TaskClaimRequestType(DjangoObjectType):
    class Meta:
        model = TaskClaimRequest
        convert_choices_to_enum = False