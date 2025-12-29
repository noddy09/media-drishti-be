from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Clip
from .serializers import ClipSerializer
from backend.auditlog.models import AuditLog
import fitz  # PyMuPDF
import io
from PIL import Image

# Create your views here.

class ClipViewSet(viewsets.ModelViewSet):
    queryset = Clip.objects.all()
    serializer_class = ClipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Expect 'upload' as the upload ID in the request
        clip = serializer.save(created_by=self.request.user)
        # No need for separate tag assignment here, handled in serializer
        AuditLog.objects.create(
            user=self.request.user,
            action='clip',
            description=f"Created clip for file '{clip.upload}'",
            tenant='default',
        )

    def perform_update(self, serializer):
        clip = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action='clip',
            description=f"Updated clip for file '{clip.upload}'",
            tenant='default',
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            user=self.request.user,
            action='clip',
            description=f"Deleted clip for file '{instance.upload}'",
            tenant='default',
        )
        instance.delete()

    @action(detail=False, methods=['post'])
    def export_clips(self, request):
        tag_ids = request.data.get('tag_ids', [])
        if tag_ids:
            clips = Clip.objects.filter(clip_tags__tag_id__in=tag_ids).distinct()
        else:
            clips = self.get_queryset()
        
        # Create a new PDF document
        pdf_doc = fitz.open()
        
        for clip in clips:
            file_path = clip.upload.file.path
            if clip.upload.file_type == 'pdf':
                # Open the original PDF
                doc = fitz.open(file_path)
                page = doc[0]  # Assume first page
                
                # Define the rectangle to crop (x, y, x+width, y+height)
                rect = fitz.Rect(clip.x, clip.y, clip.x + clip.width, clip.y + clip.height)
                
                # Get the pixmap of the cropped area
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=rect)  # Higher resolution
                
                # Convert pixmap to PIL Image
                img = Image.open(io.BytesIO(pix.tobytes()))
                
                doc.close()
            else:
                # For images, open with PIL and crop
                img = Image.open(file_path)
                img = img.crop((clip.x, clip.y, clip.x + clip.width, clip.y + clip.height))
            
            # Convert to bytes for inserting into PDF
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Insert the image as a new page in the output PDF
            pdf_doc.new_page()
            last_page = pdf_doc[-1]
            last_page.insert_image(rect=fitz.Rect(0, 0, clip.width, clip.height), stream=img_bytes.getvalue())
        
        # Save the PDF to bytes
        pdf_bytes = io.BytesIO()
        pdf_doc.save(pdf_bytes)
        pdf_doc.close()
        pdf_bytes.seek(0)
        
        # Create response
        response = HttpResponse(pdf_bytes.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="exported_clips.pdf"'
        
        AuditLog.objects.create(
            user=request.user,
            action='download',
            description="Exported clips to PDF",
            tenant='default',
        )
        return response
