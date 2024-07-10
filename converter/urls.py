from django.urls import path
from .views import ConvertirTextoPDF

urlpatterns = [
    path('convertir/pdf/', ConvertirTextoPDF.as_view(), name='convertir-texto-pdf'),
]
