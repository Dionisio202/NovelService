from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup, NavigableString
from .models import Novel, Chapter
import time
import logging

logger = logging.getLogger(__name__)

class NovelScrapingAPIView(APIView):
    def get(self, request):
        try:
            novel_title = "Un nuevo comienzo"
            novel_description = "¡Sueño sin rastro, alma grabada! ¡De regreso a la época de la juventud, el alma enciende diferentes fuegos artificiales! Después de saber decir no, finalmente viví la vida que quería..."
            novel_author = "El hombre que lleva el pelo largo"

            options = webdriver.ChromeOptions()
            options.add_argument("--lang=es")
            prefs = {
                "translate_whitelists": {"en": "es"},
                "translate": {"enabled": "true"}
            }
            options.add_experimental_option("prefs", prefs)
            driver = webdriver.Chrome(options=options)
            driver.get("https://www.google.com")
            input("Configura el navegador para traducir de inglés a español y presiona Enter para continuar...")
            messages = []

            def smooth_scroll(driver, start, end, step):
                for i in range(start, end, step):
                    driver.execute_script(f"window.scrollTo(0, {i});")
                    time.sleep(0.1)  # Ajusta la velocidad del desplazamiento aquí

            for chapter_number in range(49, 250):
                url = f"https://www.wuxiabox.com/novel/6950660_{chapter_number}.html"
                driver.get(url)
                time.sleep(2)

                # Obtener la altura total de la página
                total_height = driver.execute_script("return document.body.scrollHeight")

                # Desplazarse lentamente hasta el final de la página
                smooth_scroll(driver, 0, total_height, 100)

                # Desplazarse lentamente de vuelta al inicio
                smooth_scroll(driver, total_height, 0, -100)

                # Recoger la información después de desplazarse hacia arriba
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                [div.decompose() for div in soup.find_all('div', {'align': 'center'})]

                chapter_header = soup.find('header', class_='chapter-header')
                chapter_title_elem = chapter_header.find('h2') if chapter_header else None
                chapter_content_elem = soup.find('div', class_='chapter-content')

                if chapter_title_elem and chapter_content_elem:
                    chapter_title = chapter_title_elem.text

                    # Filtrar para obtener solo los elementos 'font' sin elementos 'font' anidados
                    fonts = chapter_content_elem.find_all('font')
                    seen_texts = set()
                    chapter_content = []

                    for font in fonts:
                        if not font.find('font'):  # Asegúrate de que no tenga elementos 'font' anidados
                            text = font.get_text(separator=" ", strip=True)
                            if text not in seen_texts:
                                seen_texts.add(text)
                                chapter_content.append(text)

                    chapter_content = "\n".join(chapter_content)

                    novel, _ = Novel.objects.get_or_create(
                        title=novel_title,
                        defaults={'description': novel_description, 'author': novel_author}
                    )

                    chapter, chapter_created = Chapter.objects.update_or_create(
                        novel=novel,
                        chapter_number=chapter_number,
                        defaults={'title': chapter_title, 'content': chapter_content, 'language': 'es'}
                    )

                    if chapter_created:
                        messages.append(f"Capítulo {chapter_number}: '{chapter_title}' creado.")
                    else:
                        messages.append(f"Capítulo {chapter_number}: '{chapter_title}' actualizado.")
                else:
                    logger.error(f"Error al obtener los datos del capítulo {chapter_number}")
                    if not chapter_title_elem:
                        logger.error("No se encontró el título del capítulo.")
                    if not chapter_content_elem:
                        logger.error("No se encontró el contenido del capítulo.")

            driver.quit()
            return Response({"message": "Proceso completado", "details": messages})
        except Exception as e:
            logger.exception("Error durante la ejecución")
            return Response({"message": str(e)}, status=500)
