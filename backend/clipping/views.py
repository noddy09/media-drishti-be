from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Clip
from .serializers import ClipSerializer
from backend.auditlog.models import AuditLog
from backend.tagging.models import ClientTag
from backend.manual_entries.models import ManualEntry
import fitz  # PyMuPDF
import io
from PIL import Image, ImageDraw, ImageFont

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
            manual_entries = ManualEntry.objects.filter(tags__id__in=tag_ids).distinct()
        else:
            clips = self.get_queryset()
            manual_entries = ManualEntry.objects.all()
        
        # For clients, filter clips to only those with tags assigned to them
        if not request.user.is_staff and not request.user.is_superuser:
            allowed_tag_ids = ClientTag.objects.filter(client=request.user).values_list('tag_id', flat=True)
            clips = clips.filter(clip_tags__tag_id__in=allowed_tag_ids).distinct()
            manual_entries = manual_entries.filter(tags__id__in=allowed_tag_ids).distinct()
        
        # Create a new PDF document with A4 pages
        pdf_doc = fitz.open()
        page_width = 595  # A4 width in points
        page_height = 842  # A4 height in points
        margin = 50
        content_width = page_width - 2 * margin
        y_position = margin
        current_page = None
        
        def add_new_page():
            nonlocal current_page, y_position
            current_page = pdf_doc.new_page(width=page_width, height=page_height)
            y_position = margin
            return current_page
        
        def check_space_and_add_page(required_height):
            nonlocal y_position, current_page
            if current_page is None or (y_position + required_height) > (page_height - margin):
                add_new_page()
        
        # Process clips
        for clip in clips:
            file_path = clip.upload.file.path
            if clip.upload.file_type == 'pdf':
                # Open the original PDF and select the correct page (1-based -> 0-based)
                doc = fitz.open(file_path)
                page_index = max(0, (clip.page_number or 1) - 1)
                page = doc[page_index]

                # Define the rectangle to crop (x, y, x+width, y+height)
                x1 = int(round(clip.x))
                y1 = int(round(clip.y))
                x2 = int(round(clip.x + clip.width))
                y2 = int(round(clip.y + clip.height))
                rect = fitz.Rect(x1, y1, x2, y2)

                # Get the pixmap of the cropped area at higher resolution (3x for better quality)
                pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=rect)

                # Convert pixmap to PIL Image
                img = Image.open(io.BytesIO(pix.tobytes()))

                doc.close()
            else:
                # For images, open with PIL and crop
                img = Image.open(file_path)
                x1 = int(round(clip.x))
                y1 = int(round(clip.y))
                x2 = int(round(clip.x + clip.width))
                y2 = int(round(clip.y + clip.height))
                img = img.crop((x1, y1, x2, y2))
            
            # Scale image to fit within content width while maintaining aspect ratio
            img_width, img_height = img.size
            scale = min(content_width / img_width, 500 / img_height, 1.0)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Add border with padding to the image
            border_width = 2
            padding = 5
            bordered_width = new_width + 2 * (padding + border_width)
            bordered_height = new_height + 2 * (padding + border_width)
            
            # Create new image with border and padding
            bordered_img = Image.new('RGB', (bordered_width, bordered_height), 'white')
            draw = ImageDraw.Draw(bordered_img)
            
            # Draw border rectangle
            draw.rectangle(
                [(0, 0), (bordered_width - 1, bordered_height - 1)],
                outline='black',
                width=border_width
            )
            
            # Paste original image with padding
            bordered_img.paste(img, (padding + border_width, padding + border_width))
            
            # Calculate total height needed (label + bordered image + separator + spacing)
            label_height = 20
            separator_spacing = 15
            spacing = 10
            total_height = label_height + bordered_height + separator_spacing + spacing
            
            # Check if we need a new page
            check_space_and_add_page(total_height)
            
            # Add label centered
            upload_name = clip.upload.name or "Unknown"
            label = f"{upload_name} - Page {clip.page_number}"
            # Calculate text width to center it manually
            text_width = len(label) * 5  # Approximate width
            x_centered_text = (page_width - text_width) / 2
            current_page.insert_text(
                (x_centered_text, y_position + 12),
                label,
                fontsize=10,
                fontname="helv",
                color=(0, 0, 0)
            )
            y_position += label_height
            
            # Convert bordered image to bytes and insert centered with high DPI
            img_bytes = io.BytesIO()
            bordered_img.save(img_bytes, format='PNG', dpi=(300, 300))
            img_bytes.seek(0)
            
            x_centered = (page_width - bordered_width) / 2
            img_rect = fitz.Rect(x_centered, y_position, x_centered + bordered_width, y_position + bordered_height)
            current_page.insert_image(rect=img_rect, stream=img_bytes.getvalue())
            y_position += bordered_height + separator_spacing
            
            # Draw horizontal separator line
            line_y = y_position
            current_page.draw_line(
                (margin, line_y),
                (page_width - margin, line_y),
                color=(0.7, 0.7, 0.7),
                width=1
            )
            y_position += spacing
        
        # Process manual entries
        for entry in manual_entries:
            # Create a formatted text block with title and content
            title_height = 25
            content_spacing = 15
            line_height = 14
            
            # Estimate content height (rough calculation)
            content_lines = len(entry.content) // 70 + 1  # Approximate characters per line
            content_height = content_lines * line_height
            total_height = title_height + content_spacing + content_height + 40  # 40 for spacing
            
            # Check if we need a new page
            check_space_and_add_page(total_height)
            
            # Add title centered and bold
            title_width = len(entry.title) * 7  # Approximate width for size 14
            x_centered_title = (page_width - title_width) / 2
            current_page.insert_text(
                (x_centered_title, y_position + 15),
                entry.title,
                fontsize=14,
                fontname="hebo",  # Helvetica Bold
                color=(0, 0, 0)
            )
            y_position += title_height + content_spacing
            
            # Add content as text block (left-aligned but within margins)
            text_rect = fitz.Rect(margin, y_position, page_width - margin, page_height - margin)
            rc = current_page.insert_textbox(
                text_rect,
                entry.content,
                fontsize=11,
                fontname="helv",
                color=(0, 0, 0),
                align=fitz.TEXT_ALIGN_LEFT
            )
            
            # Update y_position based on text height
            if rc >= 0:  # rc is the unused text or -1 on error
                y_position += content_height + 15
            else:
                y_position += 100  # Fallback
            
            # Draw horizontal separator line after manual entry
            line_y = y_position
            current_page.draw_line(
                (margin, line_y),
                (page_width - margin, line_y),
                color=(0.7, 0.7, 0.7),
                width=1
            )
            y_position += 25
        
        # Save the PDF to bytes
        pdf_bytes = io.BytesIO()
        pdf_doc.save(pdf_bytes)
        pdf_doc.close()
        pdf_bytes.seek(0)
        
        # Create response
        response = HttpResponse(pdf_bytes.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="exported_content.pdf"'
        
        AuditLog.objects.create(
            user=request.user,
            action='download',
            description="Exported clips and manual entries to PDF",
            tenant='default',
        )
        return response
