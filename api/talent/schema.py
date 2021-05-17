import json
import graphene
from django.db.models import Count, Q
from graphene_django.types import DjangoObjectType, ObjectType

from talent.models import Person, ProductPerson, PersonProfile, Review, PersonSocial
from .types import *
from work.models import CodeRepository
from api.work.types import CodeRepositoryType
from .mutations import CreatePersonMutation, SignInPersonMutation
from ..decorators import is_current_person


class PersonQuery(ObjectType):
    people = graphene.List(PersonType,
                           hide_test_users=graphene.Boolean(),
                           show_only_test_users=graphene.Boolean())
    person = graphene.Field(PersonType, id=graphene.Int())

    def resolve_person(self, info, **kwargs):
        id = kwargs.get('id')

        if not id:
            try:
                user = info.context.user

                if user.is_authenticated:
                    return Person.objects.filter(user=info.context.user).first()
                else:
                    return None
            except Person.DoesNotExist:
                return None

        if id is not None:
            return Person.objects.get(pk=id)

        return None

    def resolve_people(self, info, hide_test_users=False, show_only_test_users=False):
        filter_data = dict()
        if hide_test_users:
            filter_data["test_user"] = False
        if show_only_test_users:
            filter_data["test_user"] = True
        return Person.objects.filter(**filter_data).all()


class ProductPersonQuery(ObjectType):
    product_persons = graphene.Field(ProductPersonsType, product_slug=graphene.String())
    product_person = graphene.Field(ProductPersonType, id=graphene.Int())
    repositories = graphene.List(CodeRepositoryType, product_slug=graphene.String())

    def resolve_product_person(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return ProductPerson.objects.get(pk=id)

        return None

    @staticmethod
    def resolve_product_persons(info, *args, **kwargs):
        product_slug = kwargs.get("product_slug")
        contributor_rights = [ProductPerson.PERSON_TYPE_USER, ProductPerson.PERSON_TYPE_CONTRIBUTOR]
        if product_slug:
            product_team_persons = ProductPerson.objects\
                .filter(product__slug=product_slug)\
                .exclude(right__in=contributor_rights)\
                .distinct()\
                .values_list("person", flat=True)

            product_team = Person.objects.filter(pk__in=product_team_persons).all()

            contributors_persons = ProductPerson.objects \
                .annotate(finished_tasks=Count("person", filter=Q(person__taskclaim__kind=0)))\
                .filter(product__slug=product_slug, right__in=contributor_rights)\
                .order_by("-finished_tasks") \
                .distinct() \
                .values_list("person", flat=True)
            contributors = Person.objects.filter(pk__in=contributors_persons).all()

            return ProductPersonsType(product_team=product_team, contributors=contributors)
        else:
            return None

    def resolve_repositories(self, info, **kwargs):
        product_slug = kwargs.get("product_slug")
        if product_slug:
            qs = CodeRepository.objects.filter(product__slug=product_slug)
            return qs

        return CodeRepository.objects.all()


class ReviewQuery(ObjectType):
    reviews = graphene.List(ReviewType, person_slug=graphene.String())
    review = graphene.Field(ProductReviewType,
                            id=graphene.Int(),
                            person_slug=graphene.String())

    def resolve_review(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            review = Review.objects.get(pk=id)
            reviews = Review.objects.filter(product=review.product)

            obj = ProductReviewType()
            obj.review = review
            obj.product_reviews = reviews
            return obj

        return None

    def resolve_reviews(self, info, query=None, **kwargs):
        person_slug = kwargs.get('person_slug')
        if person_slug is not None:
            qs = Review.objects.filter(person__slug=person_slug).distinct('product')
            return qs
        return None


class PersonProfileQuery(ObjectType):
    person_profile = graphene.Field(PersonProfileType, person_slug=graphene.String())
    person_profiles = graphene.List(PersonProfileType, person_slug=graphene.String())

    def resolve_person_profile(self, info, **kwargs):
        try:
            person_slug = kwargs.get('person_slug')
            if person_slug is not None:
                return PersonProfile.objects.filter(person__username=person_slug).first()
            return None
        except:
            pass
        return None

    def resolve_person_profiles(self, info, query=None, **kwargs):
        person_slug = kwargs.get('person_slug')
        if person_slug is not None:
            qs = PersonProfile.objects.filter(person__username=person_slug)
            return qs
        return None


class PersonSocialQuery(ObjectType):
    person_socials = graphene.List(PersonSocialType, person_id=graphene.Int())

    @staticmethod
    def resolve_person_socials(self, info, **kwargs):
        person_id = kwargs.get('person_id')

        if person_id is not None:
            return PersonSocial.objects.filter(person_id=person_id)

        return None


class TalentMutations(graphene.ObjectType):
    create_person = CreatePersonMutation.Field()
    sign_in_person = SignInPersonMutation.Field()
