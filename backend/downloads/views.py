from django.shortcuts import render
from rest_framework import viewsets, permissions
from django.http import FileResponse
from rest_framework.exceptions import PermissionDenied
import fitz
import io

from backend.clipping.models import Clip
from backend.tagging.models import ClientTag
from .models import Download
from .serializers import DownloadSerializer

# Create your views here.

class DownloadViewSet(viewsets.ModelViewSet):
    queryset = Download.objects.all()
    serializer_class = DownloadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        download = self.get_object()
        upload = download.upload
        
        # For clients, ensure the upload contains at least one clip tagged with a tag assigned to them
        if not request.user.is_staff and not request.user.is_superuser:
            allowed_tag_ids = set(ClientTag.objects.filter(client=request.user).values_list('tag_id', flat=True))
            clip_tag_ids = set(
                Clip.objects.filter(upload=upload).values_list('clip_tags__tag_id', flat=True).distinct()
            )
            if not (allowed_tag_ids and (clip_tag_ids & allowed_tag_ids)):
                raise PermissionDenied("You do not have access to download this file.")
        
        clips = Clip.objects.filter(upload=upload)
        
        pdf_path = upload.file.path
        doc = fitz.open(pdf_path)
        new_doc = fitz.open()
        
        for clip in clips:
            page = doc[0]  # Assuming single page PDF
            rect = fitz.Rect(clip.x, clip.y, clip.x + clip.width, clip.y + clip.height)
            new_page = new_doc.new_page()
            new_page.show_pdf_page(new_page.rect, doc, 0, clip=rect)
        
        output = io.BytesIO()
        new_doc.save(output)
        new_doc.close()
        doc.close()
        output.seek(0)
        
        return FileResponse(output, as_attachment=True, filename='cropped_clips.pdf')
