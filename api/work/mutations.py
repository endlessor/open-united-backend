from graphene_file_upload.scalars import Upload

from commercial.models import ProductOwner
from license.models import ContributorAgreement, ContributorAgreementAcceptance
from matching.models import TaskClaimRequest, TaskClaim, CLAIM_TYPE_ACTIVE, CLAIM_TYPE_FAILED
from .types import *
from work.models import *
from talent.models import ProductPerson, Person
from git.views import create_webhook
from api.utils import is_admin_or_manager, is_admin
from api.mutations import InfoStatusMutation
from .utils import set_depends
from api.decorators import is_current_person
from ..images.utils import upload_photo
from ..types import InfoType


class CreateProductMutation(graphene.Mutation, InfoType):
    class Arguments:
        file = Upload(required=False)
        product_input = ProductInput(required=True)

    @staticmethod
    @is_current_person
    def mutate(current_person, info, *args, product_input, file=None):
        # try:
        url = None

        if file:
            url = upload_photo(file, 'products')

        products = Product.objects.filter(name=product_input.name).count()

        if products > 0:
            return CreateProductMutation(status=False, message='Product name already exits')

        product_owner = ProductOwner.get_or_create(current_person)

        new_product = Product.objects.create(
            photo=url,
            name=product_input.name,
            short_description=product_input.short_description,
            full_description=product_input.full_description,
            website=product_input.website,
            video_url=product_input.get('video_url', None),
            is_private=product_input.get('is_private', False),
            owner=product_owner
        )

        current_headline = current_person.headline
        current_person.headline = f'{current_headline}, Admin - {product_input.name}' if len(
            current_headline) > 0 else f'Admin - {product_input.name}'
        current_person.save()

        new_product_person = ProductPerson(
            person=current_person,
            product=new_product,
            right=ProductPerson.PERSON_TYPE_PRODUCT_ADMIN
        )
        new_product_person.save()

        return CreateProductMutation(status=True, message='Product successfully created')
        # except:
        #     return CreateProductMutation(status=False, message='Error with product creation')


class UpdateProductMutation(graphene.Mutation, InfoType):
    class Arguments:
        file = Upload(required=False)
        product_input = ProductInput(required=True)

    new_slug = graphene.String()

    @staticmethod
    @is_current_person
    def mutate(current_person, info, *args, product_input, file=None):
        try:
            if is_admin(current_person.id, product_input.slug):
                product = Product.objects.get(slug=product_input.slug)

                product.photo = upload_photo(file, 'products')
                product.name = product_input.name
                product.short_description = product_input.short_description
                product.full_description = product_input.full_description
                product.website = product_input.website
                product.video_url = product_input.get('video_url', None)
                product.is_private = product_input.get('is_private', False)
                product.save()

                return UpdateProductMutation(new_slug=product.slug, status=True, message='Product successfully updated')
            else:
                return UpdateProductMutation(
                    new_slug=None, status=False, message="You don't have permission for update that product"
                )
        except:
            return UpdateProductMutation(new_slug=None, status=False, message='Error with product updating')


class DeleteProductMutation(graphene.Mutation, InfoType):
    class Arguments:
        slug = graphene.String(required=True)

    @staticmethod
    @is_current_person
    def mutate(current_person, info, *args, slug):
        try:
            product = Product.objects.get(slug=slug)

            if is_admin(current_person.id, slug):
                product.delete()

                return DeleteProductMutation(status=True, message='Product successfully deleted')
            else:
                return DeleteProductMutation(status=False, message="You don't have permission for delete that product")
        except:
            return DeleteProductMutation(status=False, message='Error with product deletion')


