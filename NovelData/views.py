from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from selenium import webdriver
from bs4 import BeautifulSoup
from .models import Novel, Chapter
import time
import re
from transformers import pipeline

class NovelScrapingAPIView(APIView):
    def get(self, request):
        try:
            # Título, autor y descripción de la novela (ingresados manualmente)
            novel_title = "A Dish Best Served Cold"
            novel_description = "Descripción de la novela"
            novel_author = "Autor de la novela"
      

            options = webdriver.ChromeOptions()
            #options.add_argument("--headless")
            options.add_argument("--lang=es")
            prefs = {
                "translate_whitelists": {"en":"es"},  
                "translate":{"enabled":"true"}
                    }
            options.add_experimental_option("prefs", prefs)
            driver = webdriver.Chrome(options=options)
            driver.get("https://www.google.com")
            input("Configura el navegador para traducir de inglés a español y presiona Enter para continuar...")
            messages = []

            for chapter_number in range(300,450):  # Recorrer los capítulos del 35 al 300
                url = f"https://smnovels.com/novel/a-dish-best-served-cold-novel/chapter-{chapter_number}/"
                driver.get(url)
                time.sleep(5)  # Espera para que la página cargue completamente

                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                # Obtener título y contenido del capítulo
                chapter_title = soup.find('h1', class_='entry-title').text
                chapter_content_elem = soup.find('div', class_='entry-content')
                chapter_content = chapter_content_elem.text.strip() if chapter_content_elem else ""

                # Guardar el capítulo en la base de datos
                novel, _ = Novel.objects.get_or_create(
                    title=novel_title,
                    defaults={'description': novel_description, 'author': novel_author}
                )

                chapter, chapter_created = Chapter.objects.update_or_create(
                    novel=novel,
                    chapter_number=chapter_number,
                    defaults={'title': chapter_title, 'content': chapter_content ,'language': 'es'}
                )

                if chapter_created:
                    messages.append(f"Capítulo {chapter_number}: '{chapter_title}' creado.")
                else:
                    messages.append(f"Capítulo {chapter_number}: '{chapter_title}' actualizado.")

            driver.quit()
            return Response({"message": "Proceso completado", "details": messages})
        except Exception as e:
            return Response({"message": str(e)}, status=500)


