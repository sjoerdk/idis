from django.contrib import admin

from idis.jobs.models import (
    Job,
    Profile,
    WadoServer,
    NetworkShare,
    WADOFile,
    FileOnDisk,
    FileBatch,
)

admin.site.register(Job)
admin.site.register(Profile)
admin.site.register(WadoServer)
admin.site.register(NetworkShare)
admin.site.register(WADOFile)
admin.site.register(FileOnDisk)
admin.site.register(FileBatch)