class CreateCapabilityMutation(graphene.Mutation):
    class Arguments:
        input = CapabilityInput(required=True)

    status = graphene.Boolean()
    capability = graphene.Field(CapabilityType)

    @staticmethod
    def mutate(*args, **kwargs):
        try:
            arguments = kwargs.get('input')

            if arguments.node_id is None:
                node_id = Product.objects.get(slug=arguments.product_slug).capability_start_id

                if not node_id:
                    updated_product = Product.objects.get(slug=arguments.product_slug)
                    new_root = Capability.add_root(name=updated_product.name)
                    updated_product.capability_start_id = new_root.id
                    updated_product.save()

                    node_id = updated_product.capability_start_id

                parent_node = Capability.objects.get(pk=node_id)
            else:
                parent_node = Capability.objects.get(pk=arguments.node_id)

            new_node = parent_node.add_child(
                name=arguments.name,
                description=arguments.description,
                video_link=(arguments.video_link if arguments.video_link is not None else '')
            )

            if arguments.stacks is not None:
                for stack_id in arguments.stacks:
                    new_capability_stack = CapabilityStack(
                        capability=Capability(new_node).id, stack=Stack(stack_id)
                    )
                    new_capability_stack.save()

            if arguments.attachments is not None:
                for attachment_id in arguments.attachments:
                    new_capability_attachment = CapabilityAttachment(
                        capability=Capability(new_node).id, attachment=Attachment(attachment_id)
                    )
                    new_capability_attachment.save()

            return CreateCapabilityMutation(status=True, capability=new_node)
        except Exception as e:
            print(e)
            CreateCapabilityMutation(status=False, capability=None)


class DeleteCapabilityMutation(graphene.Mutation):
    class Arguments:
        node_id = graphene.Int(required=True)

    status = graphene.Boolean()
    capability_id = graphene.Int()

    @staticmethod
    def mutate(self, info, **kwargs):
        node_id = kwargs.get('node_id')

        try:
            capability = Capability.objects.get(pk=node_id)
            capability.delete()

            return DeleteCapabilityMutation(status=True, capability_id=node_id)
        except Exception as e:
            print(e)
            return DeleteCapabilityMutation(status=False)


class UpdateCapabilityMutation(graphene.Mutation):
    class Arguments:
        input = CapabilityInput(required=True)

    status = graphene.Boolean()
    capability = graphene.Field(CapabilityType)

    @staticmethod
    def mutate(self, info, **kwargs):
        arguments = kwargs.get('input')

        try:
            capability = Capability.objects.get(pk=arguments.node_id)

            if arguments.product_slug is not None:
                product = Product.objects.get(slug=arguments.product_slug)
                capability.product_id = product.id

            if arguments.name is not None:
                capability.name = arguments.name

            if arguments.description is not None:
                capability.description = arguments.description

            if arguments.stacks is not None:
                stacks = CapabilityStack.objects.filter(capability_id=arguments.node_id)
                stacks.delete()

                for stack_id in arguments.stacks:
                    new_capability_stack = CapabilityStack(
                        capability_id=arguments.node_id, stack=Stack(stack_id)
                    )
                    new_capability_stack.save()

            if arguments.video_link is not None:
                capability.video_link = arguments.video_link

            capability.save()

            return UpdateCapabilityMutation(status=True, capability=capability)
        except Exception as e:
            print(e)
            return UpdateCapabilityMutation(status=False, capability=None)


class UpdateCapabilityTreeMutation(graphene.Mutation):
    class Arguments:
        product_slug = graphene.String(required=True)
        tree = graphene.JSONString(required=True)

    status = graphene.Boolean()

    @staticmethod
    def transform_tree_item(tree_item):
        tree_item = list(map(lambda tree_node: {
            'id': tree_node['id'],
            'data': {
                'name': tree_node['title'],
                'description': tree_node['description'],
                'video_link': tree_node['videoLink']
            },
            'children': UpdateCapabilityTreeMutation.transform_tree_item(tree_node['children'])
        }, tree_item))

        return tree_item

    @staticmethod
    def mutate(*args, **kwargs):
        product_slug = kwargs.get('product_slug')
        tree = kwargs.get('tree')

        tree = UpdateCapabilityTreeMutation.transform_tree_item(tree)

        node_id = Product.objects.get(slug=product_slug).capability_start_id

        Capability.load_bulk(tree, parent=Capability.objects.get(pk=node_id), keep_ids=True)

        return UpdateCapabilityTreeMutation(status=True)


