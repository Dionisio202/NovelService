from PIL import Image

def compress_to_webp(input_path, output_path, quality=85):
    with Image.open(input_path) as img:
        # Convertir a WebP con compresión de calidad especificada
        img.save(output_path, 'WEBP', quality=quality)
        print(f"Imagen comprimida en WebP guardada en: {output_path}")

# Rutas de los archivos
input_image_path = r'D:\NovelApp\images\restart.png'

output_image_path = r'D:\NovelApp\images\restart2.webp'  # Cambia esto a donde quieres guardar la imagen WebP

# Comprimir la imagen a WebP
compress_to_webp(input_image_path, output_image_path)
