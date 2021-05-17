from django.urls import path
from .views import get_attachment_image
from .views import get_product_image

urlpatterns = [
    path('attachments/<name>', get_attachment_image, name='attachment_images'),
    path('products/<name>', get_product_image, name='product_images')
]
