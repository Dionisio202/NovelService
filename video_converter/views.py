import os
import time
from moviepy.editor import ImageClip, AudioFileClip
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

class ConvertirAudioVideo(APIView):
    def get(self, request, format=None):
        try:
            # Obtener la ruta del archivo de audio y la imagen desde los parámetros de la URL
            audio_filename = request.GET.get('audio_filename')
            image_filename = request.GET.get('image_filename')
            output_filename = request.GET.get('output_filename', 'output_video.mp4')

            if not audio_filename or not image_filename:
                return Response({"error": "Both audio_filename and image_filename are required."}, status=status.HTTP_400_BAD_REQUEST)

            # Construir las rutas completas de los archivos
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            audio_path = os.path.join(BASE_DIR, 'audios', audio_filename)
            image_path = os.path.join(BASE_DIR, 'images', image_filename)
            video_dir = os.path.join(BASE_DIR, 'videos')

            if not os.path.exists(audio_path):
                return Response({"error": "Audio file does not exist."}, status=status.HTTP_400_BAD_REQUEST)
            if not os.path.exists(image_path):
                return Response({"error": "Image file does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            # Crear la carpeta de videos si no existe
            if not os.path.exists(video_dir):
                os.makedirs(video_dir)

            # Ruta completa del archivo de video
            video_path = os.path.join(video_dir, output_filename)

            # Medir el tiempo de creación del video
            start_time = time.time()

            # Crear el video clip
            audio_clip = AudioFileClip(audio_path)
            image_clip = ImageClip(image_path).set_duration(audio_clip.duration)
            image_clip = image_clip.set_audio(audio_clip)

            # Escribir el archivo de video con fps especificado
            image_clip.write_videofile(video_path, codec='libx264', audio_codec='aac', fps=1)

            # Calcular el tiempo total
            elapsed_time = time.time() - start_time

            # Mensaje de éxito
            success_message = f"Video '{output_filename}' creado con éxito en {elapsed_time:.2f} segundos."
            return Response({"message": success_message}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Failed to create video: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
