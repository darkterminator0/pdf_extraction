from django.urls import path
from .views import pdf_single_page_extract
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('extract/single/', pdf_single_page_extract, name='pdf_single_page_extract'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
