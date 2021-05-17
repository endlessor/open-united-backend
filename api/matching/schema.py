import json
import graphene
from graphene_django.types import DjangoObjectType, ObjectType

from matching.models import TaskClaim, TaskClaimRequest
from .types import TaskClaimType, TaskClaimRequestType
from .mutations import CreateTaskClaimMutation


class TaskClaimQuery(ObjectType):
    matches = graphene.List(TaskClaimType)
    match = graphene.Field(TaskClaimType, id=graphene.Int())

    def resolve_match(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return TaskClaim.objects.get(pk=id)

        return None

    def resolve_matches(self, info, query=None, **kwargs):
        qs = TaskClaim.objects.all()
        return qs


class TaskClaimRequestQuery(ObjectType):
    matches = graphene.List(TaskClaimRequestType)
    match = graphene.Field(TaskClaimRequestType, id=graphene.Int())

    def resolve_match(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return TaskClaimRequest.objects.get(pk=id)

        return None

    def resolve_matches(self, info, query=None, **kwargs):
        qs = TaskClaimRequest.objects.all()
        return qs


class TaskClaimMutations(graphene.ObjectType):
    create_match = CreateTaskClaimMutation.Field()

