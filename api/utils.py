from talent.models import AuthorizedUser, Person, ProductPerson


def logged_in_user():
    authorized_user = AuthorizedUser.objects.first()
    return authorized_user.user


def get_current_user(info, input):
    user = info.context.user
    if not user.is_anonymous:
        return user

    user_id = input.get("user_id", None)
    if user_id and user_id != 0:
        return Person.objects.get(id=user_id)
    else:
        return None


def get_current_person(info, input_data=None):
    user = info.context.user
    user_id = input_data.get("user_id", None) if input_data else None
    if user.is_anonymous and user_id and user_id != 0:
        return Person.objects.filter(id=user_id).first()

    if user.is_anonymous:
        return None

    try:
        return Person.objects.get(user=user)
    except Person.DoesNotExist:
        return None


def is_admin(user_id, product_slug):
    if ProductPerson.objects.filter(
            person_id=user_id,
            product__slug=product_slug,
            right__in=[ProductPerson.PERSON_TYPE_PRODUCT_ADMIN, ProductPerson.PERSON_TYPE_SUPER_ADMIN]
    ).count() > 0:
        return True
    else:
        return False


def is_admin_or_manager(person, product_slug):
    if ProductPerson.objects.filter(
            person=person,
            product__slug=product_slug,
            right__in=[
                ProductPerson.PERSON_TYPE_PRODUCT_ADMIN,
                ProductPerson.PERSON_TYPE_SUPER_ADMIN,
                ProductPerson.PERSON_TYPE_PRODUCT_MANAGER
            ]
    ).count() > 0:
        return True
    else:
        return False
