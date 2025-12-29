from django.contrib import admin

from .models import Upload

class UploadAdmin(admin.ModelAdmin):
    pass

admin.site.register(Upload, UploadAdmin)