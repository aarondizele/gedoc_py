import uuid
from urllib.parse import quote
from io import BytesIO

from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from weasyprint import HTML, CSS
from django.core.files.storage import default_storage

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

            # Génération du PDF en mémoire
            pdf_file = BytesIO()
            HTML(string=html_content).write_pdf(
                target=pdf_file,
                stylesheets=[CSS(string=page_orientation_css)]
            )
            pdf_file.seek(0)

            # Nom du fichier PDF
            filename = f"{uuid.uuid4().hex}.pdf"

            # Enregistrement sur MinIO via django-minio-storage
            path = default_storage.save(filename, ContentFile(pdf_file.read()))

            # Construction de l'URL publique MinIO
            url_document = f"{settings.MINIO_STORAGE_MEDIA_URL}/{path}"

            return Response({"url_document": url_document})

        return Response(serializer.errors, status=400)


class PdfDocumentView(APIView):
    def get(self, request, filename):
        if not default_storage.exists(filename):
            raise Http404("Document not found.")

        file = default_storage.open(filename, 'rb')
        response = FileResponse(file, content_type='application/pdf')

        # Affichage inline dans iframe
        response['Content-Disposition'] = f'inline; filename="{quote(filename)}"'
        response.headers.pop('X-Frame-Options', None)

        return response
