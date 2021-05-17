import graphene

from backend.utils import send_email
from .types import TaskClaimInput, TaskClaimType
from matching.models import TaskClaim
from work.models import Task
from talent.models import Person


class CreateTaskClaimMutation(graphene.Mutation):
    class Arguments:
        input = TaskClaimInput(
            required=True,
            description=("Fields required to create a product"),
        )

    match = graphene.Field(TaskClaimType)
    status = graphene.Boolean()

    @staticmethod
    def mutate(*args, **kwargs):
        input = kwargs.get('input')
        status = False
        match = None

        try:
            task = Task.objects.get(id=input.task)
            person = Person.objects.get(id=input.person)
            match = TaskClaim(task=task, person=person, kind=input.kind)
            match.save()
            status = True

            if task.reviewer:
                send_email(
                    to_emails=Person.objects.get(pk=task.reviewer.id).email_address,
                    subject='Task has been submitted',
                    content=f"""
                        The task {task.title} has been submitted by {person.full_name}.
                        You can see the task here: {task.get_task_link()}
                    """
                )
        except:
            pass

        return CreateTaskClaimMutation(match=match, status=status)
