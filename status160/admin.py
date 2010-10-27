from django.contrib import admin
from . import models

admin.site.register(models.Comments)
admin.site.register(models.WardenRelationship)
admin.site.register(models.Alert)


