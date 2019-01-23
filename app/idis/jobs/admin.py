from django.contrib import admin

from .models import Job, Profile, WadoSource, DiskSource, WADOFileInfo, DiskFileInfo, FileBatch

admin.site.register(Job)
admin.site.register(Profile)
admin.site.register(WadoSource)
admin.site.register(DiskSource)
admin.site.register(WADOFileInfo)
admin.site.register(DiskFileInfo)
admin.site.register(FileBatch)
