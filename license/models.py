from django.db import models
from backend.mixins import TimeStampMixin


class ContributorAgreement(models.Model):
    product = models.ForeignKey(to='work.Product', on_delete=models.CASCADE)
    agreement_content = models.TextField()

    class Meta:
        db_table = 'license_contributor_agreement'


class ContributorAgreementAcceptance(models.Model):
    agreement = models.ForeignKey(to=ContributorAgreement, on_delete=models.CASCADE)
    person = models.ForeignKey(to='talent.Person', on_delete=models.CASCADE)
    accepted_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'license_contributor_agreement_acceptance'
