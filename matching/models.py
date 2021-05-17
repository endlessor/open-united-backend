from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from model_utils import FieldTracker
from notifications.signals import notify

from backend.utils import send_email
from work.models import Task
from talent.models import Person
from backend.mixins import TimeStampMixin, UUIDMixin

CLAIM_TYPE_DONE = 0
CLAIM_TYPE_ACTIVE = 1
CLAIM_TYPE_FAILED = 2


class TaskClaim(TimeStampMixin, UUIDMixin):
    CLAIM_TYPE = (
        (CLAIM_TYPE_DONE, "Done"),
        (CLAIM_TYPE_ACTIVE, "Active"),
        (CLAIM_TYPE_FAILED, "Failed")
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True)
    kind = models.IntegerField(choices=CLAIM_TYPE, default=0)
    tracker = FieldTracker()


@receiver(post_save, sender=TaskClaim)
def save_task_claim_second(sender, instance, **kwargs):
    task = Task.objects.get(pk=instance.task_id)
    if task.status == 3:
        try:
            send_email(
                to_emails=[Person.objects.get(pk=instance.person_id).email_address],
                subject='New assigning',
                content=f"""
                    You assigned to {task.title} task
                    You can see the task here: {task.get_task_link()}
                """
            )
        except BaseException:
            print("Can't send email to users, please check SMTP configuration")


@receiver(post_save, sender=TaskClaim)
def save_task_claim(sender, instance, created, **kwargs):
    if not created and (instance.kind == CLAIM_TYPE_DONE and instance.tracker.previous("kind") is not CLAIM_TYPE_DONE):
        admin_users = User.objects.filter(is_superuser=True).all()
        task = instance.task
        subject = f"The task \"{task.title}\" is ready to review"
        message = f"You can see the task here: {task.get_task_link()}"
        notify.send(instance, recipient=admin_users, verb=subject, description=message)
        try:
            send_email(
                to_emails=admin_users.values_list("email", flat=True),
                subject=subject,
                content=message
            )
        except BaseException:
            print("Can't send email to users, please check SMTP configuration")


class TaskClaimRequest(TimeStampMixin):
    CLAIM_REQUEST_TYPE = (
        (0, "New"),
        (1, "Approved"),
        (2, "Rejected"),
    )
    kind = models.IntegerField(choices=CLAIM_REQUEST_TYPE, default=0)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=True, null=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True)
    is_canceled = models.BooleanField(default=False)
