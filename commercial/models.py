from django.db import models
from django.core.exceptions import ValidationError
from talent.models import Person, ProductPerson
from users.models import Username
from work.models import Product
from backend.mixins import TimeStampMixin, UUIDMixin


class Organisation(TimeStampMixin, UUIDMixin, Username):
    name = models.CharField(max_length=512, unique=True)
    photo = models.ImageField(upload_to='avatars/', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Organisations"

    def __str__(self):
        return self.name


class Partner(TimeStampMixin, UUIDMixin):
    PersonType = (
        (0, "NONE"),
        (1, "CREATOR"),
        (2, "SERVICES"),
        (3, "SUPPORTER")
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    person = models.IntegerField(choices=PersonType, default=0)

    def __str__(self):
        return '{} is {} of {}'.format(self.organisation, self.person, self.product)


class OrganisationPerson(TimeStampMixin, UUIDMixin):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    right = models.IntegerField(choices=ProductPerson.PERSON_TYPE, default=0)

    def __str__(self):
        return '{} is {} of {}'.format(self.person, self.right, self.organisation)


class ProductOwner(TimeStampMixin, UUIDMixin):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, blank=True, null=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"Person: {self.person.full_name}" if self.person else f"Organization: {self.organisation.name}"

    def clean(self):
        if not self.organisation and not self.person:
            raise ValidationError("Please select person or organisation")

    def get_username(self):
        try:
            return getattr(self.person, "username")
        except AttributeError:
            return getattr(self.organisation, "username")
        except BaseException:
            return ""

    @classmethod
    def get_or_create(cls, person):
        try:
            return cls.objects.get(person=person)
        except cls.DoesNotExist:
            obj = cls.objects.create(person=person)
            return obj


class CustomerAccount(TimeStampMixin, UUIDMixin):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, blank=True, null=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True)


class Plan(TimeStampMixin, UUIDMixin):
    name = models.CharField(max_length=60)
    value = models.CharField(max_length=60)
    customer_account = models.ForeignKey(CustomerAccount, on_delete=models.CASCADE)

    def __str__(self):
        return 'Name: {}, Value: {}'.format(self.name, self.value)
