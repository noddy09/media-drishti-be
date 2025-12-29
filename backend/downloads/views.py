from django.shortcuts import render
from rest_framework import viewsets, permissions
from django.http import FileResponse
import fitz
import io

from backend.clipping.models import Clip
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