class CreateInitiativeMutation(graphene.Mutation):
    class Arguments:
        input = InitiativeInput(
            required=True,
            description=("Fields required to create a initiative"),
        )

    initiative = graphene.Field(InitiativeType)

    def mutate(cls, instance, input):
        try:
            product = Product.objects.get(slug=input.product_slug)
        except:
            product = None

        initiative = Initiative(name=input.name,
                                product=product,
                                description=input.description)
        if input.status is not None:
            initiative.status = input.status

        initiative.save()

        return CreateInitiativeMutation(initiative=initiative)


class UpdateInitiativeMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = InitiativeInput(required=True)

    status = graphene.Boolean()
    initiative = graphene.Field(InitiativeType)

    @staticmethod
    def mutate(root, info, id, input=None):
        status = False
        try:
            product = Product.objects.get(slug=input.product_slug)

            initiative = Initiative.objects.get(pk=id)
            initiative.name = input.name
            initiative.product = product
            if input.description is not None:
                initiative.description = input.description
            if input.status is not None:
                initiative.status = input.status
            initiative.save()
            status = True
            return UpdateInitiativeMutation(status=status, initiative=initiative)
        except:
            pass
        return UpdateInitiativeMutation(status=status, initiative=None)


class DeleteInitiativeMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    status = graphene.Boolean()
    initiative_id = graphene.Int()

    @staticmethod
    def mutate(root, info, id, input=None):
        status = False
        try:
            initiative = Initiative.objects.get(pk=id)
            initiative.delete()
            status = True
            return DeleteInitiativeMutation(status=status, initiative_id=id)
        except:
            pass
        return DeleteInitiativeMutation(status=status)


class CreateTaskMutation(graphene.Mutation, InfoType):
    class Arguments:
        input = TaskInput(required=True)

    task = graphene.Field(TaskType)

    @staticmethod
    @is_current_person
    def mutate(current_person, info, *args, **kwargs):
        product_input = kwargs.get("input")
        product_slug = product_input.get("product_slug", None)

        try:
            product = Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            return CreateTaskMutation(task=None, status=False, message="Product doesn't exist")

        if not is_admin_or_manager(current_person, product_slug):
            return CreateTaskMutation(task=None, status=False, message="You don't have permissions")

        try:
            initiative = Initiative.objects.get(pk=product_input.initiative)
        except:
            initiative = None

        try:
            capability = Capability.objects.get(pk=product_input.capability)
        except:
            capability = None

        status = int(product_input.status) if product_input.status else 0

        try:
            task = Task(
                initiative=initiative,
                capability=capability,
                title=product_input.title,
                description=product_input.description,
                status=status,
                created_by=current_person,
                updated_by=current_person,
                reviewer=Person.objects.get(username=product_input.reviewer),
                product=product
            )
        except Person.DoesNotExist:
            raise Exception('Reviewer is a required field')

        if product_input.short_description is not None:
            task.short_description = product_input.short_description
        task.save()

        set_depends(product_input.depend_on, task.id)

        for tag in product_input.tags:
            if Tag.objects.filter(name=tag).count() <= 0:
                Tag.objects.create(name=tag)

            task.tag.add(Tag.objects.get(name=tag))

        if product_input.stacks is not None:
            task.stack.clear()
            for stack in product_input.stacks:
                task.stack.add(Stack.objects.get(id=int(stack)))

        if product_slug:
            task.producttask_set.create(product=Product.objects.get(slug=product_slug))

        return CreateTaskMutation(task=task, status=True, message="Task has been created successfully")


