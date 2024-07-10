import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse
from NovelData.models import Chapter, Novel

class ConvertirTextoPDF(APIView):
    def get(self, request, format=None):
        try:
            # Obtener el ID de la novela y los números de capítulos desde los parámetros de la URL
            novel_id = request.GET.get('novel_id', '')
            chapter_numbers = request.GET.get('chapter_numbers', '')

            if not novel_id or not chapter_numbers:
                return Response({"error": "No novel ID or chapter numbers provided"}, status=status.HTTP_400_BAD_REQUEST)

            # Convertir los números de capítulos a una lista de enteros
            chapter_numbers = [int(number) for number in chapter_numbers.split(',')]
            if len(chapter_numbers) != 2:
                return Response({"error": "Please provide exactly two chapter numbers"}, status=status.HTTP_400_BAD_REQUEST)

            start_chapter = min(chapter_numbers)
            end_chapter = max(chapter_numbers)

            # Obtener la novela
            novel = Novel.objects.get(id=novel_id)
            novel_title = novel.title

            # Obtener los capítulos correspondientes al rango de números de capítulos
            chapters = Chapter.objects.filter(novel=novel, chapter_number__gte=start_chapter, chapter_number__lte=end_chapter).order_by('chapter_number')
            if not chapters.exists():
                return Response({"error": "No chapters found for the given numbers"}, status=status.HTTP_404_NOT_FOUND)

            pdf_filename = f"{novel_title}_capítulos_{start_chapter}-{end_chapter}.pdf"

            # Crear la carpeta novelPdf en el directorio principal del proyecto Django
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            pdf_dir = os.path.join(BASE_DIR, 'novelPdf')
            if not os.path.exists(pdf_dir):
                os.makedirs(pdf_dir)
            
            # Ruta completa del archivo PDF
            pdf_filepath = os.path.join(pdf_dir, pdf_filename)

            # Crear el documento PDF
            pdf = SimpleDocTemplate(pdf_filepath, pagesize=letter)
            elements = []

            # Obtener estilos predeterminados y ajustar el tamaño de la fuente
            styles = getSampleStyleSheet()
            style_title = styles['Title']
            style_normal = ParagraphStyle(
                'BodyText',
                parent=styles['BodyText'],
                fontSize=12,  # Ajusta el tamaño de la fuente aquí
                leading=14
            )

            # Texto al inicio del PDF
            initial_text = "Sigamos disfrutando de esta novela "
            elements.append(Paragraph(initial_text, style_normal))
            elements.append(Spacer(1, 12))

            # Combinar los capítulos
            for chapter in chapters:
                elements.append(Paragraph(f"Capítulo {chapter.chapter_number}", style_title))
                elements.append(Spacer(1, 12))

                # Añadir el contenido del capítulo con el estilo de párrafo normal
                text = chapter.content.replace('\n', '<br />')
                elements.append(Paragraph(text, style_normal))
                elements.append(PageBreak())

            # Texto al final del PDF
            final_text = "Gracias por leer nuestra novela. Esperamos que hayas disfrutado de los capítulos. No dudes en compartir tus pensamientos y comentarios. ¡Hasta la próxima en club de novelas ligeras!"
            elements.append(Paragraph(final_text, style_normal))

            # Construir el PDF
            pdf.build(elements)

            # Crear la respuesta con el PDF
            with open(pdf_filepath, 'rb') as pdf_file:
                response = FileResponse(pdf_file, as_attachment=True, filename=pdf_filename)
            return response

        except Novel.DoesNotExist:
            return Response({"error": "Novel not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Failed to create PDF: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
