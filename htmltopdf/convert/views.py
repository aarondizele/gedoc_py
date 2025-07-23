import os
import uuid
from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import HtmlToPdfSerializer
from xhtml2pdf import pisa

class HtmlToPdfView(APIView):
    parser_classes = [FormParser, MultiPartParser]

    def post(self, request):
        serializer = HtmlToPdfSerializer(data=request.data)
        if serializer.is_valid():
            html_content = serializer.validated_data['docFormat']
            orientation = serializer.validated_data.get('orientation', 'portrait')

            # ✅ Générer le CSS @page avec orientation
            page_orientation_css = f"""
                <style>
                    @page {{
                        size: A4 {'landscape' if orientation == 'paysage' else 'portrait'};
                        margin: 1cm;
                    }}
                </style>
            """

            # ✅ Concaténer le CSS avec le HTML fourni
            full_html = page_orientation_css + html_content

            # ✅ Générer un nom de fichier unique
            filename = f"{uuid.uuid4().hex}.pdf"
            file_path = os.path.join(settings.MEDIA_ROOT, filename)
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            # ✅ Créer le fichier PDF
            with open(file_path, "wb") as f:
                pisa_status = pisa.CreatePDF(full_html, dest=f)

            if pisa_status.err:
                return Response({"error": "PDF generation failed."}, status=500)

            url_document = request.build_absolute_uri(settings.MEDIA_URL + filename)
            return Response({"url_document": url_document})

        return Response(serializer.errors, status=400)


class PdfDocumentView(APIView):
    def get(self, request, filename):
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        else:
            raise Http404("Document not found.")