class UpdateTaskMutation(graphene.Mutation, InfoType):
    class Arguments:
        id = graphene.Int(required=True)
        input = TaskInput(required=True)

    task = graphene.Field(TaskType)

    @staticmethod
    @is_current_person
    def mutate(current_person, info, *args, **kwargs):
        try:
            id = kwargs.get("id")
            person_input = kwargs.get("input")
            product_slug = person_input.get("product_slug", None)

            if not is_admin_or_manager(current_person, product_slug):
                return UpdateTaskMutation(task=None, status=False, message="You don't have permissions")

            try:
                initiative = Initiative.objects.get(pk=person_input.initiative)
            except Initiative.DoesNotExist:
                initiative = None

            try:
                capability = Capability.objects.get(pk=person_input.capability)
            except Capability.DoesNotExist:
                capability = None

            task = Task.objects.get(pk=id)

            if person_input.status is not None:
                if int(person_input.status) == Task.TASK_STATUS_CLAIMED and task.taskclaim_set.filter(
                        kind__in=[0, 1]
                ).count() <= 0:
                    return UpdateTaskMutation(
                        task=None, status=False,
                        message='You cannot change status to claimed because the task is not assigned'
                    )

                if int(person_input.status) in [
                    Task.TASK_STATUS_DRAFT, Task.TASK_STATUS_BLOCKED, Task.TASK_STATUS_AVAILABLE
                ] and task.taskclaim_set.filter(kind__in=[0, 1]).count() > 0:
                    return UpdateTaskMutation(
                        task=None, status=False,
                        message='You cannot change status to that because task is claimed'
                    )
                else:
                    status = int(person_input.status)
            else:
                status = Task.TASK_STATUS_DRAFT

            task.initiative = initiative
            task.capability = capability
            task.title = person_input.title
            task.description = person_input.description
            task.status = status

            try:
                task.reviewer = Person.objects.get(username=person_input.reviewer)
            except Person.DoesNotExist:
                raise Exception('Reviewer is a required field')

            task.updated_by = current_person

            set_depends(depends=person_input.depend_on, task_id=id)

            if person_input.tags is not None:
                task.tag.clear()

                for tag in person_input.tags:
                    if Tag.objects.filter(name=tag).count() <= 0:
                        Tag.objects.create(name=tag)

                    task.tag.add(Tag.objects.get(name=tag))

            if person_input.stacks is not None:
                task.stack.clear()
                for stack in person_input.stacks:
                    task.stack.add(Stack.objects.get(id=int(stack)))

            if person_input.short_description is not None:
                task.short_description = person_input.short_description

            task.save()
            return UpdateTaskMutation(task=None, status=True, message='Task has been updated successfully')
        except:
            return UpdateTaskMutation(task=None, status=False, message='Error with task updating')


class DeleteTaskMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    status = graphene.Boolean()
    task_id = graphene.Int()

    @staticmethod
    def mutate(root, info, id, input=None):
        status = False
        try:
            task = Task.objects.get(pk=id)
            task.delete()
            status = True
            return DeleteTaskMutation(status=status, task_id=id)
        except:
            pass
        return DeleteTaskMutation(status=status)


class CreateCodeRepositoryMutation(graphene.Mutation):
    class Arguments:
        input = CodeRepositoryInput(
            required=True,
            description="Fields required to create a task",
        )

    repository = graphene.Field(CodeRepositoryType)
    error = graphene.String()

    def mutate(cls, instance, input):
        try:
            product = Product.objects.get(slug=input.product_slug)
        except:
            raise Exception("product slug is required!")

        repos = CodeRepository.objects.filter(product=product,
                                              repository=input.repository)
        if len(repos) > 0:
            raise Exception("repository already eixts!")

        git_owner = input.repository.split("/")[3]
        repo_name = input.repository.split("/")[4]
        res = create_webhook(git_owner, repo_name, input.access_token)
        try:
            error = res["error"]
            return CreateCodeRepositoryMutation(repository=None, error=error["message"])
        except:
            pass
        try:
            error = res["error"]
            return CreateCodeRepositoryMutation(repository=None, error=error["message"])
        except:
            pass
        try:
            repository = CodeRepository(product=product,
                                        repository=input.repository,
                                        git_access_token=input.access_token,
                                        git_owner=git_owner)
            repository.save()
        except:
            raise Exception("Repository creation failed!")

        return CreateCodeRepositoryMutation(repository=repository)


