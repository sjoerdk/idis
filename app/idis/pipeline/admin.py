from django.contrib import admin

# Register your models here.
from idis.pipeline.models import Stream

admin.site.register(Stream)
