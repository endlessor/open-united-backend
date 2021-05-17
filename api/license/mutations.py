import graphene
from api.decorators import is_current_person
from api.license.inputs import LicenseInput
from api.utils import is_admin
from license.models import ContributorAgreement, ContributorAgreementAcceptance
from work.models import Product


class UpdateLicenseMutation(graphene.Mutation):
    class Arguments:
        license_input = LicenseInput(required=True)

    status = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    @is_current_person
    def mutate(current_person, info, *args, **kwargs):
        license_input = kwargs.get("license_input")
        if is_admin(user_id=current_person.id, product_slug=license_input.product_slug):
            ContributorAgreement.objects.create(
                product_id=Product.objects.get(slug=license_input.product_slug).id,
                agreement_content=license_input.content
            )

            return UpdateLicenseMutation(status=True, message="License has updated successfully")
        else:
            return UpdateLicenseMutation(status=False, message="You do not have permission for update license")


class AgreeLicenseMutation(graphene.Mutation):
    class Arguments:
        license_input = LicenseInput(required=True)

    status = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    @is_current_person
    def mutate(current_person, info, *args, **kwargs):
        license_input = kwargs.get("license_input")
        agreement = ContributorAgreement.objects.filter(product__slug=license_input.product_slug).last()
        if not agreement:
            return AgreeLicenseMutation(status=False, message="Agreement doesn't exist")

        contributor_data = dict(
            agreement_id=agreement.id,
            person_id=current_person.id
        )
        if not ContributorAgreementAcceptance.objects.filter(**contributor_data).exists():
            c_obj = ContributorAgreementAcceptance(**contributor_data)
            c_obj.save()

        return AgreeLicenseMutation(status=True, message="Agreement has accepted successfully")


class LicenseMutations(graphene.ObjectType):
    update_license = UpdateLicenseMutation.Field()
    agree_license = AgreeLicenseMutation.Field()