class CreateAttachmentMutation(graphene.Mutation):
    class Arguments:
        input = AttachmentInput(
            required=True
        )

    attachment = graphene.Field(AttachmentType)
    error = graphene.String()

    @staticmethod
    def mutate(*args, **kwargs):
        attachment_input = kwargs.get('input')

        try:
            attachment_input.file_type = attachment_input.file_type if (
                    attachment_input.file_type == 'file' or attachment_input.file_type == 'link'
                    or attachment_input.file_type == 'video'
            ) else 'link'

            attachment = Attachment(
                name=attachment_input.name,
                path=attachment_input.path,
                file_type=attachment_input.file_type
            )
            attachment.save()

            return CreateAttachmentMutation(attachment=attachment)
        except Exception as e:
            return CreateAttachmentMutation(attachment=None, error=str(e))


class DeleteAttachmentMutation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        capability_id = graphene.Int(required=True)

    status = graphene.Boolean()
    attachment_id = graphene.Int()

    @staticmethod
    def mutate(root, info, id, capability_id, input=None):
        try:
            capability = Capability.objects.get(id=capability_id)
        except:
            raise Exception("Capability id is invalid!")

        try:
            attachment = Attachment.objects.get(pk=id)
            capability.attachment.remove(attachment)
            attachment.delete()
            return DeleteAttachmentMutation(status=True,
                                            attachment_id=id)
        except:
            pass
        return DeleteAttachmentMutation(status=False)


class ChangeTaskPriorityMutation(graphene.Mutation):
    class Arguments:
        task_id = graphene.Int(required=True)
        priority = graphene.String(required=True)

    status = graphene.Boolean()

    @staticmethod
    def mutate(self, _, **kwargs):
        try:
            priority = kwargs.get('priority')
            task_id = kwargs.get('task_id')

            if priority == 'High':
                priority = 0
            elif priority == 'Medium':
                priority = 1
            elif priority == 'Low':
                priority = 2
            else:
                raise Exception

            updated_task = Task.objects.get(pk=task_id)
            updated_task.priority = priority
            updated_task.save()
            return ChangeTaskPriorityMutation(status=True)
        except:
            return ChangeTaskPriorityMutation(status=False)


class LeaveTaskMutation(InfoStatusMutation, graphene.Mutation):
    class Arguments:
        task_id = graphene.Int(required=True)

    @staticmethod
    @is_current_person
    def mutate(current_person, info, *args, **kwargs):
        try:
            task_id = kwargs.get("task_id")
            task = Task.objects.get(id=task_id)
            task_claim = task.taskclaim_set.filter(person=current_person,
                                                   kind__in=[CLAIM_TYPE_DONE, CLAIM_TYPE_ACTIVE]).all()
            if len(task_claim) == 1:
                t_c = task_claim[0]
                t_c.kind = CLAIM_TYPE_FAILED
                t_c.save()
            elif len(task_claim) > 1:
                task_claim.update(kind=CLAIM_TYPE_FAILED)
            else:
                return LeaveTaskMutation(success=False, message="The task claim was not found")

            task.status = 2
            task.save()
            # cancel task claim requests
            for claim in task_claim:
                task_claim_request = task.taskclaimrequest_set.filter(person=claim.person, is_canceled=False).last()
                if task_claim_request:
                    task_claim_request.is_canceled = True
                    task_claim_request.save()

            return LeaveTaskMutation(success=True, message="The task was successfully unassigned")
        except Task.DoesNotExist:
            return LeaveTaskMutation(success=False, message="The task doesn't exist")
        except TaskClaim.DoesNotExist:
            return LeaveTaskMutation(success=False, message="The task claim doesn't exist")


