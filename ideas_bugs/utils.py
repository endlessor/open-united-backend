from django.template.loader import render_to_string
from backend.utils import send_email


def save_history(created, instance, parent_type):
    from ideas_bugs.models import REJECTED_STATUS

    if created:
        parent = getattr(instance, parent_type, None)
        parent.status = instance.current_status
        parent.save()

        if instance.current_status == REJECTED_STATUS:

            to_email = instance.person.email_address
            email_content = {
                "title": parent.headline,
                "link": parent.get_ui_link(),
                "product": parent.product.name,
                "description": instance.description
            }
            # Send email to creator
            content = render_to_string(f"email/{parent_type}_rejected.html", email_content)

            send_email(
                to_emails=to_email,
                subject=f"The {parent_type} was rejected",
                content=content
            )


def save_idea_or_bug(created, instance, instance_type):
    if created:
        product_name = instance.product.name
        to_email = instance.person.email_address
        email_content = {
            "title": instance.headline,
            "link": instance.get_ui_link(),
            "product": product_name
        }
        # Send email to creator
        content = render_to_string(f"email/{instance_type}_created_for_sender.html", email_content)

        send_email(
            to_emails=to_email,
            subject=f"New {instance_type} successfully created",
            content=content
        )

        # Send email to product members
        content = render_to_string(f"email/{instance_type}_created_for_product_members.html", email_content)

        send_email(
            to_emails=instance.product.get_members_emails(),
            subject=f"New {instance_type} for {product_name} was created",
            content=content
        )
