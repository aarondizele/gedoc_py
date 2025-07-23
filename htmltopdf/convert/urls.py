from django.urls import path
from .views import HtmlToPdfView, PdfDocumentView

urlpatterns = [
    path('generate/', HtmlToPdfView.as_view(), name='generate-pdf'),
    path('document/<str:filename>/', PdfDocumentView.as_view(), name='get-pdf'),
]