class InReviewTaskMutation(InfoStatusMutation, graphene.Mutation):
    class Arguments:
        task_id = graphene.Int(required=True)

    @staticmethod
    @is_current_person
    def mutate(current_person, info, *args, task_id):
        try:
            task = Task.objects.get(id=task_id)

            task_claims = task.taskclaim_set.filter(person=current_person, kind=CLAIM_TYPE_ACTIVE).all()
            if not task_claims:
                return InReviewTaskMutation(success=False, message="The task claim was not found")

            task_claims.update(kind=CLAIM_TYPE_DONE)

            send_email(
                to_emails=Person.objects.get(pk=task.reviewer.id).email_address,
                subject='The task status was changed to "In review"',
                content=f"""
                    The task {task.title} status was changed to "In review".
                    You can see the task here: {task.get_task_link()}
                """
            )
            # call task save event to update tasklisting model
            task.save()

            return InReviewTaskMutation(success=True, message='The task status was changed to "In review"')
        except Task.DoesNotExist:
            return InReviewTaskMutation(success=False, message="The task doesn't exist")


class ClaimTaskMutation(InfoStatusMutation, graphene.Mutation):
    class Arguments:
        task_id = graphene.Int(required=True)

    success = graphene.Boolean()
    is_need_agreement = graphene.Boolean()
    message = graphene.String()
    claimed_task_link = graphene.String()
    claimed_task_name = graphene.String()

    @staticmethod
    def get_is_need_agreement(user_id, task_id):
        product = ProductTask.objects.get(task_id=task_id).product
        agreements = ContributorAgreement.objects.filter(product=product)

        if agreements.count() > 0:
            current_agreement_content = agreements.last().agreement_content

            if current_agreement_content not in ['', '<p><br></p>'] and \
                    not ContributorAgreementAcceptance.objects.filter(
                        person_id=user_id,
                        agreement=agreements.last()
                    ).exists():
                return True

        return False

    @staticmethod
    @is_current_person
    def mutate(current_person, info, *args, task_id):
        is_need_agreement = ClaimTaskMutation.get_is_need_agreement(current_person.id, task_id)

        if is_need_agreement:
            return ClaimTaskMutation(
                success=True,
                message='Please, agree Contribution License Agreement firstly',
                is_need_agreement=is_need_agreement
            )

        success = True
        message = "The task was successfully claimed"
        if not current_person:
            return ClaimTaskMutation(success=False,
                                     message="You cannot claim the task, please authenticate to the system")

        try:
            if get_right_task_status(task_id) == Task.TASK_STATUS_BLOCKED:
                return ClaimTaskMutation(
                    success=False,
                    is_need_agreement=False,
                    message="You cannot claim the task, when it's blocked"
                )

            task = Task.objects.get(pk=task_id)

            claimed_task = current_person.taskclaim_set.filter(kind=CLAIM_TYPE_ACTIVE).last()

            if claimed_task:
                claimed_task = claimed_task.task
                return ClaimTaskMutation(
                    success=False,
                    is_need_agreement=False,
                    message="""
                        You cannot claim the task, you have an active task.
                        Please complete another task to claim a new task.
                    """,
                    claimed_task_link=claimed_task.get_task_link(False),
                    claimed_task_name=claimed_task.title
                )

            # create a new task claim request with "Accepted" status
            try:
                TaskClaimRequest.objects.create(
                    kind=CLAIM_TYPE_ACTIVE,
                    task_id=task.id,
                    person_id=current_person.id
                )
            except Exception as e:
                print("TaskClaimRequest exception:", e, flush=True)
            # create a new task claim with "Active" status if task has "auto_approve_task_claims" value
            if task.auto_approve_task_claims:
                t_claim = TaskClaim(
                    kind=1,
                    task_id=task.id,
                    person_id=current_person.id
                )
                t_claim.save()

            task.status = 3
            task.save()

        except Task.DoesNotExist:
            success = False
            message = "The task doesn't exist"
        except Person.DoesNotExist:
            success = False
            message = "The person doesn't exist"

        return ClaimTaskMutation(success=success, message=message, is_need_agreement=is_need_agreement)


