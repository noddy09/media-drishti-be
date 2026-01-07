import io
import fitz
from django.shortcuts import render
from django.http import FileResponse
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Download
from backend.clipping.models import Clip
from .serializers import DownloadSerializer
from backend.tagging.models import ClientTag


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

        zoom = 4.0  # Render clips at 4x scale for sharper output
        matrix = fitz.Matrix(zoom, zoom)

        for clip in clips:
            page_index = max(0, (clip.page_number or 1) - 1)
            page = doc[page_index]

            # Define the clip rectangle using original PDF coordinates
            rect = fitz.Rect(clip.x, clip.y, clip.x + clip.width, clip.y + clip.height)

            # Render the clipped region at higher resolution and embed as an image
            pix = page.get_pixmap(matrix=matrix, clip=rect, alpha=False)
            img_bytes = pix.tobytes("png")

            page_width = rect.width
            page_height = rect.height
            new_page = new_doc.new_page(width=page_width, height=page_height)
            new_page.insert_image(new_page.rect, stream=img_bytes)

        output = io.BytesIO()
        new_doc.save(output)
        new_doc.close()
        doc.close()
        output.seek(0)

        return FileResponse(output, as_attachment=True, filename='cropped_clips.pdf')
