import graphene_django_optimizer as gql_optimizer
from api.utils import get_current_person
from talent.models import Review
from work.models import TaskDepend, Task, Product


def set_depends(depends, task_id):
    if depends is not None:
        TaskDepend.objects.filter(task=Task.objects.get(pk=task_id)).delete()

        for depend in depends:
            new_task_depend = TaskDepend(
                task=Task.objects.get(pk=task_id), depends_by=Task.objects.get(pk=int(depend))
            )
            new_task_depend.save()


def get_right_task_status(task_id, task=None):
    depends_on_tasks = Task.objects.\
        filter(taskdepend__task=task_id).\
        exclude(status=Task.TASK_STATUS_DONE).exists()
    if depends_on_tasks:
        return Task.TASK_STATUS_BLOCKED

    if not task:
        task = Task.objects.get(pk=task_id)

    if task.status == Task.TASK_STATUS_BLOCKED:
        return Task.TASK_STATUS_AVAILABLE

    return task.status


def get_tasks(task_model, info, kwargs):
    input_data = kwargs.get('input')
    exclude_data = None

    current_person = get_current_person(info, kwargs)
    if not current_person:
        exclude_data = {"status__in": [0, 1]}

    return gql_optimizer.query(task_model.get_filtered_data(input_data, exclude_data=exclude_data), info)


def get_tasks_by_product(task_model, info, kwargs, only_count=False):
    try:
        review_id = kwargs.get('review_id')
        input_data = kwargs.get('input')
        exclude_data = None

        current_person = get_current_person(info, kwargs)
        if not current_person:
            exclude_data = {"status__in": [0, 1]}

        if review_id is not None:
            product_id = Review.objects.get(pk=review_id).product_id
        else:
            product_id = Product.objects.get(slug=kwargs.get('product_slug')).id

        product_param_name = "producttask__product" \
            if task_model.__name__ == Task.__name__ else "product_id"

        filter_data = {
            product_param_name: product_id,
            "blocked": False
        }

        task_queryset = task_model.get_filtered_data(input_data, filter_data, exclude_data)

        if only_count:
            return task_queryset.count()

        return gql_optimizer.query(task_queryset, info)
    except Product.DoesNotExist:
        return None