class RejectTaskMutation(InfoStatusMutation, graphene.Mutation):
    class Arguments:
        task_id = graphene.Int(required=True)

    @staticmethod
    @is_current_person
    def mutate(current_person, info, *args, **kwargs):
        try:
            task_id = kwargs.get("task_id")
            task = Task.objects.get(id=task_id)

            # check if user has permissions
            if not is_admin_or_manager(current_person, task.product.slug):
                return RejectTaskMutation(success=False, message="You don't have permissions")

            # set "Failed" status to task claims
            task_claim = task.taskclaim_set.filter(kind__in=[CLAIM_TYPE_DONE, CLAIM_TYPE_ACTIVE]).all()
            task_claim.update(kind=CLAIM_TYPE_FAILED)

            # cancel task claim requests
            for claim in task_claim:
                task_claim_request = task.taskclaimrequest_set.filter(person=claim.person, is_canceled=False).last()
                if task_claim_request:
                    task_claim_request.is_canceled = True
                    task_claim_request.save()

            # set task status "Available"
            task.status = Task.TASK_STATUS_AVAILABLE
            task.updated_by = current_person
            task.save()

            return RejectTaskMutation(success=True, message="The work has been rejected")
        except Task.DoesNotExist:
            return RejectTaskMutation(success=False, message="The task doesn't exist")


class ApproveTaskMutation(InfoStatusMutation, graphene.Mutation):
    class Arguments:
        task_id = graphene.Int(required=True)

    @staticmethod
    @is_current_person
    def mutate(current_person, info, *args, **kwargs):
        try:
            task_id = kwargs.get("task_id")
            task = Task.objects.get(id=task_id)

            # check if user has permissions
            if not is_admin_or_manager(current_person, task.product.slug):
                return ApproveTaskMutation(success=False, message="You don't have permissions")

            # set "Done" status to task claims
            task_claim = task.taskclaim_set.filter(kind__in=[CLAIM_TYPE_DONE, CLAIM_TYPE_ACTIVE]).all()
            task_claim.update(kind=CLAIM_TYPE_DONE)

            # approve task claim requests
            for claim in task_claim:
                task_claim_request = task.taskclaimrequest_set.filter(person=claim.person, is_canceled=False).last()
                if task_claim_request:
                    task_claim_request.kind = 1
                    task_claim_request.save()

            # set task status "Done"
            task.status = Task.TASK_STATUS_DONE
            task.updated_by = current_person
            task.save()

            return ApproveTaskMutation(success=True, message="The work has been approved")
        except Task.DoesNotExist:
            return ApproveTaskMutation(success=False, message="The task doesn't exist")


class WorkMutations(graphene.ObjectType):
    create_product = CreateProductMutation.Field()
    update_product = UpdateProductMutation.Field()
    delete_product = DeleteProductMutation.Field()
    update_capability_tree = UpdateCapabilityTreeMutation.Field()
    create_capability = CreateCapabilityMutation.Field()
    update_capability = UpdateCapabilityMutation.Field()
    delete_capability = DeleteCapabilityMutation.Field()
    create_initiative = CreateInitiativeMutation.Field()
    update_initiative = UpdateInitiativeMutation.Field()
    delete_initiative = DeleteInitiativeMutation.Field()
    create_task = CreateTaskMutation.Field()
    update_task = UpdateTaskMutation.Field()
    delete_task = DeleteTaskMutation.Field()
    create_code_repository = CreateCodeRepositoryMutation.Field()
    create_attachment = CreateAttachmentMutation.Field()
    delete_attachment = DeleteAttachmentMutation.Field()
    change_task_priority = ChangeTaskPriorityMutation.Field()
    leave_task = LeaveTaskMutation.Field()
    claim_task = ClaimTaskMutation.Field()
    in_review_task = InReviewTaskMutation.Field()
    approve_task = ApproveTaskMutation.Field()
    reject_task = RejectTaskMutation.Field()
