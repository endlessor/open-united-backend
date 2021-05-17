from django.contrib import admin
from work.models import Product, Initiative, Task, Tag, \
    Attachment, CodeRepository


class InitiativeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'product')


class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'initiative')


admin.site.register(Product)
admin.site.register(Initiative, InitiativeAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Tag)
admin.site.register(Attachment)
admin.site.register(CodeRepository)
