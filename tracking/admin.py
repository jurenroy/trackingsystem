from django.contrib import admin
from .models import Document,Types,ActionTaken

# Register your models here.

admin.site.site_header = 'Document Tracking-(Admin Page)'

admin.site.register(Document)
#admin.site.register(Types)
#admin.site.register(ActionTaken)


