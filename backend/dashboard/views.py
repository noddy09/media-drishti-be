from django.db import models
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.clipping.models import Clip
from backend.downloads.models import Download
from backend.tagging.models import ClipTag, Tag
from backend.uploads.models import Upload
from backend.users.roles import is_staff_or_admin
from backend.auditlog.models import AuditLog

from .models import DashboardStat
from .serializers import DashboardStatSerializer, RecentActivitySerializer


class DashboardStatViewSet(viewsets.ModelViewSet):
    queryset = DashboardStat.objects.all()
    serializer_class = DashboardStatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user

        if is_staff_or_admin(user):
            upload_qs = Upload.objects.all()
            clip_qs = Clip.objects.all()
            download_qs = Download.objects.all()
            tag_qs = Tag.objects.all()
            clip_tag_qs = ClipTag.objects.all()
        else:
            tag_ids = list(user.client_tags.values_list('tag_id', flat=True))
            upload_qs = Upload.objects.filter(clips__clip_tags__tag_id__in=tag_ids).distinct()
            clip_qs = Clip.objects.filter(clip_tags__tag_id__in=tag_ids).distinct()
            download_qs = Download.objects.filter(upload__clips__clip_tags__tag_id__in=tag_ids).distinct()
            tag_qs = Tag.objects.filter(id__in=tag_ids)
            clip_tag_qs = ClipTag.objects.filter(tag_id__in=tag_ids)

        top_tags_qs = (
            clip_tag_qs.values('tag__name')
            .annotate(clip_count=models.Count('clip_id', distinct=True))
            .order_by('-clip_count')[:5]
        )
        top_tags = [
            {'tag_name': row['tag__name'], 'clip_count': row['clip_count']}
            for row in top_tags_qs
        ]

        return Response({
            'total_uploads': upload_qs.count(),
            'total_clips': clip_qs.count(),
            'total_downloads': download_qs.count(),
            'active_tags': tag_qs.count(),
            'top_tags': top_tags,
        })


class RecentActivityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if is_staff_or_admin(user):
            queryset = AuditLog.objects.all()
        else:
            queryset = AuditLog.objects.filter(user=user)

        queryset = queryset.order_by('-timestamp')[:20]
        serializer = RecentActivitySerializer(queryset, many=True)
        return Response(serializer.data)
