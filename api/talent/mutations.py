import graphene
from .forms import CreatePersonForm
from .types import PersonInput
from talent.models import Person
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class CreatePersonMutation(graphene.Mutation):
    class Arguments:
        person_input = PersonInput(required=True)

    status = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(*args, **kwargs):
        person_input = kwargs.get('person_input')
        form = CreatePersonForm(person_input)
        try:
            if form.is_valid():
                is_exists_person_by_email = Person.objects.filter(email_address=person_input.email_address).exists()
                is_exists_user_by_email = User.objects.filter(email=person_input.email_address).exists()

                if is_exists_person_by_email or is_exists_user_by_email:
                    return CreatePersonMutation(status=False, message='User already exists')
                else:
                    CreatePersonMutation.sign_up(person_input, slug_increment=0)

                    return CreatePersonMutation(status=True, message='Successfully signed up')
            else:
                return CreatePersonMutation(status=False, message=form.non_field_errors().as_text())
        except Exception as e:
            print(e)
            return CreatePersonMutation(status=False, message='Unknown error')

    @staticmethod
    def sign_up(person_input, slug_increment):
        available_slug = CreatePersonMutation.get_available_slug(person_input, slug_increment)
        is_exists_person_by_slug = Person.objects.filter(slug=available_slug).exists()
        is_exists_user_by_slug = User.objects.filter(username=available_slug).exists()

        if is_exists_person_by_slug or is_exists_user_by_slug:
            CreatePersonMutation.sign_up(person_input, slug_increment + 1)
        else:
            user = User.objects.create_user(
                username=available_slug,
                email=person_input.email_address,
                password=person_input.password
            )

            person = Person(
                full_name=f'{person_input.first_name} {person_input.last_name}',
                email_address=person_input.email_address,
                slug=available_slug,
                user=user
            )
            person.save()

    @staticmethod
    def get_available_slug(person_input, slug_increment):
        return person_input.get_slug() + ('' if slug_increment == 0 else f'-{slug_increment}')


class SignInPersonMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    status = graphene.Boolean()

    @staticmethod
    def mutate(*args, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')

        try:
            user = authenticate(email=email, password=password)
            if user is not None:
                return SignInPersonMutation(status=True)
            else:
                return SignInPersonMutation(status=False)
        except Exception as e:
            print(e)
            return CreatePersonMutation(status=False, message='Unknown error')
