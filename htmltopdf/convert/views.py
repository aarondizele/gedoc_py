import uuid
from urllib.parse import quote

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from weasyprint import HTML, CSS

from .serializers import HtmlToPdfSerializer


class HtmlToPdfView(APIView):
    parser_classes = [FormParser, MultiPartParser]

    def post(self, request):
        serializer = HtmlToPdfSerializer(data=request.data)
        if serializer.is_valid():
            html_content = serializer.validated_data['docFormat']
            orientation = serializer.validated_data.get('orientation', 'portrait')

            # CSS pour l'orientation du document
            page_orientation_css = f"""
                @page {{
                    size: A4 {'landscape' if orientation == 'paysage' else 'portrait'};
                    margin: 1cm;
                }}
            """

            # Génération du PDF (en mémoire)
            from io import BytesIO
            pdf_file = BytesIO()
            HTML(string=html_content).write_pdf(
                target=pdf_file,
                stylesheets=[CSS(string=page_orientation_css)]
            )
            pdf_file.seek(0)

            # Nom du fichier
            filename = f"{uuid.uuid4().hex}.pdf"

            # Sauvegarde dans le stockage S3 (MinIO)
            path = default_storage.save(filename, ContentFile(pdf_file.read()))

            # Construction de l'URL MinIO
            if hasattr(default_storage, 'url'):
                url_document = default_storage.url(path)
            else:
                # fallback
                url_document = request.build_absolute_uri(settings.MEDIA_URL + filename)

            return Response({"url_document": url_document})

        return Response(serializer.errors, status=400)


class PdfDocumentView(APIView):
    def get(self, request, filename):
        # Lire depuis MinIO
        if not default_storage.exists(filename):
            raise Http404("Document not found.")

        file = default_storage.open(filename, 'rb')
        response = FileResponse(file, content_type='application/pdf')

        response['Content-Disposition'] = f'inline; filename="{quote(filename)}"'
        response.headers.pop('X-Frame-Options', None)

        return response
