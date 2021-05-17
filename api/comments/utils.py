import re
from backend.utils import send_email
from talent.models import Person


def create_comment(current_person, comment_input, commented_object, comment_object):
    try:
        if comment_input.parent_id is None:
            parent_id = commented_object.objects.get(pk=comment_input.commented_object_id).comments_start_id

            if not parent_id:
                new_root = comment_object.add_root(text='root')
                updated_object = commented_object.objects.get(pk=comment_input.commented_object_id)
                updated_object.comments_start_id = new_root.id
                updated_object.save()

                parent_id = updated_object.comments_start_id

            parent_node = comment_object.objects.get(pk=parent_id)
        else:
            parent_node = comment_object.objects.get(pk=comment_input.parent_id)

        parent_node.add_child(text=comment_input.text,
                              person_id=current_person.id)

        mentioned_slugs = re.findall("@([\S]+)", comment_input.text)
        mentioned_emails = list(map(lambda slug: Person.objects.get(slug=slug).email_address, mentioned_slugs))

        send_email(
            to_emails=mentioned_emails,
            subject='You have been mentioned in the comment',
            content=comment_input.text
        )
        return True, "Comment was successfully created"
    except commented_object.DoesNotExist:
        return False, "Commented object doesn't exist"


def resolve_comments(commented_object_id, commented_object, comment_object):
    try:
        node_id = commented_object.objects.get(pk=commented_object_id).comments_start_id

        tree = comment_object.dump_bulk(parent=comment_object.objects.get(pk=node_id))
        tree = tree[0]['children']
        list(map(lambda comment: fetch_tree(comment), tree))

        return tree
    except:
        return None


def fetch_tree(comment):
    try:
        person = Person.objects.get(pk=comment['data']['person'])
        comment['data']['person'] = {'fullname': person.full_name, 'slug': person.username}

        if comment['children']:
            list(map(lambda children: fetch_tree(children), comment['children']))
    except:
        pass