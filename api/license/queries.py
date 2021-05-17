import graphene
from graphene import ObjectType
from api.license.types import LicenseType
from license.models import ContributorAgreement


class LicenseQuery(ObjectType):
    license = graphene.Field(LicenseType, product_slug=graphene.String())

    @staticmethod
    def resolve_license(*args, product_slug):
        try:
            return ContributorAgreement.objects.filter(product__slug=product_slug).last()
        except ContributorAgreement.DoesNotExist:
            return None
