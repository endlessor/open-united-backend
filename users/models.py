from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from polymorphic.models import PolymorphicModel

from backend.mixins import TimeStampMixin, UUIDMixin
from commercial.validators import validate_reserved_words


# class User(AbstractUser, PolymorphicModel):
#     username = models.CharField(max_length=39,
#                                 unique=True,
#                                 validators=[
#                                     RegexValidator(
#                                         regex="^(?!-)(?!.*--)[a-zA-Z\d)-]+(?<!-)$",
#                                         message="Username may only contain alphanumeric characters or hyphens & cannot "
#                                                 "have multiple consecutive hyphens & cannot begin or end with a hyphen",
#                                         code="invalid_username"
#                                     ),
#                                     validate_reserved_words
#                                 ])
#
#     class Meta:
#         db_table = 'auth_user'

class Username(PolymorphicModel):
    username = models.CharField(max_length=39,
                                unique=True,
                                validators=[
                                    RegexValidator(
                                        regex="^(?!-)(?!.*--)[a-zA-Z\d)-]+(?<!-)$",
                                        message="Username may only contain alphanumeric characters or hyphens & cannot "
                                                "have multiple consecutive hyphens & cannot begin or end with a hyphen",
                                        code="invalid_username"
                                    ),
                                    validate_reserved_words
                                ])
    # organisation = models.OneToOneField(Organisation, on_delete=models.CASCADE, blank=True, null=True)
    # person = models.OneToOneField(Person, on_delete=models.CASCADE, blank=True, null=True)
    #
    # def __str__(self):
    #     title = f"Person: {self.person.full_name}" if self.person else f"Organization: {self.organisation.name}" \
    #         if self.person or self.organisation else ""
    #     return f"Username: {self.username}, {title}"
    #
    # def clean(self):
    #     if not self.organisation and not self.person:
    #         raise ValidationError("Please select person or organisation")
    #
    #     if self.organisation and self.person:
    #         raise ValidationError("You can't select person and organization, please select only one type")