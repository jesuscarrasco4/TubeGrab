import yt_dlp
import os
import re
import time
from tqdm import tqdm

def validar_url_youtube(url):
    """Valida si la URL es de YouTube"""
    patron_youtube = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'
    return bool(re.match(patron_youtube, url))

def normalizar_url(url):
    """Normaliza la URL de YouTube"""
    if 'youtu.be' in url:
        video_id = url.split('/')[-1]
        return f'https://www.youtube.com/watch?v={video_id}'
    return url

class ProgressHook:
    def __init__(self):
        self.pbar = None

    def __call__(self, d):
        if d['status'] == 'downloading':
            if self.pbar is None:
                total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                self.pbar = tqdm(total=total, unit='B', unit_scale=True, desc="Descargando")
            
            downloaded = d.get('downloaded_bytes', 0)
            self.pbar.update(downloaded - self.pbar.n)
            
        elif d['status'] == 'finished':
            if self.pbar:
                self.pbar.close()
                self.pbar = None
            print("\nDescarga completada, procesando video...")

def formatear_tamaño(tamaño_bytes):
    """Formatea el tamaño en bytes a una cadena legible"""
    if tamaño_bytes is None:
        return "N/A"
    for unidad in ['B', 'KB', 'MB', 'GB']:
        if tamaño_bytes < 1024:
            return f"{tamaño_bytes:.1f}{unidad}"
        tamaño_bytes /= 1024
    return f"{tamaño_bytes:.1f}TB"

def descargar_video(url, carpeta_destino="descargas", intentos_maximos=3):
    try:
        # Normalizar la URL
        url = normalizar_url(url)
        
        # Validar la URL
        if not validar_url_youtube(url):
            print("\nError: La URL proporcionada no es válida para YouTube")
            return

        # Crear la carpeta de destino si no existe
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)

        # Configurar opciones de yt-dlp
        ydl_opts = {
            'format': 'best[ext=mp4]/best',  # Simplificado para mejor compatibilidad
            'outtmpl': os.path.join(carpeta_destino, '%(title)s.%(ext)s'),
            'progress_hooks': [ProgressHook()],
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        for intento in range(intentos_maximos):
            try:
                print(f"\nIntento {intento + 1} de {intentos_maximos}")
                print("Conectando con YouTube...")
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Obtener información del video
                    info = ydl.extract_info(url, download=False)
                    print(f"\nTítulo: {info['title']}")
                    print(f"Duración: {info['duration']} segundos")
                    print(f"Vistas: {info.get('view_count', 'N/A'):,}")
                    
                    # Mostrar formatos disponibles
                    print("\nFormatos disponibles:")
                    formatos_mp4 = [f for f in info['formats'] if f.get('ext') == 'mp4' and f.get('format_note')]
                    for f in formatos_mp4:
                        tamaño = f.get('filesize', 0) or f.get('filesize_approx', 0)
                        print(f"• {f.get('format_note', 'N/A')} - {formatear_tamaño(tamaño)}")
                    
                    print("\nIniciando descarga...")
                    # Descargar el video
                    ydl.download([url])
                    
                    print(f"\n¡Descarga completada! El video se ha guardado en la carpeta '{carpeta_destino}'")
                    return  # Si llegamos aquí, la descarga fue exitosa
                
            except Exception as e:
                error_msg = str(e)
                print(f"\nError en intento {intento + 1}: {error_msg}")
                
                if "Requested format is not available" in error_msg:
                    print("Intentando con formato alternativo...")
                    ydl_opts['format'] = 'best'  # Intentar con el mejor formato disponible
                    continue
                
                if intento < intentos_maximos - 1:
                    print("Reintentando en 3 segundos...")
                    time.sleep(3)
                else:
                    print("\nSe agotaron los intentos de descarga.")
                    print("\nSugerencias:")
                    print("1. Verifica tu conexión a internet")
                    print("2. Asegúrate de que el video esté disponible en tu región")
                    print("3. Intenta con otro video")
                    print("4. Verifica que el video no esté restringido por edad")
                    print("5. Intenta usar una VPN si el video está restringido en tu región")
                    print("6. Verifica que el video no sea privado o esté eliminado")
        
    except Exception as e:
        print(f"\nError inesperado: {str(e)}")
        print("Por favor, intenta nuevamente o usa una URL diferente")

def main():
    print("=== Convertidor de YouTube a MP4 ===")
    print("Nota: Si encuentras errores, asegúrate de que la URL sea correcta y que tengas una buena conexión a internet")
    
    while True:
        url = input("\nIngresa la URL del video de YouTube (o 'salir' para terminar): ").strip()
        
        if url.lower() == 'salir':
            print("\n¡Gracias por usar el convertidor!")
            break
            
        if not url:
            print("Por favor, ingresa una URL válida.")
            continue
            
        descargar_video(url)

if __name__ == "__main__":
    main() 