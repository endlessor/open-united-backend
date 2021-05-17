from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from backend.mixins import TimeStampMixin, UUIDMixin
from users.models import Username


class Person(TimeStampMixin, UUIDMixin, Username):
    full_name = models.CharField(max_length=60)
    email_address = models.EmailField(null=True, blank=True)
    photo = models.ImageField(upload_to='avatars/', null=True, blank=True)
    github_username = models.CharField(max_length=30)
    git_access_token = models.CharField(max_length=60, null=True, blank=True)
    slug = models.SlugField(unique=True)
    headline = models.TextField()
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, default=1)
    test_user = models.BooleanField(default=False, blank=True)

    class Meta:
        verbose_name_plural = 'People'

    def __str__(self):
        return self.full_name


@receiver(post_save, sender=Person)
def save_bug(sender, instance, created, **kwargs):
    if created:
        PersonProfile.objects.create(person=instance)


class ProductPerson(TimeStampMixin, UUIDMixin):
    PERSON_TYPE_USER = 0
    PERSON_TYPE_PRODUCT_ADMIN = 1
    PERSON_TYPE_PRODUCT_MANAGER = 2
    PERSON_TYPE_CONTRIBUTOR = 3
    PERSON_TYPE_SUPER_ADMIN = 4

    PERSON_TYPE = (
        (PERSON_TYPE_USER, "User"),
        (PERSON_TYPE_PRODUCT_ADMIN, "Product Admin"),
        (PERSON_TYPE_PRODUCT_MANAGER, "Product Manager"),
        (PERSON_TYPE_CONTRIBUTOR, "Contributor"),
        (PERSON_TYPE_SUPER_ADMIN, "Super Admin")
    )
    product = models.ForeignKey('work.Product', on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    right = models.IntegerField(choices=PERSON_TYPE, default=0)

    def __str__(self):
        return '{} is {} of {}'.format(self.person.full_name, self.right, self.product)


class Review(TimeStampMixin, UUIDMixin):
    product = models.ForeignKey('work.Product', on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    initiative = models.ForeignKey('work.Initiative', on_delete=models.CASCADE, null=True, blank=True)
    score = models.DecimalField(decimal_places=2, max_digits=3)
    text = models.TextField()
    created_by = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True, related_name="given")


class PersonProfile(TimeStampMixin, UUIDMixin):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True)
    overview = models.TextField()


class PersonSocial(TimeStampMixin, UUIDMixin):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=255)


class AuthorizedUser(models.Model):
    user = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True)

    @property
    def is_authenticated(self):
        return bool(self.user)


class SocialAccount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    provider = models.CharField(verbose_name=_('provider'), max_length=30)

    uid = models.CharField(verbose_name=_('uid'), max_length=settings.UID_MAX_LENGTH)
    last_login = models.DateTimeField(verbose_name=_('last login'),
                                      auto_now=True,
                                      blank=True)
    date_joined = models.DateTimeField(verbose_name=_('date joined'),
                                       auto_now_add=True,
                                       blank=True)
    extra_data = models.JSONField(verbose_name=_('extra data'), default=dict)

    class Meta:
        unique_together = ('provider', 'uid')
