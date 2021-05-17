import graphene


class LicenseInput(graphene.InputObjectType):
    product_slug = graphene.String(required=True)
    content = graphene.String(required=False)
