from graphene_django import DjangoObjectType
from license.models import ContributorAgreement


class LicenseType(DjangoObjectType):
    class Meta:
        model = ContributorAgreement
