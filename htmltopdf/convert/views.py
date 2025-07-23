import os
import uuid
from urllib.parse import quote  # pour sécuriser le nom de fichier
from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import HtmlToPdfSerializer
from weasyprint import HTML, CSS

class HtmlToPdfView(APIView):
    parser_classes = [FormParser, MultiPartParser]

    def post(self, request):
        serializer = HtmlToPdfSerializer(data=request.data)
        if serializer.is_valid():
            html_content = serializer.validated_data['docFormat']
            orientation = serializer.validated_data.get('orientation', 'portrait')

            # Générer l’orientation via CSS @page
            page_orientation_css = f"""
                @page {{
                    size: A4 {'landscape' if orientation == 'paysage' else 'portrait'};
                    margin: 1cm;
                }}
            """

            # Nom et chemin du fichier PDF
            filename = f"{uuid.uuid4().hex}.pdf"
            file_path = os.path.join(settings.MEDIA_ROOT, filename)
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            # Générer le PDF avec WeasyPrint
            HTML(string=html_content).write_pdf(
                target=file_path,
                stylesheets=[CSS(string=page_orientation_css)]
            )

            # URL de retour
            url_document = request.build_absolute_uri(settings.MEDIA_URL + filename)
            return Response({"url_document": url_document})

        return Response(serializer.errors, status=400)

class PdfDocumentView(APIView):
    def get(self, request, filename):
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')

            # Affichage inline dans un navigateur (ex: iframe)
            response['Content-Disposition'] = f'inline; filename="{quote(filename)}"'

            # Retirer le header X-Frame-Options si défini automatiquement
            response.headers.pop('X-Frame-Options', None)

            return response
        else:
            raise Http404("Document not found.")
