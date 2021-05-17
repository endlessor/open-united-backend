import graphene
from graphene_django.types import DjangoObjectType, ObjectType

from matching.models import CLAIM_TYPE_ACTIVE
from talent.models import Person, ProductPerson, PersonProfile, Review, PersonSocial


class PersonSocialType(DjangoObjectType):
    class Meta:
        model = PersonSocial


class PersonType(DjangoObjectType):
    photo = graphene.String(required=False)
    slug = graphene.String()
    claimed_task = graphene.Field("api.work.types.TaskType")

    class Meta:
        model = Person

    def resolve_photo(self, info):
        """Resolve product image absolute path"""
        if self.photo:
            return info.context.build_absolute_uri(self.photo.url)
        return None

    def resolve_slug(self, info):
        return self.username

    def resolve_claimed_task(self, info):
        claimed_task = self.taskclaim_set.filter(kind=CLAIM_TYPE_ACTIVE).last()
        return claimed_task.task if claimed_task else None


class PersonInput(graphene.InputObjectType):
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    email_address = graphene.String(required=True)
    password = graphene.String(required=True)
    password_2 = graphene.String(required=True)

    def get_slug(self):
        return f'{str(self.first_name).lower()}-{str(self.last_name).lower()}'


class ProductPersonType(DjangoObjectType):
    class Meta:
        model = ProductPerson
        convert_choices_to_enum = False


class ProductPersonsType(graphene.ObjectType):
    product_team = graphene.List(PersonType)
    contributors = graphene.List(PersonType)


class PersonProfileType(DjangoObjectType):
    class Meta:
        model = PersonProfile


class ReviewType(DjangoObjectType):
    class Meta:
        model = Review


class ReviewInput(graphene.InputObjectType):
    person_id = graphene.Int(
        description="User Id",
        required=True
    )


class ProductReviewType(ObjectType):
    product_reviews = graphene.List(ReviewType)
    review = graphene.Field(ReviewType)
