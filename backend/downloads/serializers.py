from rest_framework import serializers
from .models import Download

class DownloadSerializer(serializers.ModelSerializer):
    upload_name = serializers.SerializerMethodField()

    class Meta:
        model = Download
        fields = ('id', 'upload', 'upload_name', 'downloaded_at', 'downloaded_by', 'tenant')
        read_only_fields = ('downloaded_at',)

    def get_upload_name(self, obj):
        return obj.upload.name or obj.upload.file.name
