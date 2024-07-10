from django.urls import path
from .views import ConvertirAudioVideo

urlpatterns = [
    path('convertir/audio-video/', ConvertirAudioVideo.as_view(), name='convertir-audio-video'),
]
